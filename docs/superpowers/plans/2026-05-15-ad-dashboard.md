# Ad Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file static ad campaign daily report dashboard with dark theme, metric cards, channel table, optimization suggestions, and responsive mobile layout.

**Architecture:** Single `index.html` with embedded `<style>` and `<script>`. No external dependencies. Data is hardcoded as a JS object. Responsive via CSS Grid + media queries. Collapsible sections use vanilla JS class toggle.

**Tech Stack:** HTML5, CSS3 (Grid, Flexbox, Custom Properties, Media Queries), Vanilla JavaScript (ES6+)

---

### Task 1: HTML Structure

**Files:**
- Create: `index.html`

- [ ] **Step 1: Write the full HTML skeleton**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>广告投放日报</title>
</head>
<body>
  <header class="header">
    <h1>广告投放日报</h1>
    <span class="date"></span>
  </header>

  <main class="container">
    <!-- 1. 核心指标卡片网格 -->
    <section class="metrics-section">
      <h2>核心指标</h2>
      <div class="metrics-grid" id="metricsGrid">
        <!-- 8 cards: 总消耗, 曝光量, 点击量, CTR, CPM, CPC, 转化数, ROI -->
      </div>
    </section>

    <!-- 2. 渠道数据表（折叠面板） -->
    <section class="channel-section collapsible">
      <button class="collapsible-header" aria-expanded="true">
        <h2>渠道数据</h2>
        <span class="collapse-icon"></span>
      </button>
      <div class="collapsible-body">
        <table class="channel-table">
          <thead>
            <tr>
              <th>渠道</th><th>消耗</th><th>曝光</th><th>点击</th><th>CTR</th><th>CPM</th><th>CPC</th><th>转化</th><th>ROI</th>
            </tr>
          </thead>
          <tbody id="channelBody"></tbody>
        </table>
      </div>
    </section>

    <!-- 3. 优化建议（折叠面板） -->
    <section class="suggestions-section collapsible">
      <button class="collapsible-header" aria-expanded="true">
        <h2>优化建议</h2>
        <span class="collapse-icon"></span>
      </button>
      <div class="collapsible-body">
        <ul class="suggestions-list" id="suggestionsList"></ul>
      </div>
    </section>
  </main>

  <footer class="footer">
    <p>数据更新时间：<span id="updateTime"></span></p>
  </footer>
</body>
</html>
```

### Task 2: CSS Styling — Dark Theme & Metrics Cards

**Files:**
- Modify: `index.html` — add `<style>` block to `<head>`

- [ ] **Step 1: Add CSS custom properties and base reset**

```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1e293b;
  --border: #334155;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --accent-blue: #38bdf8;
  --accent-green: #4ade80;
  --accent-orange: #fb923c;
  --accent-red: #f87171;
  --accent-purple: #c084fc;
  --card-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
  --radius: 8px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
}
```

- [ ] **Step 2: Add header styles**

```css
.header {
  padding: 24px 32px;
  border-bottom: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: baseline;
}
.header h1 { font-size: 24px; font-weight: 700; }
.date { color: var(--text-secondary); font-size: 14px; }
```

- [ ] **Step 3: Add metrics grid and card styles**

```css
.container { max-width: 1200px; margin: 0 auto; padding: 24px 32px; }

.metrics-section h2, .channel-section h2, .suggestions-section h2 {
  font-size: 18px; margin-bottom: 16px; color: var(--text-secondary);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--card-shadow);
  transition: transform 0.15s, box-shadow 0.15s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.4); }

