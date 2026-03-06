---
name: morning-briefing
description: M早报 - 股市晨报自动生成。运行脚本即出完整简报，无需模型做任何分析。当蟹大爷要求发早报、股市简报、M早报时使用。
allowed-tools:
  - Bash(python:*)
  - Read
---

# M早报

一键生成股市晨报，所有数据获取、分析、格式化全在脚本里完成。

## 使用方法

```bash
source ~/.zshrc 2>/dev/null
python3 scripts/morning_briefing.py
```

**把脚本输出原样发给蟹大爷，不要修改、不要补充、不要总结。**

## 依赖

- 环境变量：`TUSHARE_TOKEN`（已配置在 ~/.zshrc）
- Python 标准库（无需 pip install）
- 网络：Tushare API + 腾讯行情 + 财联社

## 自选股修改

编辑 `scripts/morning_briefing.py` 顶部的 `A_STOCKS` 和 `HK_STOCKS` 列表。

## 常见问题

- 港股数据走腾讯行情接口，无频率限制
- 15:00前运行取前一个交易日数据，15:00后取当日
- 新闻抓取财联社早间精选，若抓取失败显示"暂未获取到"
