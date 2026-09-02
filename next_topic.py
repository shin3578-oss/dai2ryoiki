# -*- coding: utf-8 -*-
"""第2領域ブログ 週1投稿のリマインド

ネタ帳 topics.json の「まだ出していない一番上の1本」を院長DMへ知らせる。
記事づくり（本文・図・サムネ・サイト・note）はClaude Codeとのセッションで行うので、
このスクリプトは「今週の題はこれ」「前回からの間隔」を出すところまでを受け持つ。
通知は apotool の lw_notify.yml を呼び出す（この置き場に鍵を持たない）。

  python next_topic.py                 … 送る
  NO_NOTIFY=1 python next_topic.py     … 文面を出すだけ（動作確認）
  python next_topic.py --done <slug>   … 出し終わった1本を published へ移す（手元で使う）
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
WD = "月火水木金土日"
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "topics.json")
SITE = "https://shin3578-oss.github.io/dai2ryoiki/blog.html"


def load():
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)


def done(slug):
    """出し終わった1本を queue から published へ移す（日付は今日）。"""
    d = load()
    hit = [t for t in d["queue"] if t["slug"] == slug]
    if not hit:
        print(f"queue に {slug} がありません")
        return 1
    t = hit[0]
    d["queue"] = [x for x in d["queue"] if x["slug"] != slug]
    d["published"].append({"slug": t["slug"], "title": t["title"],
                           "posted": datetime.now(JST).strftime("%Y-%m-%d")})
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"published へ移しました: {t['title']}（残り {len(d['queue'])} 本）")
    return 0


def message():
    d = load()
    now = datetime.now(JST)
    head = f"【第2領域ブログ】今週の1本\n{now.month}月{now.day}日（{WD[now.weekday()]}）21時\n"

    last = max((p["posted"] for p in d["published"] if p.get("posted")), default="")
    gap = ""
    if last:
        days = (now.date() - datetime.strptime(last, "%Y-%m-%d").date()).days
        gap = f"前回の投稿から{days}日（{last[5:].replace('-', '/')}「{[p for p in d['published'] if p['posted'] == last][-1]['title']}」）\n"
        if days >= 14:
            gap += "※2週以上あいています。ここで1本出しておきたいところです。\n"

    if not d["queue"]:
        return (head + gap + "\nネタ帳が空になりました。\n"
                "次の10本を仕込むところから始めます。Claude Codeで「第2領域のネタ帳を足して」と言ってください。\n\n"
                + SITE)

    t = d["queue"][0]
    body = (f"\n次の題　{t['title']}\n"
            f"　切り口　{t['angle']}\n"
            f"　もとになる自動化　メニュー#{t['menu']}\n"
            f"\nClaude Codeで「第2領域の記事書いて」と言えば、"
            f"本文・図・サムネ・サイト・noteまで作ります。\n"
            f"公開の前に必ず文面をお見せします。題を変えたいときは、その場で言ってください。\n"
            f"\nネタ帳の残り　{len(d['queue'])}本（出した記事　{len(d['published'])}本）\n\n"
            + SITE)
    return head + gap + body


def main():
    if "--done" in sys.argv:
        return done(sys.argv[sys.argv.index("--done") + 1])

    msg = message()
    print(msg)

    if os.environ.get("NO_NOTIFY", "").lower() in ("1", "true", "yes"):
        print("\n[no_notify が指定されているため送信しません（動作確認用）]")
        return 0
    pat = os.environ.get("NOTIFY_PAT", "")
    if not pat:
        print("\n[NOTIFY_PAT が無いため送信しません]")
        return 0
    req = urllib.request.Request(
        "https://api.github.com/repos/shin3578-oss/apotool-automation/actions/workflows/lw_notify.yml/dispatches",
        data=json.dumps({"ref": "main", "inputs": {
            "message": msg, "bot_id": "12786828"}}).encode(),
        headers={"Authorization": "Bearer " + pat, "Accept": "application/vnd.github+json",
                 "User-Agent": "dai2ryoiki-next-topic", "Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)
    print("\n[LINEワークスへ送信しました]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
