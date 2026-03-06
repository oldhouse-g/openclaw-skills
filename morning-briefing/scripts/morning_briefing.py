#!/usr/bin/env python3
"""
M早报 - 股市晨报生成器
全自动获取数据、分析量价关系、生成格式化简报。
模型只需运行本脚本，把输出发给蟹大爷。
"""

import os
import sys
import json
import time
import urllib.request
from datetime import datetime, timedelta

# ─── 配置 ───────────────────────────────────────────────
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")

# 自选股列表（修改这里即可增删）
A_STOCKS = [
    ("600519.SH", "贵州茅台"),
    ("000333.SZ", "美的集团"),
    ("000651.SZ", "格力电器"),
    ("600887.SH", "伊利股份"),
    ("600036.SH", "招商银行"),
    ("000001.SZ", "平安银行"),
]

HK_STOCKS = [
    ("00700.HK", "腾讯控股"),
    ("09988.HK", "阿里巴巴"),
    ("00992.HK", "联想集团"),
    ("01810.HK", "小米集团"),
]

# 大盘指数
INDICES = [
    ("000001.SH", "上证指数"),
    ("399001.SZ", "深证成指"),
    ("399006.SZ", "创业板指"),
]

# ─── Tushare 数据获取 ─────────────────────────────────────

def tushare_api(api_name, **params):
    """直接调用Tushare HTTP API，不依赖tushare包"""
    payload = {
        "api_name": api_name,
        "token": TUSHARE_TOKEN,
        "params": params,
        "fields": "",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://api.tushare.pro",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            return None, result.get("msg", "unknown error")
        fields = result["data"]["fields"]
        items = result["data"]["items"]
        rows = [dict(zip(fields, row)) for row in items]
        return rows, None
    except Exception as e:
        return None, str(e)


def get_trade_dates(n=6):
    """获取最近n个交易日"""
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=20)).strftime("%Y%m%d")
    rows, err = tushare_api("trade_cal", exchange="SSE", start_date=start,
                            end_date=end, is_open="1")
    if err or not rows:
        print(f"⚠️ 获取交易日历失败: {err}", file=sys.stderr)
        return []
    dates = sorted([r["cal_date"] for r in rows], reverse=True)
    return dates[:n]


def get_index_daily(ts_code, start_date, end_date):
    """获取指数日线"""
    rows, err = tushare_api("index_daily", ts_code=ts_code,
                            start_date=start_date, end_date=end_date)
    if err:
        print(f"⚠️ 获取指数{ts_code}失败: {err}", file=sys.stderr)
        return []
    return sorted(rows, key=lambda r: r["trade_date"])


def get_a_stock_daily(ts_code, trade_date):
    """获取A股个股日线"""
    rows, err = tushare_api("daily", ts_code=ts_code, trade_date=trade_date)
    if err or not rows:
        return None
    return rows[0]


def get_hk_daily_tencent(codes, target_date=None):
    """
    腾讯日K线接口获取港股数据（无频率限制）。
    使用日K线历史数据，精确匹配目标日期。
    target_date: YYYYMMDD 格式
    """
    result = {}
    # 先用日K线接口拿每只股票的近期数据
    for code in codes:
        pure_code = code.replace(".HK", "")
        kline_url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=hk{pure_code},day,,,10,qfq"
        req = urllib.request.Request(kline_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode("utf-8"))
            klines = (data.get("data", {}).get(f"hk{pure_code}", {}).get("day", [])
                      or data.get("data", {}).get(f"hk{pure_code}", {}).get("qfqday", []))
            if not klines:
                continue

            # 格式: [日期, 开盘, 收盘, 最高, 最低, 成交量]
            # 日期格式: "2026-03-05"
            target_fmt = f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:]}" if target_date else None

            # 查找目标日和前一日
            target_row = None
            prev_row = None
            for i, k in enumerate(klines):
                if target_fmt and k[0] == target_fmt:
                    target_row = k
                    if i > 0:
                        prev_row = klines[i - 1]
                    break

            if not target_row:
                # 没有精确匹配，取最后一行
                target_row = klines[-1]
                if len(klines) >= 2:
                    prev_row = klines[-2]

            close = float(target_row[2])
            if prev_row:
                prev_close = float(prev_row[2])
                pct_chg = (close - prev_close) / prev_close * 100 if prev_close else 0
            else:
                prev_close = float(target_row[1])  # 用当日开盘做备用
                pct_chg = 0

            result[code] = {
                "name": "",  # 日K线不含名称，后面补
                "close": close,
                "prev_close": prev_close,
                "pct_chg": round(pct_chg, 2),
                "trade_date": target_row[0].replace("-", ""),
            }
        except Exception as e:
            print(f"⚠️ 腾讯日K获取{code}失败: {e}", file=sys.stderr)

    # 补充股票名称（用实时接口一次性获取）
    qt_codes = [f"r_hk{c.replace('.HK','')}" for c in codes]
    url = f"https://qt.gtimg.cn/q={','.join(qt_codes)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode("gbk")
        for line in text.strip().split("\n"):
            if "=" not in line:
                continue
            var_name, val = line.split("=", 1)
            val = val.strip(' ";')
            parts = val.split("~")
            if len(parts) < 10:
                continue
            code = parts[2] + ".HK"
            name = parts[1]
            if code in result:
                result[code]["name"] = name
    except:
        pass

    return result


