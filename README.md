# 第2領域 — 公開サイト

医科・歯科クリニック向けAI自動化サービス「第2領域」の営業ページ。

## 公開中

**https://shin3578-oss.github.io/dai2ryoiki/**

2026-08-18 公開。HTTPS有効。

## 独自ドメインに移すとき

1. ドメインを取得する（予定：`dai2ryoiki.com`）
2. DNSに GitHub Pages 向けのレコードを登録する
3. Settings → Pages → Custom domain に入力して保存
   → 旧URL（github.io）から新ドメインへ **301で転送される**
4. 手元の `config.json` に `domain` を入れて `python build_site.py` を実行し、
   canonical・OGP・構造化データ・sitemap を新URLに切り替えてから push
5. Search Console は新ドメインで**別プロパティを作り直し**、アドレス変更ツールで旧→新を申告

## ファイル

| ファイル | 中身 |
|---|---|
| `index.html` | トップページ |
| `untei.html` | 運営者情報 |
| `privacy.html` | プライバシーポリシー |
| `img/` | 写真（`og.jpg` はSNS共有用） |
| `robots.txt` / `sitemap.xml` | 検索エンジン向け |

## 直し方

**このリポジトリのHTMLを直接編集しない。** 元データは手元にある。

```
Desktop\AI\_work6-07-19_ChairsideHP  chairside.html    ← 本体（ここを直す）
  untei_body.html   ← 運営者情報
  privacy_body.html ← プライバシーポリシー
  config.json       ← ドメイン・アナリティクス・Search Consoleの値
  build_site.py     ← site\ に公開用ファイルを書き出す
  apply_photos.py   ← canva\ の写真を埋め込み直す
  build_menu.py     ← 自動化台帳から販売メニューを作り直す
  shot.py           ← PC/スマホで撮って目視確認する
  form\             ← お問い合わせ受付（GAS）
```

直したら `python build_site.py` → `site\` の中身をこのリポジトリへ。

## 補足

- 事業者（医療機関）向けのため、特定商取引法の通信販売には該当しない（同法26条）。
  `untei.html` は信用のために自主的に開示しているもの。
- 掲載している人物写真はAIで生成したイメージで、実在の人物ではない。
- お問い合わせはGASのウェブアプリで受け、スプレッドシートに記録して院長へメール通知する。
