---
name: stock-briefing
description: 股市简报 - 零依赖版。不需要任何API Key，纯Python标准库即可运行。当蟹大爷说"来份股市简报"、"股市简报"时使用。
allowed-tools:
  - Bash(python:*)
  - Read
---

# 股市简报

零依赖的股市简报生成器。不需要 tushare、不需要 API Key，任何环境都能跑。

## 使用方法

```bash
python3 scripts/stock_briefing.py
```

**把脚本输出原样发给蟹大爷，不要修改、不要补充、不要总结。**

## 数据来源

- A股大盘指数+成交额：东方财富 push2his API
- A股个股行情：腾讯日K线 web.ifzq.gtimg.cn
- 港股行情：腾讯日K线 + 实时接口（名称）
- 财经新闻：财联社电报 API

## 零依赖

- 不需要 pip install 任何包
- 不需要任何 API Key 或 Token
- 只用 Python 标准库（urllib, json, re, datetime）

## 自选股修改

编辑 `scripts/stock_briefing.py` 顶部的 `A_STOCKS` 和 `HK_STOCKS` 列表。
