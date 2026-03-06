#!/usr/bin/env python3
"""
股市简报 - 零依赖版股市报告生成器
数据全部来自公开免费接口（东方财富+腾讯行情+财联社），
不需要任何 API Key，纯 Python 标准库即可运行。
"""

import sys
import json
import time
import re
import urllib.request
from datetime import datetime, timedelta


# ─── 配置 ───────────────────────────────────────────────

# 自选股列表（修改这里即可增删）
A_STOCKS = [
    ("sh600519", "600519.SH", "贵州茅台"),
    ("sz000333", "000333.SZ", "美的集团"),
    ("sz000651", "000651.SZ", "格力电器"),
    ("sh600887", "600887.SH", "伊利股份"),
    ("sh600036", "600036.SH", "招商银行"),
    ("sz000001", "000001.SZ", "平安银行"),
]

HK_STOCKS = [
    ("00700.HK", "腾讯控股"),
    ("09988.HK", "阿里巴巴"),
    ("00992.HK", "联想集团"),
    ("01810.HK", "小米集团"),
]

# 大盘指数（东方财富 secid: 1=上海, 0=深圳）
INDICES = [
    ("1.000001", "sh000001", "上证指数"),
    ("0.399001", "sz399001", "深证成指"),
    ("0.399006", "sz399006", "创业板指"),
]


# ─── 东方财富接口（大盘指数，含成交额） ──────────────────────