def get_news_cls():
    """从财联社抓取早间新闻精选（多种方式尝试）"""
    import re

    # 方法1：财联社电报API（找"早间新闻精选"）
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

        # 优先找标题含"早间新闻精选"的条目
        for item in rolls:
            title = item.get("title", "")
            content = item.get("content", "")
            if "早间新闻精选" in title:
                # 提取编号新闻
                text = re.sub(r'<[^>]+>', '', content)  # strip HTML tags
                # 用"行首数字+、"分割，避免内容中的小数点被误切
                # 匹配 "\n1、" "\n2、" 格式
                items = re.findall(r'(?:^|\n)\d{1,2}[、]\s*(.+?)(?=\n\d{1,2}[、]|\Z)', text, re.DOTALL)
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
        if news:
            return news
    except Exception as e:
        print(f"⚠️ 财联社API失败: {e}", file=sys.stderr)

    # 方法2：直接抓取页面
    try:
        url = "https://www.cls.cn/telegraph"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode("utf-8")
        idx = html.find("早间新闻精选")
        if idx != -1:
            chunk = html[idx:idx + 5000]
            matches = re.findall(r'[1-9]\d?[、．.]([^<\n]{10,120})', chunk)
            news = []
            for m in matches[:5]:
                clean = re.sub(r'<[^>]+>', '', m).strip()
                if clean:
                    news.append(clean)
            if news:
                return news
    except Exception as e:
        print(f"⚠️ 财联社页面抓取失败: {e}", file=sys.stderr)

    return []


# ─── 量价分析引擎 ──────────────────────────────────────────

def analyze_volume_price(amounts, pct_chgs):
    """
    基于近5日量价数据，输出分析结论。
    amounts: 近5日成交额列表（从旧到新）
    pct_chgs: 近5日上证涨跌幅列表（从旧到新）
    返回 (量能描述, 趋势判断)
    """
    if len(amounts) < 3:
        return "数据不足，无法分析", ""

    latest_amt = amounts[-1]
    prev_amt = amounts[-2]
    avg_amt = sum(amounts) / len(amounts)
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

    # amount 单位是千元，/1e9 = 万亿
    volume_summary = f"两市成交{latest_amt/1e9:.2f}万亿，{vol_desc}（较前日{amt_chg:+.1f}%），{combo}格局。"
    trend_summary = f"{trend}{analysis}"

    return volume_summary, trend_summary


# ─── 格式化输出 ─────────────────────────────────────────

def fmt_pct(pct):
    """涨跌幅带emoji"""
    if pct > 0:
        return f"📈 +{pct:.2f}%"
    elif pct < 0:
        return f"📉 {pct:.2f}%"
    else:
        return f"   {pct:.2f}%"


