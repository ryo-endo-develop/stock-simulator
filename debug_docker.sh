#!/bin/bash

# Docker Composeでの詳細デバッグ用起動スクリプト

echo "🔍 LLM投資アイデア検証ツール - デバッグモードで起動中..."

# データディレクトリの詳細確認
echo "📁 ホストのdataディレクトリ状況:"
ls -la ./data/
echo ""

# 既存のコンテナを停止・削除
echo "🛑 既存のコンテナを停止・削除中..."
docker-compose down

# Docker Composeでアプリケーションを起動
echo "🚀 Docker Composeでアプリケーションを起動中..."
docker-compose up --build -d

# コンテナ内のデータディレクトリを確認
echo ""
echo "🔍 コンテナ内のdataディレクトリ状況:"
docker exec stock_simulator-stock-simulator-1 ls -la /app/data/ 2>/dev/null || \
docker exec stock-simulator-stock-simulator-1 ls -la /app/data/ 2>/dev/null || \
docker exec llm-stock-analyzer-stock-simulator-1 ls -la /app/data/ 2>/dev/null || \
echo "⚠️ コンテナ名を特定できませんでした。手動で確認してください。"

echo ""
echo "✅ アプリケーションが起動しました！"
echo "🌐 ブラウザで http://localhost:8501 にアクセスしてください"
echo ""
echo "🔍 デバッグコマンド:"
echo "  docker ps                     # 実行中のコンテナ確認"
echo "  docker logs [CONTAINER_NAME]  # ログ確認"
echo "  docker exec -it [CONTAINER_NAME] /bin/bash  # コンテナ内にアクセス"
