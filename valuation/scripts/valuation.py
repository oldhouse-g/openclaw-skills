#!/usr/bin/env python3
"""
股票估值分析工具 - DDM + CAPM 模型
基于蟹大爷的估值方法论

用法: python3 valuation.py <股票代码>
示例: python3 valuation.py 000651.SZ
      python3 valuation.py 600519.SH
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

try:
    import tushare as ts
    import pandas as pd
    import numpy as np
except ImportError:
    print("缺少依赖，请运行: pip3 install tushare pandas numpy")
    sys.exit(1)

token = os.environ.get("TUSHARE_TOKEN", "")
if not token:
    print("错误: 缺少 TUSHARE_TOKEN 环境变量")
    sys.exit(1)

pro = ts.pro_api(token)
TODAY = pd.Timestamp.now().strftime('%Y%m%d')


# ========== 数据获取函数 ==========

def get_stock_name(ts_code):
    try:
        df = pro.stock_basic(ts_code=ts_code, fields='ts_code,name')
        return df.iloc[0]['name'] if not df.empty else ts_code
    except:
        return ts_code

def get_latest_price(ts_code):
    try:
        start = (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime('%Y%m%d')
        df = pro.daily(ts_code=ts_code, start_date=start, end_date=TODAY)
        return df.iloc[0]['close'] if not df.empty else None
    except:
        return None

def get_risk_free_rate():
    """10年期国债收益率"""
    try:
        start = (pd.Timestamp.now() - pd.Timedelta(days=60)).strftime('%Y%m%d')
        df = pro.yc_cb(ts_code='1001.CB', curve_type='0',
                       start_date=start, end_date=TODAY)
        if not df.empty:
            return df.iloc[0]['yield'] / 100
    except:
        pass
    return 0.025  # 降级: 2.5%

def calculate_beta(ts_code, days=252):
    """用最近1年日收益率与沪深300回归计算Beta"""
    try:
        start = (pd.Timestamp.now() - pd.Timedelta(days=days * 2)).strftime('%Y%m%d')
        stock = pro.daily(ts_code=ts_code, start_date=start, end_date=TODAY,
                          fields='trade_date,pct_chg')
        market = pro.index_daily(ts_code='000300.SH', start_date=start, end_date=TODAY,
                                 fields='trade_date,pct_chg')
        merged = pd.merge(stock, market, on='trade_date', suffixes=('_s', '_m')).dropna()
        if len(merged) < 60:
            return 1.0
        cov = np.cov(merged['pct_chg_s'], merged['pct_chg_m'])
        return round(cov[0][1] / cov[1][1], 4)
    except:
        return 1.0

def get_market_risk_premium():
    """市场风险溢价 Rm - Rf（沪深300近5年年化 - Rf）"""
    try:
        start = (pd.Timestamp.now() - pd.Timedelta(days=365 * 5)).strftime('%Y%m%d')
        df = pro.index_daily(ts_code='000300.SH', start_date=start, end_date=TODAY,
                             fields='trade_date,close').sort_values('trade_date')
        if len(df) > 100:
            annual_ret = (df.iloc[-1]['close'] / df.iloc[0]['close']) ** (1 / 5) - 1
            rf = get_risk_free_rate()
            premium = annual_ret - rf
            if premium > 0.02:
                return premium
    except:
        pass
    return 0.06  # 降级: 6%

def get_roe(ts_code):
    try:
        df = pro.fina_indicator(ts_code=ts_code, fields='end_date,roe')
        df = df.sort_values('end_date', ascending=False)
        annual = df[df['end_date'].str.endswith('1231')]
        if not annual.empty:
            val = annual.iloc[0]['roe']
            if pd.notna(val):
                return val / 100
    except:
        pass
    return None

def calculate_roic(ts_code):
    """ROIC = NOPAT / 投入资本"""
    try:
        inc = pro.income(ts_code=ts_code,
                         fields='end_date,operate_profit,income_tax,total_profit')
        inc = inc.sort_values('end_date', ascending=False)
        inc_a = inc[inc['end_date'].str.endswith('1231')]

        bs = pro.balancesheet(ts_code=ts_code,
                              fields='end_date,total_assets,notes_payable,acct_payable,adv_receipts,oth_payable')
        bs = bs.sort_values('end_date', ascending=False)
        bs_a = bs[bs['end_date'].str.endswith('1231')]

        if inc_a.empty or bs_a.empty:
            return None

        op = inc_a.iloc[0]['operate_profit']
        tp = inc_a.iloc[0]['total_profit']
        tax = inc_a.iloc[0]['income_tax']
        if pd.isna(op):
            return None

        # 有效税率
        eff_tax = (tax / tp) if (pd.notna(tax) and pd.notna(tp) and tp > 0) else 0.25
        nopat = op * (1 - eff_tax)

        # 投入资本 = 总资产 - 无息流动负债
        ta = bs_a.iloc[0]['total_assets']
        if pd.isna(ta) or ta <= 0:
            return None
        nicl = 0
        for c in ['notes_payable', 'acct_payable', 'adv_receipts', 'oth_payable']:
            v = bs_a.iloc[0].get(c, 0)
            nicl += v if pd.notna(v) else 0
        ic = ta - nicl
        if ic <= 0:
            return None

        result = nopat / ic
        return round(result, 4) if pd.notna(result) else None
    except:
        return None

def get_dividend_info(ts_code):
    """返回 (过去一年每股分红合计, 是否持续分红3年)"""
    try:
        df = pro.dividend(ts_code=ts_code,
                          fields='end_date,cash_div,cash_div_tax,div_proc')
        if df.empty:
            return 0, False
        # 只取已实施的分红
        impl = df[df['div_proc'] == '实施'].copy()
        if impl.empty:
            return 0, False
        impl = impl.sort_values('end_date', ascending=False)
        impl['year'] = impl['end_date'].str[:4]
        # 按年汇总
        yearly = impl.groupby('year')['cash_div_tax'].sum().sort_index(ascending=False)
        # 取最近完整年度的分红
        # 分红从公告到实施可能跨年，所以排除当年和上一年
        current_year = int(pd.Timestamp.now().strftime('%Y'))
        latest_div = 0
        for yr_str in yearly.index:
            yr = int(yr_str)
            if yr <= current_year - 2:
                latest_div = yearly[yr_str]
                break
        # 如果都不满足，用最近的
        if latest_div == 0 and len(yearly) > 0:
            latest_div = yearly.iloc[0]
        continuous = len(yearly) >= 3
        return (latest_div if pd.notna(latest_div) else 0), continuous
    except:
        return 0, False

def get_pe_ttm(ts_code):
    try:
        start = (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime('%Y%m%d')
        df = pro.daily_basic(ts_code=ts_code, start_date=start, end_date=TODAY,
                             fields='trade_date,pe_ttm')
        return df.iloc[0]['pe_ttm'] if not df.empty else None
    except:
        return None

def get_revenue_cagr(ts_code, years=3):
    """返回 (营收CAGR, 利润CAGR)"""
    try:
        df = pro.income(ts_code=ts_code, fields='end_date,revenue,n_income')
        df = df.sort_values('end_date', ascending=False)
        annual = df[df['end_date'].str.endswith('1231')]
        if len(annual) < years + 1:
            return None, None

        def cagr(end_val, start_val, n):
            if start_val > 0 and end_val > 0:
                return (end_val / start_val) ** (1 / n) - 1
            return None

        rev = cagr(annual.iloc[0]['revenue'], annual.iloc[years]['revenue'], years)
        ni = cagr(annual.iloc[0]['n_income'], annual.iloc[years]['n_income'], years)
        return rev, ni
    except:
        return None, None

def get_free_cash_flow(ts_code):
    try:
        df = pro.cashflow(ts_code=ts_code,
                          fields='end_date,n_cashflow_act,c_pay_acq_const_fiolta')
        df = df.sort_values('end_date', ascending=False)
        annual = df[df['end_date'].str.endswith('1231')]
        if annual.empty:
            return None
        ocf = annual.iloc[0]['n_cashflow_act']
        capex = annual.iloc[0].get('c_pay_acq_const_fiolta', 0)
        capex = capex if pd.notna(capex) else 0
        return (ocf - capex) if pd.notna(ocf) else None
    except:
        return None

def get_total_shares(ts_code):
    """获取总股本（万股）"""
    try:
        start = (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime('%Y%m%d')
        df = pro.daily_basic(ts_code=ts_code, start_date=start, end_date=TODAY,
                             fields='trade_date,total_share')
        return df.iloc[0]['total_share'] if not df.empty else None
    except:
        return None


# ========== 主分析函数 ==========

def valuation_analysis(ts_code):
    name = get_stock_name(ts_code)
    print(f"\n{'='*60}")
    print(f"  股票估值分析报告 - {name} ({ts_code})")
    print(f"  分析日期: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    print(f"{'='*60}")

    # ===== 第一步：资格筛选 =====
    print(f"\n{'─'*60}")
    print("【第一步】资格筛选")
    print(f"{'─'*60}")

    D_0, continuous_div = get_dividend_info(ts_code)
    if D_0 == 0:
        print("  ⚠️  该公司无分红记录，DDM估值方法不适用！")
        print("  建议使用 DCF 自由现金流模型")
    else:
        print(f"  最近每股分红 D_0: {D_0:.4f} 元")
        status = "是（近3年）" if continuous_div else "否（不足3年）"
        print(f"  持续分红: {status}")

    roe = get_roe(ts_code)
    roic = calculate_roic(ts_code)
    print(f"  ROE:  {roe*100:.2f}%" if roe else "  ROE:  无数据")
    print(f"  ROIC: {roic*100:.2f}%" if roic else "  ROIC: 无数据")

    Rf = get_risk_free_rate()
    beta = calculate_beta(ts_code)
    Rm_Rf = get_market_risk_premium()
    w = Rf + beta * Rm_Rf

    print(f"\n  CAPM 参数:")
    print(f"    Rf  (无风险利率)      = {Rf*100:.2f}%")
    print(f"    β   (Beta)            = {beta:.4f}")
    print(f"    Rm-Rf (市场风险溢价)  = {Rm_Rf*100:.2f}%")
    print(f"    w   (要求回报率)      = {w*100:.2f}%")

    if roic is not None:
        if roic < w:
            print(f"\n  🔴 强烈建议放弃！ROIC ({roic*100:.2f}%) < w ({w*100:.2f}%)")
            print(f"     公司创造的价值不足以覆盖资本成本")
        else:
            print(f"\n  ✅ ROIC ({roic*100:.2f}%) > w ({w*100:.2f}%)，通过资格筛选")

    equity_risk_premium = beta * Rm_Rf
    a = Rf / equity_risk_premium if equity_risk_premium > 0 else 1
    print(f"  打折系数 a = Rf/(β*(Rm-Rf)) = {a:.4f}")

    # ===== 第二步：核心参数计算 =====
    print(f"\n{'─'*60}")
    print("【第二步】核心参数计算与数据验证")
    print(f"{'─'*60}")

    P = get_latest_price(ts_code)
    PE_TTM = get_pe_ttm(ts_code)

    if not P:
        print("  ❌ 无法获取股价，分析终止")
        return

    E_TTM = P / PE_TTM if PE_TTM and PE_TTM > 0 else None
    print(f"  最新股价 P:     {P:.2f} 元")
    print(f"  每股收益 E_TTM: {E_TTM:.4f} 元" if E_TTM else "  E_TTM: 无数据")
    print(f"  PE_TTM:         {PE_TTM:.2f}" if PE_TTM else "  PE_TTM: 无数据")
    print(f"  每股分红 D_0:   {D_0:.4f} 元")

    d = D_0 / E_TTM if E_TTM and E_TTM > 0 else 0
    print(f"  分红率 d:       {d*100:.2f}%")

    # 增长率
    print(f"\n  增长率交叉验证:")
    g_sgr = (1 - d) * roe if roe else None
    rev_cagr, ni_cagr = get_revenue_cagr(ts_code)
    g_cagr = ni_cagr if ni_cagr is not None else rev_cagr

    if g_sgr is not None:
        print(f"    g_sgr (可持续增长率)    = {g_sgr*100:.2f}%  [(1-d)*ROE]")
    if g_cagr is not None:
        print(f"    g_cagr (3年利润CAGR)    = {g_cagr*100:.2f}%")
    if rev_cagr is not None:
        print(f"    营收CAGR (参考)         = {rev_cagr*100:.2f}%")
    print(f"    g_analyst (分析师预测)  = 暂无数据")

    # 取最小
    rates = []
    if g_sgr is not None and g_sgr > 0:
        rates.append(('g_sgr', g_sgr))
    if g_cagr is not None and g_cagr > 0:
        rates.append(('g_cagr', g_cagr))

    if not rates:
        print(f"\n  ⚠️  无法计算有效增长率，使用保守值 3%")
        g_a = 0.03
        g_a_src = "保守估计"
    else:
        g_a = min(r[1] for r in rates)
        g_a_src = [r[0] for r in rates if r[1] == g_a][0]

    g_m = a * g_a
    print(f"\n    审慎增长率 g_a = {g_a*100:.2f}% (取最小, 来自 {g_a_src})")
    print(f"    最终增长率 g_m = a * g_a = {a:.4f} * {g_a*100:.2f}% = {g_m*100:.2f}%")

    model_valid = g_m < w
    if not model_valid:
        print(f"\n  🔴 注意！g_m ({g_m*100:.2f}%) >= w ({w*100:.2f}%)")
        print(f"     Gordon模型要求增长率 < 折现率，DDM估值可能不可靠")
        print(f"     以下分析仅供参考，建议使用 DCF 模型补充验证")

    # ===== 第三步：内在价值计算 =====
    print(f"\n{'─'*60}")
    print("【第三步】内在价值计算")
    print(f"{'─'*60}")

    if model_valid:
        PE_calc = d * (1 + g_m) / (w - g_m)
    else:
        # 模型失效时用保守增长率重算
        g_fallback = w * 0.8  # 取w的80%作为上限
        PE_calc = d * (1 + g_fallback) / (w - g_fallback)
        print(f"  ⚠️  使用保守增长率 g={g_fallback*100:.2f}% 替代计算")
    print(f"  PE_计算 = d*(1+g_m)/(w-g_m) = {d:.4f}*(1+{g_m*100:.2f}%)/({w*100:.2f}%-{g_m*100:.2f}%)")
    print(f"  PE_计算 (内在): {PE_calc:.2f}")
    print(f"  PE_TTM  (市场): {PE_TTM:.2f}" if PE_TTM else "  PE_TTM: 无数据")

    if E_TTM:
        iv = PE_calc * E_TTM
        print(f"\n  内在价值: {iv:.2f} 元")
        print(f"  当前股价: {P:.2f} 元")
        disc = (iv - P) / P * 100
        print(f"  折溢价:   {disc:+.2f}%")

    # ===== 第四步：估值决策与风险分析 =====
    print(f"\n{'─'*60}")
    print("【第四步】估值决策与风险分析")
    print(f"{'─'*60}")

    div_yield = D_0 / P if P > 0 else 0
    exp_ret = div_yield + g_m
    print(f"  股息率:       {div_yield*100:.2f}%")
    print(f"  实际预期收益: {exp_ret*100:.2f}% (股息率 + g_m)")

    if exp_ret > 0.10:
        print(f"  ✅ 预期收益 > 10%，值得投资")
    else:
        print(f"  ⚠️  预期收益 < 10%，吸引力不足")

    # 估值判断
    if PE_TTM:
        if PE_calc > PE_TTM:
            print(f"\n  ✅ PE_计算 ({PE_calc:.2f}) > PE_TTM ({PE_TTM:.2f})，可能低估")
        else:
            print(f"\n  ⚠️  PE_计算 ({PE_calc:.2f}) < PE_TTM ({PE_TTM:.2f})，可能高估")

    # 股息风险
    ear_yield = 1 / PE_TTM if PE_TTM and PE_TTM > 0 else 0
    if div_yield > ear_yield and ear_yield > 0:
        print(f"\n  🔴 股息风险警告！")
        print(f"     股息率 ({div_yield*100:.2f}%) > 盈利率 ({ear_yield*100:.2f}%)")
        print(f"     警惕寅吃卯粮风险！")
        fcf = get_free_cash_flow(ts_code)
        shares = get_total_shares(ts_code)
        if fcf is not None:
            print(f"     自由现金流: {fcf/1e8:.2f} 亿元")
            if shares:
                total_div_est = D_0 * shares * 10000  # shares是万股
                print(f"     估算总分红: {total_div_est/1e8:.2f} 亿元")
                if fcf > total_div_est:
                    print(f"     ✅ 自由现金流可覆盖分红")
                else:
                    print(f"     🔴 自由现金流不足以覆盖分红！可能借债或变卖资产分红")
            if fcf < 0:
                print(f"     🔴 自由现金流为负，存在借债分红风险！")

    # 成长风险
    if PE_calc > 10 and PE_TTM and PE_TTM > 10 and g_m > div_yield * 2:
        print(f"\n  ⚠️  成长风险提示")
        print(f"     PE较高且增长率远大于股息率，需警惕成长股陷阱")
        if g_m > 0:
            peg = PE_TTM / (g_m * 100)
            print(f"     PEG = PE_TTM / (g_m*100) = {PE_TTM:.2f} / {g_m*100:.1f} = {peg:.2f}")
            if peg <= 1:
                print(f"     ✅ PEG ≤ 1，估值与增长匹配")
            else:
                print(f"     ⚠️  PEG > 1，估值可能偏高")

    # ===== 第五步：情景分析与结论 =====
    print(f"\n{'─'*60}")
    print("【第五步】情景分析与结论")
    print(f"{'─'*60}")

    PE_zero = d / w if w > 0 else 0
    PE_low = d * (1.03) / (w - 0.03) if w > 0.03 else 0

    print(f"\n  估值区间:")
    print(f"    {'场景':<16} {'PE':>8} {'对应价格':>10}")
    print(f"    {'─'*38}")
    if E_TTM:
        print(f"    {'零增长':<16} {PE_zero:>8.2f} {PE_zero*E_TTM:>10.2f} 元")
        print(f"    {'低增长(3%)':<14} {PE_low:>8.2f} {PE_low*E_TTM:>10.2f} 元")
        print(f"    {'当前增长':<16} {PE_calc:>8.2f} {PE_calc*E_TTM:>10.2f} 元")
        if PE_TTM:
            print(f"    {'市场当前':<16} {PE_TTM:>8.2f} {P:>10.2f} 元")
    else:
        print(f"    零增长 PE:    {PE_zero:.2f}")
        print(f"    低增长 PE:    {PE_low:.2f}")
        print(f"    当前增长 PE:  {PE_calc:.2f}")

    # 综合结论
    print(f"\n  {'='*50}")
    print(f"  综合结论")
    print(f"  {'='*50}")

    signals = []
    if roic is not None:
        signals.append(("✅" if roic > w else "🔴",
                        f"ROIC {'>' if roic > w else '<'} 资本成本 ({roic*100:.1f}% vs {w*100:.1f}%)"))
    signals.append(("✅" if exp_ret > 0.10 else "⚠️",
                    f"预期收益 {exp_ret*100:.1f}% {'>' if exp_ret > 0.10 else '<'} 10%"))
    if PE_TTM:
        signals.append(("✅" if PE_calc > PE_TTM else "⚠️",
                        f"内在PE {PE_calc:.1f} {'>' if PE_calc > PE_TTM else '<'} 市场PE {PE_TTM:.1f}"))
    signals.append(("✅" if continuous_div else "⚠️",
                    "持续分红" if continuous_div else "分红记录不足3年"))

    for icon, msg in signals:
        print(f"    {icon} {msg}")

    pos = sum(1 for i, _ in signals if i == "✅")
    neg = sum(1 for i, _ in signals if i == "🔴")
    print(f"\n    积极信号: {pos} / 警告信号: {neg}")

    if pos >= 3 and neg == 0:
        print("    📊 综合评价: 值得深入研究，建议结合定性分析")
    elif neg > 0:
        print("    📊 综合评价: 存在明显风险，谨慎对待")
    else:
        print("    📊 综合评价: 中性，需结合护城河分析等定性判断")

    print(f"\n  ⚠️  免责声明: 此分析仅供参考，不构成投资建议")
    print(f"  ⚠️  建议结合公司护城河、管理层、行业前景做定性分析")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 valuation.py <股票代码>")
        print("示例: python3 valuation.py 000651.SZ  (格力电器)")
        print("      python3 valuation.py 600519.SH  (贵州茅台)")
        sys.exit(2)
    valuation_analysis(sys.argv[1])