.metric-card .label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.metric-card .value { font-size: 28px; font-weight: 700; }
.metric-card .change { font-size: 12px; margin-top: 8px; }
.metric-card .change.up { color: var(--accent-green); }
.metric-card .change.down { color: var(--accent-red); }
```

- [ ] **Step 4: Add color accents per card type (nth-child selectors)**

Color mapping:
- 总消耗: #38bdf8 (blue)
- 曝光量: #c084fc (purple)
- 点击量: #fb923c (orange)
- CTR: #4ade80 (green)
- CPM: #fbbf24 (yellow)
- CPC: #f472b6 (pink)
- 转化数: #4ade80 (green)
- ROI: #38bdf8 (blue)

Each card gets a top border accent: `border-top: 3px solid var(--accent-*)`.

### Task 3: CSS Styling — Table, Collapsible, Suggestions, Footer

**Files:**
- Modify: `index.html` — extend `<style>` block

- [ ] **Step 1: Add collapsible panel styles**

```css
.collapsible { margin-bottom: 24px; }
.collapsible-header {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 20px; cursor: pointer;
  color: var(--text-primary); font: inherit; transition: background 0.15s;
}
.collapsible-header:hover { background: #334155; }
.collapsible-header[aria-expanded="false"] { border-radius: var(--radius); }
.collapsible-header[aria-expanded="false"] + .collapsible-body { display: none; }
.collapse-icon::after { content: '▲'; font-size: 12px; transition: transform 0.2s; }
.collapsible-header[aria-expanded="false"] .collapse-icon::after { content: '▼'; }
.collapsible-body { padding: 16px 0; }
```

- [ ] **Step 2: Add table styles**

```css
.channel-table { width: 100%; border-collapse: collapse; }
.channel-table th, .channel-table td {
  text-align: right; padding: 12px 16px; border-bottom: 1px solid var(--border);
}
.channel-table th:first-child, .channel-table td:first-child { text-align: left; }
.channel-table th { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.channel-table td { font-size: 14px; }
.channel-table tbody tr:hover { background: rgba(255,255,255,0.03); }

.channel-name { font-weight: 600; }
.roi-badge { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.roi-high { background: rgba(74,222,128,0.15); color: var(--accent-green); }
.roi-mid { background: rgba(251,191,36,0.15); color: #fbbf24; }
.roi-low { background: rgba(248,113,113,0.15); color: var(--accent-red); }
```

- [ ] **Step 3: Add suggestions and footer styles**

```css
.suggestions-list { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.suggestion-item {
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 20px;
  display: flex; align-items: flex-start; gap: 12px;
}
.suggestion-item .priority {
  width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0;
}
.priority-high { background: var(--accent-red); }
.priority-mid { background: var(--accent-orange); }
.priority-low { background: var(--accent-blue); }
.suggestion-item .content { flex: 1; }
.suggestion-item .title { font-weight: 600; margin-bottom: 4px; }
.suggestion-item .desc { font-size: 13px; color: var(--text-secondary); }

.footer { text-align: center; padding: 24px; color: var(--text-secondary); font-size: 13px; border-top: 1px solid var(--border); }
```

### Task 4: CSS — Responsive Media Queries

**Files:**
- Modify: `index.html` — add media queries to `<style>` block

- [ ] **Step 1: Add tablet and mobile breakpoints**

```css
/* Tablet: 2 columns */
@media (max-width: 1024px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .container { padding: 16px 20px; }
  .header { padding: 16px 20px; }
}

/* Mobile: 1 column + horizontal scroll for table */
@media (max-width: 640px) {
  .metrics-grid { grid-template-columns: 1fr; }
  .header { flex-direction: column; gap: 4px; }
  .header h1 { font-size: 20px; }
  .metric-card { padding: 16px; }
  .metric-card .value { font-size: 24px; }
  .container { padding: 12px 16px; }

  /* Scrollable table wrapper */
  .channel-section .collapsible-body { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .channel-table { min-width: 700px; }
  .channel-table th, .channel-table td { padding: 8px 10px; font-size: 12px; }

  .suggestion-item { padding: 12px 16px; }
}
```

### Task 5: JavaScript — Data, Rendering & Interactivity

**Files:**
- Modify: `index.html` — add `<script>` block before `</body>`

- [ ] **Step 1: Add data model**

```js
const reportData = {
  date: '2026-05-14',
  updateTime: '2026-05-15 08:30:00',
  metrics: [
    { label: '总消耗', value: '¥128,450', change: '+12.5%', direction: 'up', color: 'blue' },
    { label: '曝光量', value: '2,847,320', change: '+8.3%', direction: 'up', color: 'purple' },
    { label: '点击量', value: '68,235', change: '+15.2%', direction: 'up', color: 'orange' },
    { label: 'CTR', value: '2.40%', change: '+0.3%', direction: 'up', color: 'green' },
    { label: 'CPM', value: '¥45.12', change: '-3.1%', direction: 'down', color: 'yellow' },
    { label: 'CPC', value: '¥1.88', change: '-2.4%', direction: 'down', color: 'pink' },
    { label: '转化数', value: '3,412', change: '+18.7%', direction: 'up', color: 'green' },
    { label: 'ROI', value: '3.42', change: '+0.28', direction: 'up', color: 'blue' },
  ],
  channels: [
    { name: '巨量引擎', cost: 45200, impressions: 980000, clicks: 24500, ctr: 2.50, cpm: 46.12, cpc: 1.84, conversions: 1320, roi: 3.85 },
    { name: '腾讯广告', cost: 32800, impressions: 720000, clicks: 15800, ctr: 2.19, cpm: 45.56, cpc: 2.08, conversions: 890, roi: 3.12 },
    { name: '快手', cost: 18500, impressions: 520000, clicks: 12400, ctr: 2.38, cpm: 35.58, cpc: 1.49, conversions: 560, roi: 4.21 },
    { name: '百度', cost: 15600, impressions: 310000, clicks: 8200, ctr: 2.65, cpm: 50.32, cpc: 1.90, conversions: 320, roi: 2.75 },
    { name: '小红书', cost: 9850, impressions: 195000, clicks: 5100, ctr: 2.62, cpm: 50.51, cpc: 1.93, conversions: 210, roi: 2.98 },
    { name: 'Google', cost: 6500, impressions: 122320, clicks: 2235, ctr: 1.83, cpm: 53.14, cpc: 2.91, conversions: 112, roi: 2.41 },
  ],
  suggestions: [
    { title: '快手渠道 ROI 表现优异，建议增加预算投放', desc: '快手当前 ROI 4.21 远超其他渠道，CPC 仅 ¥1.49，建议将预算提升 20-30%。', priority: 'high' },
    { title: 'Google 渠道 CTR 偏低，需优化素材', desc: 'Google CTR 仅 1.83% 低于平均值，建议更新广告素材和文案，A/B 测试不同创意方向。', priority: 'high' },
    { title: '百度渠道 CPM 偏高，可尝试调整定向', desc: 'CPM ¥50.32 高于大盘，建议收缩地域定向或调整人群包以降低获客成本。', priority: 'mid' },
    { title: '整体 CPM 呈下降趋势，投放效率持续改善', desc: 'CPM 环比下降 3.1%，说明素材质量和受众匹配度在提升，保持当前优化策略。', priority: 'low' },
  ],
};
```

- [ ] **Step 2: Add rendering functions**

```js
function renderMetrics() {
  const grid = document.getElementById('metricsGrid');
  grid.innerHTML = reportData.metrics.map((m, i) => `
    <div class="metric-card" style="border-top: 3px solid var(--accent-${m.color})">
      <div class="label">${m.label}</div>
      <div class="value">${m.value}</div>
      <div class="change ${m.direction}">
        ${m.direction === 'up' ? '▲' : '▼'} ${m.change} 环比
      </div>
    </div>
  `).join('');
}

function roiClass(roi) {
  if (roi >= 3.5) return 'roi-high';
  if (roi >= 3.0) return 'roi-mid';
  return 'roi-low';
}

function renderChannels() {
  const tbody = document.getElementById('channelBody');
  tbody.innerHTML = reportData.channels.map(c => `
    <tr>
      <td><span class="channel-name">${c.name}</span></td>
      <td>¥${c.cost.toLocaleString()}</td>
      <td>${c.impressions.toLocaleString()}</td>
      <td>${c.clicks.toLocaleString()}</td>
      <td>${c.ctr.toFixed(2)}%</td>
      <td>¥${c.cpm.toFixed(2)}</td>
      <td>¥${c.cpc.toFixed(2)}</td>
      <td>${c.conversions.toLocaleString()}</td>
      <td><span class="roi-badge ${roiClass(c.roi)}">${c.roi.toFixed(2)}</span></td>
    </tr>
  `).join('');
}

function renderSuggestions() {
  const list = document.getElementById('suggestionsList');
  list.innerHTML = reportData.suggestions.map(s => `
    <li class="suggestion-item">
      <span class="priority priority-${s.priority}"></span>
      <div class="content">
        <div class="title">${s.title}</div>
        <div class="desc">${s.desc}</div>
      </div>
    </li>
  `).join('');
}
```

- [ ] **Step 3: Add collapsible toggle and init**

```js
document.querySelectorAll('.collapsible-header').forEach(btn => {
  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', !expanded);
  });
});

document.getElementById('updateTime').textContent = reportData.updateTime;
document.querySelector('.date').textContent = `报告日期：${reportData.date}`;

renderMetrics();
renderChannels();
renderSuggestions();
```

### Task 6: Verification

**Files:**
- No new files

- [ ] **Step 1: Open in browser and verify**
  - Open `file:///home/blueming/code/class02/index.html` in browser
  - Verify: 8 metric cards in 4-column grid
  - Verify: 6 channel rows in table with ROI badges
  - Verify: 4 suggestion items with priority dots
  - Verify: Collapsible panels toggle on click
  - Verify: Hover effects on cards and table rows
  - Verify: Resize to tablet (2 columns) and mobile (1 column)

- [ ] **Step 2: Check responsive behavior**
  - Chrome DevTools → Device Toolbar → test at 375px, 768px, 1024px, 1440px
  - Verify no horizontal overflow at mobile
  - Verify table scrolls horizontally on mobile
