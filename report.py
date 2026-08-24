# -*- coding: utf-8 -*-
"""第2領域 ウィークリーレポート

サイトのアクセス状況をGA4から取り、LINEワークスの院長DMへ週1通送る。
公開直後で訪問者0の日が続くため、毎晩の配信は2026-08-24に週1（月曜21時）へ落とした。
記事や検索から人が来はじめたら、毎晩の配信に戻す。
通知は apotool の lw_notify.yml を呼び出して行う（この置き場に鍵を持たない）。
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

PROPERTY = "550291203"          # Dai2Ryoiki Site（GA4）
SC_SITE = "https://shin3578-oss.github.io/dai2ryoiki/"   # Search Consoleのプロパティ
SITE = "https://shin3578-oss.github.io/dai2ryoiki/"
JST = timezone(timedelta(hours=9))
WD = "月火水木金土日"
OPEN = "2026-08-18"          # 公開日（ここからの累計を出す）


def token():
    data = urllib.parse.urlencode({
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    r = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    return json.load(urllib.request.urlopen(r, timeout=30))["access_token"]


def report(tok, body):
    r = urllib.request.Request(
        f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY}:runReport",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=60))


def search_console(tok, days_back_from, days_back_to):
    """Search Consoleの検索実績。データは2〜3日遅れるので少し前の期間を見る。
    権限が無い・データが無い場合は None を返し、レポートからその節を落とす。"""
    now = datetime.now(JST)
    s_ = (now - timedelta(days=days_back_from)).strftime("%Y-%m-%d")
    e_ = (now - timedelta(days=days_back_to)).strftime("%Y-%m-%d")
    site = urllib.parse.quote(SC_SITE, safe="")
    def q(body):
        r = urllib.request.Request(
            f"https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query",
            data=json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(r, timeout=60)).get("rows", [])
    try:
        total = q({"startDate": s_, "endDate": e_})
        words = q({"startDate": s_, "endDate": e_, "dimensions": ["query"], "rowLimit": 5})
    except Exception:
        return None
    if not total:
        return {"impressions": 0, "clicks": 0, "position": 0, "words": [], "from": s_, "to": e_}
    t = total[0]
    return {"impressions": int(t["impressions"]), "clicks": int(t["clicks"]),
            "position": t["position"],
            "words": [(w["keys"][0], int(w["impressions"]), int(w["clicks"]), w["position"])
                      for w in words],
            "from": s_, "to": e_}


def one(res, i=0):
    rows = res.get("rows", [])
    return int(float(rows[0]["metricValues"][i]["value"])) if rows else 0


def listing(res, limit=5):
    out = []
    for row in res.get("rows", [])[:limit]:
        out.append((row["dimensionValues"][0]["value"],
                    int(float(row["metricValues"][0]["value"]))))
    return out


def main():
    tok = token()
    now = datetime.now(JST)
    today = now.strftime("%Y-%m-%d")
    s7 = (now - timedelta(days=6)).strftime("%Y-%m-%d")       # この1週間（今日を含む7日）
    p_from = (now - timedelta(days=13)).strftime("%Y-%m-%d")  # その前の1週間
    p_to = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    rng = [{"startDate": s7, "endDate": today}]

    total = report(tok, {"dateRanges": rng,
                         "metrics": [{"name": "activeUsers"},
                                     {"name": "screenPageViews"},
                                     {"name": "averageSessionDuration"}]})
    before = report(tok, {"dateRanges": [{"startDate": p_from, "endDate": p_to}],
                          "metrics": [{"name": "activeUsers"}]})
    src = report(tok, {"dateRanges": rng,
                       "dimensions": [{"name": "sessionSource"}],
                       "metrics": [{"name": "activeUsers"}],
                       "orderBys": [{"metric": {"metricName": "activeUsers"}, "desc": True}]})
    pages = report(tok, {"dateRanges": rng,
                         "dimensions": [{"name": "pagePath"}],
                         "metrics": [{"name": "screenPageViews"}],
                         "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}]})
    allt = report(tok, {"dateRanges": [{"startDate": OPEN, "endDate": today}],
                        "metrics": [{"name": "activeUsers"}]})

    users, views = one(total, 0), one(total, 1)
    secs = 0
    if total.get("rows"):
        secs = int(float(total["rows"][0]["metricValues"][2]["value"]))
    ycount = one(before)
    diff = users - ycount
    arrow = "前の週と同じ" if diff == 0 else (f"前の週より{diff}人増" if diff > 0 else f"前の週より{-diff}人減")
    span = f"{s7[5:].replace('-', '/')}〜{today[5:].replace('-', '/')}"

    L = [f"【第2領域 ウィークリーレポート】{now.month}月{now.day}日"
         f"（{WD[now.weekday()]}）21時", f"この1週間（{span}）", ""]
    if users == 0:
        L += ["訪問者はいませんでした。", "",
              "まだ検索から見つけてもらえる段階ではないので、想定どおりです。",
              "記事を出す・リンクをもらうまでは、この数字は動きません。"]
    else:
        L += [f"訪問者　　　{users}人（{arrow}）",
              f"ページ表示　{views}回"]
        if secs:
            L.append(f"滞在時間　　平均 {secs // 60}分{secs % 60}秒")
        L.append("")
        if src.get("rows"):
            L.append("どこから来たか")
            for n, v in listing(src):
                label = {"(direct)": "直接アクセス（URLを直接開いた）",
                         "google": "Google検索",
                         "bing": "Bing検索",
                         "yahoo": "Yahoo!検索"}.get(n, n)
                L.append(f"　{label}　{v}人")
            L.append("")
        if pages.get("rows"):
            L.append("よく見られたページ")
            for n, v in listing(pages, 3):
                label = {"/dai2ryoiki/": "トップ",
                         "/dai2ryoiki/index.html": "トップ",
                         "/dai2ryoiki/untei.html": "運営者情報",
                         "/dai2ryoiki/privacy.html": "プライバシーポリシー"}.get(n, n)
                L.append(f"　{label}　{v}回")
            L.append("")
    sc = search_console(tok, 9, 3)   # 3日前までの7日間（Search Consoleは2〜3日遅れる）
    if sc is not None:
        if L and L[-1] != "":
            L.append("")
        L += [f"── 検索での見え方（{sc['from'][5:].replace('-','/')}〜{sc['to'][5:].replace('-','/')}）"]
        if sc["impressions"] == 0:
            L.append("　検索結果にはまだ出ていません")
        else:
            L.append(f"　検索結果に出た回数　{sc['impressions']}回")
            L.append(f"　そこから来た人　　　{sc['clicks']}人")
            L.append(f"　平均の順位　　　　　{sc['position']:.1f}位")
            if sc["words"]:
                L.append("　拾えている言葉")
                for w, imp, clk, pos in sc["words"]:
                    L.append(f"　　{w}　{imp}回・{pos:.0f}位")

    if L and L[-1] != "":
        L.append("")
    L += [f"公開してからの累計　{one(allt)}人", "",
          "問い合わせが入ったときは、別途メールが届きます。", SITE]

    msg = "\n".join(L)
    print(msg)

    if os.environ.get("NO_NOTIFY", "").lower() in ("1", "true", "yes"):
        print("\n[no_notify が指定されているため送信しません（動作確認用）]")
        return
    pat = os.environ.get("NOTIFY_PAT", "")
    if not pat:
        print("\n[NOTIFY_PAT が無いため送信しません]")
        return
    req = urllib.request.Request(
        "https://api.github.com/repos/shin3578-oss/apotool-automation/actions/workflows/lw_notify.yml/dispatches",
        data=json.dumps({"ref": "main", "inputs": {
            "message": msg, "bot_id": "12786828"}}).encode(),
        headers={"Authorization": "Bearer " + pat, "Accept": "application/vnd.github+json",
                 "User-Agent": "dai2ryoiki-report", "Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)
    print("\n[LINEワークスへ送信しました]")


if __name__ == "__main__":
    main()
