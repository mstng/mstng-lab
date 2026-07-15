# 📓 学習ログ Webアプリ

AIチーム（ハル・リク・リン）が反応してくれる、今日の学習を記録するシンプルなWebアプリです。

## 特徴

- カテゴリ（Python / Node.js / Shell / Claude Code / その他）付きで学習内容を記録
- 記録するたびにAIチームのメンバーがランダムにコメント
- 合計記録数・連続記録日数・今日の記録数を自動集計
- カテゴリで絞り込み表示、不要な記録は削除可能
- サーバー不要、ブラウザの `localStorage` だけで動作

## 使い方

`index.html` をブラウザで開くだけ。ビルドや依存パッケージは不要です。

```bash
open webapp/index.html      # macOS
xdg-open webapp/index.html  # Linux
```

GitHub Pages で公開する場合は、このディレクトリをそのまま配信するだけで動作します。
