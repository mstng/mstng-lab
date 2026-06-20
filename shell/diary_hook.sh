#!/bin/bash
# Claude CodeのStopフック
# セッション終了時に diary/ へ作業ログを自動追記する
#
# 設定方法: .claude/settings.json の hooks.Stop に登録する
# 詳細: https://qiita.com/mstng/items/fdf798b0fda912054c70

DATE=$(date +%Y%m%d)
TIME=$(date +%H:%M)
DIARY_DIR="$HOME/diary"   # ← 好きなパスに変更してください
DIARY_FILE="$DIARY_DIR/$DATE.md"

# stdinのJSONを読み捨て（hookの仕様上必要）
cat > /dev/null

# 日記ファイルがなければ今日の見出しを作る
if [ ! -f "$DIARY_FILE" ]; then
  mkdir -p "$DIARY_DIR"
  cat > "$DIARY_FILE" << EOF
# $DATE

## Claude作業ログ

EOF
fi

# 「## Claude作業ログ」セクションがなければ追加
if ! grep -q "## Claude作業ログ" "$DIARY_FILE"; then
  echo "" >> "$DIARY_FILE"
  echo "## Claude作業ログ" >> "$DIARY_FILE"
  echo "" >> "$DIARY_FILE"
fi

# タイムスタンプを追記
echo "- $TIME: Claudeとセッション" >> "$DIARY_FILE"
