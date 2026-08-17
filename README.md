# 第2領域 — 公開サイト

医科・歯科クリニック向けAI自動化サービス「第2領域」の営業ページ。

## いまの状態

**このリポジトリは非公開（private）です。GitHub Pages はまだ有効にしていません。**
＝ まだ世の中の誰も見られません。

## 公開するときの手順（3分）

GitHub Pages の無料枠は公開リポジトリのみのため、公開に切り替える必要があります。

1. Settings → General → 一番下 `Change repository visibility` → **Public** に変更
2. Settings → Pages → Source を `Deploy from a branch`、Branch を `main` / `(root)` にして Save
3. 1〜2分待つと `https://shin3578-oss.github.io/dai2ryoiki/` で見られるようになる

独自ドメインを使う場合は、ドメインを取得したあと Settings → Pages → Custom domain に入力し、
DNSに CNAME レコード（`shin3578-oss.github.io`）を登録する。

## ファイル

| ファイル | 中身 |
|---|---|
| `index.html` | トップページ（営業ページ本体） |
| `untei.html` | 運営者情報 |

## 直し方

**このリポジトリのHTMLを直接編集しない。** 元データは手元にある。

```
Desktop\AI\_work\2026-07-19_ChairsideHP\
  chairside.html   ← 本体（ここを直す）
  untei_body.html  ← 運営者情報の中身
  build_site.py    ← site\ に公開用HTMLを書き出す
  apply_photos.py  ← canva\ の写真を埋め込み直す
  build_menu.py    ← 自動化台帳から販売メニューを作り直す
  shot.py          ← PC/スマホで撮って目視確認する
```

直したら `python build_site.py` → `site\` の中身をこのリポジトリに上げる。

## 補足

- 本サービスは**事業者（医療機関）向け**。特定商取引法の通信販売には該当しない（同法26条）ため、
  法定の表記義務はない。`untei.html` は信用のために自主的に開示しているもの。
- 掲載している人物写真はAIで生成したイメージで、実在の人物ではない。
