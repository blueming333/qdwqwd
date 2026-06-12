# Google Play Scraper

抓取 Google Play 应用详情页并输出结构化 Markdown 报告的小工具。

## 功能

- 通过 Playwright（无头浏览器）抓取应用详情页
- 解析核心元数据：名称、开发者、评分、评论数、下载量、版本、大小、分类、最后更新
- 解析富内容：应用描述、截图链接、Top N 评测
- 输出结构化 Markdown 报告
- CLI 参数可配置（应用 ID、地区语言、输出路径）

## 环境要求

- Python 3.9+
- 可访问 `play.google.com` 的网络

## 安装

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器（仅 Chromium 就够）
playwright install chromium
```

> 第一次 `playwright install` 会下载约 150 MB 的浏览器二进制。

## 运行

```bash
# 抓取默认应用并写报告到 reports/
python main.py

# 指定其他应用
python main.py --app-id com.whatsapp

# 指定地区 / 语言
python main.py --app-id com.whatsapp --lang en --country us

# 自定义输出文件
python main.py --app-id com.whatsapp --output reports/whatsapp.md

# 查看完整选项
python main.py --help
```

## 报告输出

文件位置：`reports/<app-id>-<YYYYMMDD-HHMMSS>.md`

报告结构（计划）：

1. 元数据表格（名称 / 开发者 / 评分 / 下载量 / 版本 …）
2. 应用描述（去除 HTML 标签）
3. 评分分布
4. 截图 URL 列表
5. 最近 N 条评测

## 目录结构（计划中）

```
.
├── README.md
├── requirements.txt
├── main.py              # CLI 入口
├── src/
│   ├── __init__.py
│   ├── config.py        # 常量 / 配置
│   ├── scraper.py       # Playwright 抓取
│   ├── parser.py        # 字段解析
│   └── report.py        # Markdown 生成
└── reports/             # 生成的报告
```

## License

MIT
