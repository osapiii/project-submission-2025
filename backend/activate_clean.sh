#!/bin/bash
# 安全な仮想環境アクティベーション用スクリプト

# 既存の仮想環境があれば無効化
if [ -n "$VIRTUAL_ENV" ]; then
    echo "🔄 Deactivating existing virtual environment: $VIRTUAL_ENV"
    deactivate 2>/dev/null || true
fi

# 念のため環境変数をクリア
unset VIRTUAL_ENV
unset VIRTUAL_ENV_PROMPT
unset _OLD_VIRTUAL_PATH
unset _OLD_VIRTUAL_PYTHONHOME

# 新しい仮想環境をアクティベート
if [ -f "venv/bin/activate" ]; then
    echo "✨ Activating virtual environment: $(pwd)/venv"
    source venv/bin/activate
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
    python --version
else
    echo "❌ Error: venv/bin/activate not found in $(pwd)"
    echo "💡 Run: python3.12 -m venv venv"
fi 