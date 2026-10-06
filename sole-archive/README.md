# SOLE ARCHIVE

NIKE/JORDAN、SALOMON、On、HOKAのスニーカーを眺める独立系ギャラリーです。ブランド別の画面演出、展示モード、お気に入り機能を備えています。

## ローカル確認

ビルドは不要です。`dist` を静的ファイルとして配信してください。

```sh
python3 -m http.server 8080 --directory dist
```

ブラウザで `http://localhost:8080` を開きます。お気に入りはブラウザ内に保存されます。

## デプロイ

Vercelの出力ディレクトリは `dist` です。`main` ブランチを本番ブランチに設定して運用します。

写真の出典はサイト内の「写真・掲載について」と `dist/assets/credits.json` に記載しています。商品名・商標・写真の権利は各権利者に帰属します。