def fmt_bar(value, max_val, width=11):
    """文本柱状图"""
    filled = int(value / max_val * width) if max_val else 0
    filled = max(1, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def build_report():
    """生成完整晨报"""
    if not TUSHARE_TOKEN:
        print("❌ 错误：未配置 TUSHARE_TOKEN 环境变量")
        sys.exit(1)

    # 1. 获取交易日
    trade_dates = get_trade_dates(6)
    if not trade_dates:
        print("❌ 无法获取交易日历")
        sys.exit(1)

    latest = trade_dates[0]
    # 判断：如果当前时间在15:00之前且最新交易日是今天，用前一个交易日
    now = datetime.now()
    today_str = now.strftime("%Y%m%d")
    if latest == today_str and now.hour < 15:
        latest = trade_dates[1]
        dates_for_chart = trade_dates[1:6]
    else:
        dates_for_chart = trade_dates[0:5]

    dates_for_chart = sorted(dates_for_chart)  # 从旧到新

    latest_dt = datetime.strptime(latest, "%Y%m%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    date_display = f"{latest_dt.month}月{latest_dt.day}日（{weekdays[latest_dt.weekday()]}）"

    # 2. 获取大盘指数（近5日）
    start_chart = dates_for_chart[0]
    end_chart = dates_for_chart[-1]

    idx_data = {}
    for code, name in INDICES:
        rows = get_index_daily(code, start_chart, end_chart)
        idx_data[code] = {r["trade_date"]: r for r in rows}

    # 最新日大盘数据
    idx_latest = {}
    for code, name in INDICES:
        if latest in idx_data.get(code, {}):
            idx_latest[code] = idx_data[code][latest]

    # 成交额（近5日）
    sh_amounts = []
    sz_amounts = []
    sh_pcts = []
    for d in dates_for_chart:
        sh = idx_data.get("000001.SH", {}).get(d, {})
        sz = idx_data.get("399001.SZ", {}).get(d, {})
        sh_amt = sh.get("amount", 0)
        sz_amt = sz.get("amount", 0)
        sh_amounts.append(sh_amt)
        sz_amounts.append(sz_amt)
        sh_pcts.append(sh.get("pct_chg", 0))

    total_amounts = [s + z for s, z in zip(sh_amounts, sz_amounts)]

    # 3. 获取A股自选股
    a_stock_data = []
    for code, name in A_STOCKS:
        row = get_a_stock_daily(code, latest)
        if row:
            a_stock_data.append({
                "code": code,
                "name": name,
                "close": row["close"],
                "pct_chg": row["pct_chg"],
            })
        else:
            a_stock_data.append({"code": code, "name": name, "close": 0, "pct_chg": 0})

    # 4. 获取港股自选股（腾讯行情，无频率限制）
    hk_codes_list = [c for c, n in HK_STOCKS]
    hk_data_raw = get_hk_daily_tencent(hk_codes_list, target_date=latest)
    hk_stock_data = []
    for code, name in HK_STOCKS:
        if code in hk_data_raw:
            d = hk_data_raw[code]
            hk_stock_data.append({
                "code": code,
                "name": d.get("name", name),
                "close": d["close"],
                "pct_chg": d["pct_chg"],
            })
        else:
            hk_stock_data.append({"code": code, "name": name, "close": 0, "pct_chg": 0})

    # 5. 获取新闻
    news = get_news_cls()

    # 6. 量价分析
    vol_summary, trend_summary = analyze_volume_price(total_amounts, sh_pcts)

    # ─── 组装报告 ─────────────────────────────

    lines = []
    lines.append(f"📊 蟹大爷早上好！{date_display}股市收盘简报——")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("📈 大盘收盘概况")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("")

    for code, name in INDICES:
        d = idx_latest.get(code, {})
        close = d.get("close", 0)
        pct = d.get("pct_chg", 0)
        lines.append(f"{name}　{close:.2f}　{fmt_pct(pct)}")

    # 成交额
    sh_latest = sh_amounts[-1] if sh_amounts else 0
    sz_latest = sz_amounts[-1] if sz_amounts else 0
    total_latest = total_amounts[-1] if total_amounts else 0
    lines.append("")
    # amount 单位是千元，/1e9 = 万亿
    lines.append(f"沪市成交：{sh_latest/1e9:.2f}万亿 | 深市成交：{sz_latest/1e9:.2f}万亿")
    lines.append(f"两市合计：{total_latest/1e9:.2f}万亿")

    # 成交量柱状图
    lines.append("")
    lines.append("📊 近5日成交量趋势（万亿）：")
    max_amt = max(total_amounts) if total_amounts else 1
    for i, d in enumerate(dates_for_chart):
        amt = total_amounts[i]
        bar = fmt_bar(amt, max_amt)
        label = f"{d[4:6]}/{d[6:]}"
        amt_display = f"{amt/1e9:.2f}"
        # 量能标注
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

    # A股
    all_a = [s for s in a_stock_data if s["close"] > 0]
    if all_a:
        max_a = max(all_a, key=lambda s: s["pct_chg"])
        min_a = min(all_a, key=lambda s: s["pct_chg"])

    lines.append("")
    lines.append("🇨🇳 A股：")
    for s in a_stock_data:
        tag = ""
        if all_a:
            if s["code"] == max_a["code"] and max_a["pct_chg"] > 0:
                tag = "  ⬆️涨幅最大"
            elif s["code"] == min_a["code"] and min_a["pct_chg"] < 0:
                tag = "  ⬇️跌幅最大"
        # 对齐：名字4字，价格右对齐
        name_padded = s["name"].ljust(4, "　")
        lines.append(f"{name_padded}　{s['close']:>8.2f}　{fmt_pct(s['pct_chg'])}{tag}")

    # 港股
    all_hk = [s for s in hk_stock_data if s["close"] > 0]
    if all_hk:
        max_hk = max(all_hk, key=lambda s: s["pct_chg"])
        min_hk = min(all_hk, key=lambda s: s["pct_chg"])

    lines.append("")
    lines.append("🇭🇰 港股：")
    for s in hk_stock_data:
        tag = ""
        if all_hk:
            if s["code"] == max_hk["code"] and max_hk["pct_chg"] > 0:
                tag = "  ⬆️涨幅最大"
            elif s["code"] == min_hk["code"] and min_hk["pct_chg"] < 0:
                tag = "  ⬇️跌幅最大"
        name_padded = s["name"].ljust(4, "　")
        # 港股名可能含"-W"，去掉
        display_name = s["name"].replace("-W", "")
        display_name = display_name.ljust(4, "　")
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

    # 大盘涨跌概述
    idx_summary_parts = []
    for code, name in INDICES:
        d = idx_latest.get(code, {})
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
