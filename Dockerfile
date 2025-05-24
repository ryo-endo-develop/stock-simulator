# Python 3.11をベースイメージとして使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係ファイルをコピー
COPY requirements.txt .

# Pythonパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルとモジュールをコピー
COPY app.py .
COPY modules/ ./modules/

# データ永続化用のディレクトリを作成
RUN mkdir -p /app/data

# Streamlitの設定ファイルをコピー
COPY .streamlit/ ./.streamlit/

# ポート8501を公開
EXPOSE 8501

# ヘルスチェックを追加
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# アプリケーションを実行
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
