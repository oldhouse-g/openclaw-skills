---
name: valuation
description: A股股票估值分析工具。基于DDM+CAPM模型，包含资格筛选、增长率交叉验证、内在价值计算、风险分析和情景分析。当用户要求分析某只股票估值、判断是否值得投资时使用。
allowed-tools:
  - Bash(python:*)
  - Read
---

# 股票估值分析

对A股股票进行DDM+CAPM估值分析，五步完成：

1. 资格筛选（分红、ROIC、CAPM）
2. 核心参数计算（增长率交叉验证）
3. 内在价值计算
4. 风险分析（股息风险、成长股陷阱）
5. 情景分析与结论

## 使用方法

```bash
python3 scripts/valuation.py <股票代码>
```

示例：
```bash
python3 scripts/valuation.py 000651.SZ    # 格力电器
python3 scripts/valuation.py 600519.SH    # 贵州茅台
```

## 依赖

- Python3, tushare, pandas, numpy
- TUSHARE_TOKEN 环境变量