def eastmoney_kline(secid, days=6):
    """
    东方财富日K线，返回 [{date, open, close, high, low, volume, amount, pct_chg}, ...]
    amount 单位：元
    """
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=20)).strftime("%Y%m%d")
    url = (
        f"http://push2his.eastmoney.com/api/qt/stock/kline/get?"
        f"secid={secid}&fields1=f1,f2,f3,f4,f5,f6"
        f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
        f"&klt=101&fqt=1&beg={start}&end={end}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode("utf-8"))
        klines = data.get("data", {}).get("klines", [])
        result = []
        for line in klines:
            # 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
            parts = line.split(",")
            if len(parts) < 11:
                continue
            result.append({
                "date": parts[0].replace("-", ""),
                "open": float(parts[1]),
                "close": float(parts[2]),
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume": float(parts[5]),
                "amount": float(parts[6]),  # 元
                "pct_chg": float(parts[8]),
            })
        return result
    except Exception as e:
        print(f"⚠️ 东方财富获取{secid}失败: {e}", file=sys.stderr)
        return []


# ─── 腾讯日K线（A股个股+港股） ──────────────────────────────

def tencent_kline(symbol, days=10):
    """
    腾讯日K线。
    symbol: A股用 "sh600519"/"sz000333"，港股用 "hk00700"
    返回 [{date, open, close, high, low, volume}, ...]
    """
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,,{days},qfq"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        kdata = data.get("data", {}).get(symbol, {})
        klines = kdata.get("day", []) or kdata.get("qfqday", [])
        result = []
        for k in klines:
            # [日期, 开盘, 收盘, 最高, 最低, 成交量]
            if len(k) < 6:
                continue
            result.append({
                "date": k[0].replace("-", ""),
                "open": float(k[1]),
                "close": float(k[2]),
                "high": float(k[3]),
                "low": float(k[4]),
                "volume": float(k[5]),
            })
        return result
    except Exception as e:
        print(f"⚠️ 腾讯K线获取{symbol}失败: {e}", file=sys.stderr)
        return []


def tencent_hk_names(codes):
    """腾讯实时接口获取港股名称"""
    qt_codes = [f"r_hk{c.replace('.HK','')}" for c in codes]
    url = f"https://qt.gtimg.cn/q={','.join(qt_codes)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    names = {}
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode("gbk")
        for line in text.strip().split("\n"):
            if "=" not in line:
                continue
            var_name, val = line.split("=", 1)
            parts = val.strip(' ";').split("~")
            if len(parts) >= 3:
                code = parts[2] + ".HK"
                names[code] = parts[1]
    except:
        pass
    return names


# ─── 财联社新闻 ──────────────────────────────────────────

def get_news_cls():
    """从财联社抓取早间新闻精选"""
    try:
        ts = int(time.time())
        api_url = f"https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&os=web&sv=8.4.6&rn=50&last_time={ts}"
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Referer": "https://www.cls.cn/telegraph",
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        rolls = data.get("data", {}).get("roll_data", [])

        # 优先找"早间新闻精选"
        for item in rolls:
            title = item.get("title", "")
            content = item.get("content", "")
            if "早间新闻精选" in title:
                text = re.sub(r'<[^>]+>', '', content)
                items = re.findall(
                    r'(?:^|\n)\d{1,2}[、]\s*(.+?)(?=\n\d{1,2}[、]|\Z)',
                    text, re.DOTALL
                )
                news = []
                for p in items:
                    p = p.strip().replace('\n', '')
                    if len(p) >= 15:
                        if len(p) > 120:
                            p = p[:117] + "..."
                        news.append(p)
                        if len(news) >= 5:
                            break
                if news:
                    return news

        # fallback: 取最近5条重要电报
        news = []
        for item in rolls[:15]:
            content = item.get("content", "") or item.get("brief", "")
            if not content:
                continue
            clean = re.sub(r'<[^>]+>', '', content).strip()
            if len(clean) > 20:
                if len(clean) > 120:
                    clean = clean[:117] + "..."
                news.append(clean)
                if len(news) >= 5:
                    break
        return news
    except Exception as e:
        print(f"⚠️ 新闻抓取失败: {e}", file=sys.stderr)
        return []


# ─── 量价分析引擎 ──────────────────────────────────────────

def analyze_volume_price(amounts, pct_chgs):
    """
    基于近5日量价数据，输出分析结论。
    amounts: 近5日成交额列表（从旧到新，单位：元）
    pct_chgs: 近5日上证涨跌幅列表（从旧到新）
    返回 (量能描述, 趋势判断)
    """
    if len(amounts) < 3:
        return "数据不足，无法分析", ""

    latest_amt = amounts[-1]
    prev_amt = amounts[-2]
    amt_chg = (latest_amt - prev_amt) / prev_amt * 100 if prev_amt else 0

    latest_pct = pct_chgs[-1]

    # 量能变化判断
    if amt_chg > 15:
        vol_desc = "显著放量"
    elif amt_chg > 5:
        vol_desc = "温和放量"
    elif amt_chg < -15:
        vol_desc = "显著缩量"
    elif amt_chg < -5:
        vol_desc = "温和缩量"
    else:
        vol_desc = "量能持平"

    # 近3日趋势
    recent_pcts = pct_chgs[-3:]
    up_days = sum(1 for p in recent_pcts if p > 0)
    down_days = sum(1 for p in recent_pcts if p < 0)

    # 量价组合模板
    if latest_pct > 0.5 and amt_chg > 10:
        combo = "放量上涨"
        analysis = "多头发力，量价齐升，短期有望延续反弹。"
    elif latest_pct > 0.5 and amt_chg < -5:
        combo = "缩量上涨"
        analysis = "反弹力度有限，上方抛压待消化，若后续不能放量确认则可能再度回落。"
    elif latest_pct < -0.5 and amt_chg > 10:
        combo = "放量下跌"
        analysis = "恐慌情绪释放，关注放量后能否快速缩量企稳。"
    elif latest_pct < -0.5 and amt_chg < -5:
        combo = "缩量下跌"
        analysis = "下跌动能衰减，空方力量不足，关注是否出现止跌信号。"
    elif abs(latest_pct) <= 0.5 and amt_chg < -10:
        combo = "缩量横盘"
        analysis = "市场观望情绪浓厚，等待方向选择。"
    else:
        combo = "量价温和"
        analysis = "市场运行平稳，多空分歧不大，短期以震荡为主。"

    # 近几日综合趋势判断
    if down_days >= 2 and latest_pct > 0:
        trend = f"近3日{down_days}跌1涨，昨日反弹修复，"
    elif up_days >= 2 and latest_pct > 0:
        trend = f"近3日连续{up_days}日上涨，"
    elif down_days >= 2:
        trend = f"近3日连续调整，"
    else:
        trend = ""

    # 成交额转万亿
    amt_wan_yi = latest_amt / 1e12
    volume_summary = f"两市成交{amt_wan_yi:.2f}万亿，{vol_desc}（较前日{amt_chg:+.1f}%），{combo}格局。"
    trend_summary = f"{trend}{analysis}"

    return volume_summary, trend_summary


# ─── 格式化工具 ─────────────────────────────────────────

def fmt_pct(pct):
    if pct > 0:
        return f"📈 +{pct:.2f}%"
    elif pct < 0:
        return f"📉 {pct:.2f}%"
    else:
        return f"   {pct:.2f}%"


def fmt_bar(value, max_val, width=11):
    filled = int(value / max_val * width) if max_val else 0
    filled = max(1, min(width, filled))
    return "█" * filled + "░" * (width - filled)


# ─── 主流程 ─────────────────────────────────────────────

def build_report():
    # 1. 获取大盘指数数据（东方财富，含成交额）
    idx_data = {}
    for secid, qt_code, name in INDICES:
        rows = eastmoney_kline(secid, days=6)
        idx_data[secid] = rows

    if not idx_data.get("1.000001"):
        print("❌ 无法获取上证指数数据")
        sys.exit(1)

    sh_rows = idx_data["1.000001"]

    # 判断最新交易日（15:00前用前一天）
    now = datetime.now()
    today_str = now.strftime("%Y%m%d")
    if sh_rows and sh_rows[-1]["date"] == today_str and now.hour < 15:
        # 今天盘中，取到前一日
        latest = sh_rows[-2]["date"] if len(sh_rows) >= 2 else sh_rows[-1]["date"]
    else:
        latest = sh_rows[-1]["date"] if sh_rows else today_str

    # 取近5个交易日数据
    all_dates = [r["date"] for r in sh_rows]
    latest_idx_pos = all_dates.index(latest) if latest in all_dates else len(all_dates) - 1
    start_pos = max(0, latest_idx_pos - 4)
    chart_dates = all_dates[start_pos:latest_idx_pos + 1]

    latest_dt = datetime.strptime(latest, "%Y%m%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    date_display = f"{latest_dt.month}月{latest_dt.day}日（{weekdays[latest_dt.weekday()]}）"

    # 大盘最新日数据
    idx_latest = {}
    for secid, qt_code, name in INDICES:
        rows = idx_data.get(secid, [])
        for r in rows:
            if r["date"] == latest:
                idx_latest[secid] = r
                break

    # 成交额（近5日，沪+深）
    sh_amounts = []
    sz_amounts = []
    sh_pcts = []
    for d in chart_dates:
        sh_row = next((r for r in idx_data.get("1.000001", []) if r["date"] == d), None)
        sz_row = next((r for r in idx_data.get("0.399001", []) if r["date"] == d), None)
        sh_amounts.append(sh_row["amount"] if sh_row else 0)
        sz_amounts.append(sz_row["amount"] if sz_row else 0)
        sh_pcts.append(sh_row["pct_chg"] if sh_row else 0)

    total_amounts = [s + z for s, z in zip(sh_amounts, sz_amounts)]

    # 2. A股个股（腾讯日K线）
    target_fmt = f"{latest[:4]}-{latest[4:6]}-{latest[6:]}"
    a_stock_data = []
    for qt_sym, ts_code, name in A_STOCKS:
        klines = tencent_kline(qt_sym, days=10)
        target_row = None
        prev_row = None
        for i, k in enumerate(klines):
            if k["date"] == latest:
                target_row = k
                if i > 0:
                    prev_row = klines[i - 1]
                break
        if not target_row and klines:
            target_row = klines[-1]
            if len(klines) >= 2:
                prev_row = klines[-2]

        if target_row and prev_row:
            pct = (target_row["close"] - prev_row["close"]) / prev_row["close"] * 100
            a_stock_data.append({
                "code": ts_code, "name": name,
                "close": target_row["close"], "pct_chg": round(pct, 2),
            })
        elif target_row:
            a_stock_data.append({
                "code": ts_code, "name": name,
                "close": target_row["close"], "pct_chg": 0,
            })
        else:
            a_stock_data.append({"code": ts_code, "name": name, "close": 0, "pct_chg": 0})

    # 3. 港股（腾讯日K线）
    hk_names_map = tencent_hk_names([c for c, n in HK_STOCKS])
    hk_stock_data = []
    for code, default_name in HK_STOCKS:
        pure = code.replace(".HK", "")
        klines = tencent_kline(f"hk{pure}", days=10)
        target_row = None
        prev_row = None
        for i, k in enumerate(klines):
            if k["date"] == latest:
                target_row = k
                if i > 0:
                    prev_row = klines[i - 1]
                break
        if not target_row and klines:
            target_row = klines[-1]
            if len(klines) >= 2:
                prev_row = klines[-2]

        display_name = hk_names_map.get(code, default_name).replace("-W", "")
        if target_row and prev_row:
            pct = (target_row["close"] - prev_row["close"]) / prev_row["close"] * 100
            hk_stock_data.append({
                "code": code, "name": display_name,
                "close": target_row["close"], "pct_chg": round(pct, 2),
            })
        elif target_row:
            hk_stock_data.append({
                "code": code, "name": display_name,
                "close": target_row["close"], "pct_chg": 0,
            })
        else:
            hk_stock_data.append({"code": code, "name": default_name, "close": 0, "pct_chg": 0})

    # 4. 新闻
    news = get_news_cls()

    # 5. 量价分析
    vol_summary, trend_summary = analyze_volume_price(total_amounts, sh_pcts)

    # ─── 组装报告 ─────────────────────────────

    lines = []
    lines.append(f"📊 蟹大爷早上好！{date_display}股市收盘简报——")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("📈 大盘收盘概况")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("")

    for secid, qt_code, name in INDICES:
        d = idx_latest.get(secid, {})
        close = d.get("close", 0)
        pct = d.get("pct_chg", 0)
        lines.append(f"{name}　{close:.2f}　{fmt_pct(pct)}")

    sh_latest = sh_amounts[-1] if sh_amounts else 0
    sz_latest = sz_amounts[-1] if sz_amounts else 0
    total_latest = total_amounts[-1] if total_amounts else 0
    lines.append("")
    lines.append(f"沪市成交：{sh_latest/1e12:.2f}万亿 | 深市成交：{sz_latest/1e12:.2f}万亿")
    lines.append(f"两市合计：{total_latest/1e12:.2f}万亿")

    # 柱状图
    lines.append("")
    lines.append("📊 近5日成交量趋势（万亿）：")
    max_amt = max(total_amounts) if total_amounts else 1
    for i, d in enumerate(chart_dates):
        amt = total_amounts[i]
        bar = fmt_bar(amt, max_amt)
        label = f"{d[4:6]}/{d[6:]}"
        amt_display = f"{amt/1e12:.2f}"
        if i > 0:
            prev = total_amounts[i - 1]
            chg = (amt - prev) / prev * 100 if prev else 0
            if chg > 15:
                tag = "  放量↑"
            elif chg > 5:
                tag = "  放量"
            elif chg < -15:
                tag = "  缩量↓"
            elif chg < -5:
                tag = "  缩量"
            else:
                tag = ""
        else:
            tag = ""
        lines.append(f"{label}　{bar}　{amt_display}{tag}")

    # 自选股
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("📋 自选股行情一览")
    lines.append("━━━━━━━━━━━━━━━━")

    all_a = [s for s in a_stock_data if s["close"] > 0]
    max_a = max(all_a, key=lambda s: s["pct_chg"]) if all_a else None
    min_a = min(all_a, key=lambda s: s["pct_chg"]) if all_a else None

    lines.append("")
    lines.append("🇨🇳 A股：")
    for s in a_stock_data:
        tag = ""
        if max_a and s["code"] == max_a["code"] and max_a["pct_chg"] > 0:
            tag = "  ⬆️涨幅最大"
        elif min_a and s["code"] == min_a["code"] and min_a["pct_chg"] < 0:
            tag = "  ⬇️跌幅最大"
        name_padded = s["name"].ljust(4, "　")
        lines.append(f"{name_padded}　{s['close']:>8.2f}　{fmt_pct(s['pct_chg'])}{tag}")

    all_hk = [s for s in hk_stock_data if s["close"] > 0]
    max_hk = max(all_hk, key=lambda s: s["pct_chg"]) if all_hk else None
    min_hk = min(all_hk, key=lambda s: s["pct_chg"]) if all_hk else None

    lines.append("")
    lines.append("🇭🇰 港股：")
    for s in hk_stock_data:
        tag = ""
        if max_hk and s["code"] == max_hk["code"] and max_hk["pct_chg"] > 0:
            tag = "  ⬆️涨幅最大"
        elif min_hk and s["code"] == min_hk["code"] and min_hk["pct_chg"] < 0:
            tag = "  ⬇️跌幅最大"
        display_name = s["name"].ljust(4, "　")
        lines.append(f"{display_name}　{s['close']:>8.2f}　{fmt_pct(s['pct_chg'])}{tag}")

    # 新闻
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("📰 今日要闻提示")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("")
    if news:
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i, n in enumerate(news[:5]):
            lines.append(f"{emojis[i]} {n}")
    else:
        lines.append("暂未获取到今日要闻")

    # 小结
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("💡 小结")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("")

    idx_summary_parts = []
    for secid, qt_code, name in INDICES:
        d = idx_latest.get(secid, {})
        pct = d.get("pct_chg", 0)
        direction = "涨" if pct > 0 else "跌"
        idx_summary_parts.append(f"{name}{direction}{abs(pct):.2f}%")
    lines.append(f"三大指数：{'，'.join(idx_summary_parts)}。")

    lines.append("")
    lines.append(f"量能分析：{vol_summary}")
    lines.append(f"趋势判断：{trend_summary}")

    print("\n".join(lines))


if __name__ == "__main__":
    build_report()
