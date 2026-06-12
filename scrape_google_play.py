#!/usr/bin/env python3
"""Scrape a Google Play app detail page and emit 3 output files.

Outputs (next to this script):
  - google_play_report.md    (Markdown report)
  - google_play_data.json    (Structured JSON)
  - raw_text.txt             (Full body innerText, for debugging)

Missing fields are written as the literal string "未找到" (never raise).
Image URLs are deduplicated and the icon is excluded from screenshots.
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------- Config ----------

APP_URL = (
    "https://play.google.com/store/apps/details?id="
    "com.allstarunion.watch&hl=en&gl=US"
)
OUT_DIR = Path(__file__).resolve().parent
REPORT_PATH = OUT_DIR / "google_play_report.md"
JSON_PATH = OUT_DIR / "google_play_data.json"
RAW_PATH = OUT_DIR / "raw_text.txt"

NOT_FOUND = "未找到"
TIMEOUT_MS = 30_000
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
# Use the system Google Chrome — Playwright's bundled Chromium is not
# yet available for this OS (Ubuntu 26.04).
CHROME_PATH = "/usr/bin/google-chrome"


# ---------- Helpers ----------

def dedupe(items):
    seen, out = set(), []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def safe_text(page, selectors):
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                txt = (el.inner_text() or "").strip()
                if txt:
                    return txt
        except Exception:
            continue
    return NOT_FOUND


def safe_attr(page, selectors, attr):
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                val = el.get_attribute(attr)
                if val:
                    return val.strip()
        except Exception:
            continue
    return NOT_FOUND


# ---------- Extraction ----------

def extract_metadata_pairs(page):
    """Locate 'Downloads' / 'Updated on' label-value pairs in the page."""
    return page.evaluate(
        """() => {
            const find = (label) => {
                const all = document.querySelectorAll('div, span');
                for (const el of all) {
                    if (el.children.length > 0) continue;
                    const t = (el.textContent || '').trim();
                    if (t === label) {
                        const parent = el.parentElement;
                        if (parent) {
                            const texts = Array.from(parent.children)
                                .map(c => (c.textContent || '').trim())
                                .filter(x => x && x !== label);
                            if (texts.length) return texts[0];
                        }
                    }
                }
                return null;
            };
            return {
                installs: find('Downloads'),
                updated: find('Updated on'),
            };
        }"""
    )


def extract_icon_url(page):
    # 1) og:image meta — usually a clean icon link
    try:
        meta_icon = page.evaluate(
            """() => {
                const m = document.querySelector('meta[property="og:image"]');
                return m ? m.content : null;
            }"""
        )
        if meta_icon and "googleusercontent" in meta_icon:
            return meta_icon
    except Exception:
        pass
    # 2) First reasonably-sized image
    for img in page.query_selector_all("img"):
        try:
            src = img.get_attribute("src") or ""
            if "googleusercontent" not in src:
                continue
            try:
                w = int(img.get_attribute("width") or "0")
                if 30 <= w <= 300:
                    return src
            except ValueError:
                continue
        except Exception:
            continue
    # 3) First googleusercontent image, last resort
    for img in page.query_selector_all("img"):
        try:
            src = img.get_attribute("src") or ""
            if "googleusercontent" in src:
                return src
        except Exception:
            continue
    return NOT_FOUND


def extract_screenshot_urls(page, icon_url):
    """Collect screenshot URLs, drop icon and reviewer avatars.

    Google Play reuses lh3.googleusercontent.com for icons, screenshots,
    and reviewer avatars. Heuristics used here:
      - Drop `=s<size>-` tiny thumbnails (reviewer avatars, badges)
      - Drop `a-/ALV-` reviewer avatar paths
      - Keep `=w<size>-h<size>-` sized images (true screenshots)
      - Always drop the icon URL (compare on base URL, ignoring size suffix)
    """
    def base_url(u):
        # Strip trailing size hint like "=w240-h480-rw" or "=s32-rw"
        return u.split("=", 1)[0]

    icon_base = base_url(icon_url) if icon_url != NOT_FOUND else None
    shots = []
    for img in page.query_selector_all("img"):
        try:
            src = img.get_attribute("src") or ""
            if "googleusercontent" not in src:
                continue
            # Drop reviewer avatar paths
            if "/a-/ALV-" in src or "/a/ACg8oc" in src:
                continue
            # Drop tiny size hints — avatars / icons / badges
            if "=s" in src.split("/")[-1] and "=w" not in src:
                continue
            # If the URL has a `=w<size>` hint, it must also carry `-h<size>`.
            # `=w48` without `-h` is a thumbnail/banner, not a screenshot.
            if "=w" in src and "-h" not in src:
                continue
            # If a =w<W>-h<H> hint is present, enforce min dimensions so
            # that thin promotional banners (e.g. 48x16) are dropped.
            m = re.search(r"=w(\d+)-h(\d+)", src)
            if m:
                w, h = int(m.group(1)), int(m.group(2))
                if w < 200 or h < 200:
                    continue
            # Drop if it equals the icon (base URL match)
            if icon_base and base_url(src) == icon_base:
                continue
            shots.append(src)
        except Exception:
            continue
    return dedupe(shots)


def extract_whats_new(page):
    val = safe_text(page, ['[data-g-id="whats-new"]'])
    if val != NOT_FOUND:
        return val
    try:
        res = page.evaluate(
            """() => {
                const heads = document.querySelectorAll('h1, h2, h3, h4, h5, span, div');
                for (const h of heads) {
                    const t = (h.textContent || '').trim().toLowerCase();
                    if (t === "what's new" || t === 'whats new') {
                        let sib = h.nextElementSibling;
                        if (sib && (sib.textContent || '').trim()) {
                            return sib.textContent.trim();
                        }
                        const p = h.parentElement;
                        if (p && p.nextElementSibling) {
                            return (p.nextElementSibling.textContent || '').trim();
                        }
                    }
                }
                return null;
            }"""
        )
        if res:
            return res
    except Exception:
        pass
    return NOT_FOUND


def extract_data(page):
    data = {
        "url": page.url,
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
        "app_name": NOT_FOUND,
        "developer": NOT_FOUND,
        "rating": NOT_FOUND,
        "review_count": NOT_FOUND,
        "installs": NOT_FOUND,
        "last_updated": NOT_FOUND,
        "category": NOT_FOUND,
        "description": NOT_FOUND,
        "whats_new": NOT_FOUND,
        "support_email": NOT_FOUND,
        "icon_url": NOT_FOUND,
        "screenshot_urls": [],
    }

    data["app_name"] = safe_text(page, [
        'h1[itemprop="name"]',
        'h1 span',
        'header h1',
    ])

    data["developer"] = safe_text(page, [
        'a[href*="/store/apps/dev"]',
        'div.Vbfug a',
        'a[aria-label*="developer" i]',
    ])

    rating = safe_attr(page, [
        'div[aria-label*="Rated"][role="img"]',
        'div.TT9eCd[role="img"]',
    ], "aria-label")
    if rating == NOT_FOUND:
        rating = safe_text(page, ['div.TT9eCd', 'span.YdKkSc'])
    data["rating"] = rating

    data["review_count"] = safe_text(page, [
        'div.g1rdde',
        'span[aria-label*="reviews" i]',
    ])

    try:
        meta = extract_metadata_pairs(page) or {}
        if meta.get("installs"):
            data["installs"] = meta["installs"]
        if meta.get("updated"):
            data["last_updated"] = meta["updated"]
    except Exception:
        pass

    data["category"] = safe_text(page, [
        'a[href*="/store/apps/category/"]',
        'a[itemprop="genre"]',
    ])

    data["description"] = safe_text(page, [
        '[data-g-id="description"]',
        'div[itemprop="description"]',
        'div.bARER',
    ])

    data["whats_new"] = extract_whats_new(page)

    email = safe_attr(page, ['a[href^="mailto:"]'], "href")
    if email != NOT_FOUND:
        email = email.replace("mailto:", "").strip()
    data["support_email"] = email

    data["icon_url"] = extract_icon_url(page)
    data["screenshot_urls"] = extract_screenshot_urls(page, data["icon_url"])

    return data


# ---------- Renderer ----------

def render_markdown(data):
    L = []
    L.append(f"# Google Play 应用报告 — {data['app_name']}")
    L.append("")
    L.append(f"- **来源**：{data['url']}")
    L.append(f"- **抓取时间**：{data['scraped_at']}")
    L.append("")
    L.append("## 元数据")
    L.append("")
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    for k, v in [
        ("应用名", data["app_name"]),
        ("开发者", data["developer"]),
        ("评分", data["rating"]),
        ("评论数", data["review_count"]),
        ("下载量", data["installs"]),
        ("更新时间", data["last_updated"]),
        ("分类", data["category"]),
        ("支持邮箱", data["support_email"]),
    ]:
        L.append(f"| {k} | {v} |")
    L.append("")
    L.append("## 应用简介")
    L.append("")
    L.append(data["description"] or NOT_FOUND)
    L.append("")
    L.append("## 更新说明（What's New）")
    L.append("")
    L.append(data["whats_new"] or NOT_FOUND)
    L.append("")
    L.append("## 图标")
    L.append("")
    L.append(
        f"![]({data['icon_url']})" if data["icon_url"] != NOT_FOUND else NOT_FOUND
    )
    L.append("")
    L.append("## 截图")
    L.append("")
    if data["screenshot_urls"]:
        for u in data["screenshot_urls"]:
            L.append(f"- {u}")
    else:
        L.append(NOT_FOUND)
    L.append("")
    return "\n".join(L)


# ---------- Main ----------

def load_page(page, url):
    for attempt in range(3):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
            try:
                page.wait_for_load_state("networkidle", timeout=15_000)
            except PWTimeout:
                pass
            return True
        except Exception as e:
            print(f"[!] goto attempt {attempt+1} failed: {e}", file=sys.stderr)
            if attempt < 2:
                time.sleep(2)
    return False


def main():
    print(f"[+] Target : {APP_URL}", file=sys.stderr)
    print(f"[+] Output : {OUT_DIR}", file=sys.stderr)

    raw_text = ""
    data = None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 900},
            )
            page = context.new_page()
            page.set_default_timeout(TIMEOUT_MS)
            if load_page(page, APP_URL):
                try:
                    raw_text = page.evaluate("() => document.body.innerText") or ""
                except Exception:
                    raw_text = ""
                data = extract_data(page)
            else:
                print("[!] Could not load page after retries.", file=sys.stderr)
        finally:
            browser.close()

    if data is None:
        data = {
            "url": APP_URL,
            "scraped_at": datetime.now().isoformat(timespec="seconds"),
        }
        for k in [
            "app_name", "developer", "rating", "review_count", "installs",
            "last_updated", "category", "description", "whats_new",
            "support_email", "icon_url",
        ]:
            data[k] = NOT_FOUND
        data["screenshot_urls"] = []

    RAW_PATH.write_text(raw_text, encoding="utf-8")
    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    REPORT_PATH.write_text(render_markdown(data), encoding="utf-8")

    print(f"[+] Saved: {REPORT_PATH}", file=sys.stderr)
    print(f"[+] Saved: {JSON_PATH}", file=sys.stderr)
    print(f"[+] Saved: {RAW_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
