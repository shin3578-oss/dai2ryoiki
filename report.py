# -*- coding: utf-8 -*-
"""第2領域 デイリーレポート

昨日のサイトのアクセス状況をGA4から取り、LINEワークスの院長DMへ1通送る。
通知は apotool の lw_notify.yml を呼び出して行う（この置き場に鍵を持たない）。
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

PROPERTY = "550291203"          # Dai2Ryoiki Site
SITE = "https://shin3578-oss.github.io/dai2ryoiki/"
JST = timezone(timedelta(hours=9))


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


def one(res, i=0):
    rows = res.get("rows", [])
    return int(rows[0]["metricValues"][i]["value"]) if rows else 0


def listing(res, limit=5):
    out = []
    for row in res.get("rows", [])[:limit]:
        name = row["dimensionValues"][0]["value"]
        val = row["metricValues"][0]["value"]
        out.append((name, int(val)))
    return out


def main():
    tok = token()
    y = (datetime.now(JST) - timedelta(days=1)).strftime("%Y-%m-%d")
    prev = (datetime.now(JST) - timedelta(days=2)).strftime("%Y-%m-%d")
    rng = [{"startDate": y, "endDate": y}]

    total = report(tok, {"dateRanges": rng,
                         "metrics": [{"name": "activeUsers"},
                                     {"name": "screenPageViews"},
                                     {"name": "averageSessionDuration"}]})
    before = report(tok, {"dateRanges": [{"startDate": prev, "endDate": prev}],
                          "metrics": [{"name": "activeUsers"}]})
    src = report(tok, {"dateRanges": rng,
                       "dimensions": [{"name": "sessionSource"}],
                       "metrics": [{"name": "activeUsers"}],
                       "orderBys": [{"metric": {"metricName": "activeUsers"}, "desc": True}]})
    pages = report(tok, {"dateRanges": rng,
                         "dimensions": [{"name": "pagePath"}],
                         "metrics": [{"name": "screenPageViews"}],
                         "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}]})
    week = report(tok, {"dateRanges": [{"startDate": "7daysAgo", "endDate": "yesterday"}],
                        "metrics": [{"name": "activeUsers"}]})

    users, views = one(total, 0), one(total, 1)
    secs = 0
    if total.get("rows"):
        secs = int(float(total["rows"][0]["metricValues"][2]["value"]))
    yday = one(before)
    diff = users - yday
    arrow = "→ 前日と同じ" if diff == 0 else (f"↑ 前日より{diff}人増" if diff > 0 else f"↓ 前日より{-diff}人減")

    L = [f"【第2領域 デイリーレポート】{y}", ""]
    if users == 0:
        L += ["昨日の訪問者はいませんでした。", "",
              "まだ誰にもURLを知らせていない段階なので、想定どおりです。"]
    else:
        L += [f"訪問者　　 {users}人（{arrow}）",
              f"ページ表示 {views}回",
              f"滞在時間　 平均 {secs // 60}分{secs % 60}秒", ""]
        if src.get("rows"):
            L.append("どこから来たか")
            for n, v in listing(src):
                label = {"(direct)": "直接アクセス（URLを直接開いた）",
                         "google": "Google検索"}.get(n, n)
                L.append(f"　{label}　{v}人")
            L.append("")
        if pages.get("rows"):
            L.append("よく見られたページ")
            for n, v in listing(pages, 3):
                label = {"/dai2ryoiki/": "トップ",
                         "/dai2ryoiki/untei.html": "運営者情報",
                         "/dai2ryoiki/privacy.html": "プライバシーポリシー"}.get(n, n)
                L.append(f"　{label}　{v}回")
            L.append("")
    L += [f"直近7日の訪問者　{one(week)}人", "",
          "問い合わせが入ったときは、別途メールが届きます。", SITE]

    msg = "\n".join(L)
    print(msg)

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
