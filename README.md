# LLM 投資アイデア検証ツール

LLM の投資アイデアを体系的に検証・比較するための専用分析ツール

## 概要

このアプリケーションは、外部の LLM（ChatGPT、Gemini、Claude 等）から得た投資アイデアを科学的に検証し、各 LLM の強みと弱みを定量的に分析するためのツールです。

## 🎯 主要機能

### 1. 固定銘柄での LLM 予測精度検証

- 同一銘柄に対する複数 LLM の予測精度を比較
- 価格予測と実際の結果を定量評価

### 2. LLM 銘柄選定能力検証

- LLM の銘柄選定能力を期間別に検証
- 短期・中期の選定精度分析

### 3. 包括的な履歴分析・統計機能

- 過去の分析結果の統計的評価
- モデル別・期間別成果ランキング

## 🚀 起動方法

### Docker Compose

```bash
# 起動
docker compose up --build

# 停止
docker compose down
```

## 📈 分析指標

### 予測精度計算

```
予測精度(%) = 100 - |実際価格 - 予測価格| / 実際価格 × 100
```

### 騰落率計算

```
騰落率(%) = (売却価格 - 購入価格) / 購入価格 × 100
```

### 勝率計算

```
勝率(%) = 利益が出た回数 / 総シミュレーション回数 × 100
```

## 💡 活用シナリオ例

### シナリオ 1: LLM 予測精度比較

1. **固定銘柄分析**を選択
2. 複数の LLM に同一銘柄の株価を予測させる
3. 各予測をアプリに入力してシミュレーション実行
4. 予測精度ランキングで最優秀 LLM を特定

### シナリオ 2: 銘柄選定能力検証

1. **銘柄選定分析**で期間を選択
2. 各 LLM に銘柄選定させる
3. 選定された銘柄をシミュレーション
4. 統計分析で最適な LLM を特定

## 📂 ファイル構成

```
stock_simulator/
├── app.py                        # メインアプリケーション
├── modules/                      # モジュールディレクトリ
│   ├── stock_analyzer.py         # 株価分析機能
│   ├── data_manager.py           # データ管理機能
│   ├── ui_components.py          # UIコンポーネント
│   ├── history_analysis.py       # 履歴分析機能
│   └── chart_utils.py            # チャート生成ユーティリティ
├── requirements.txt              # Python依存ライブラリ
├── Dockerfile                    # Dockerイメージ設定
├── docker-compose.yml            # Docker Compose設定
├── run_docker.sh                 # Docker Compose起動スクリプト
├── stop_docker.sh                # Docker Compose停止スクリプト
├── run_docker_standalone.sh      # 単体Docker起動スクリプト
├── stop_docker_standalone.sh     # 単体Docker停止スクリプト
├── data/                         # データ保存ディレクトリ
│   ├── fixed_stock_analysis.csv       # 固定銘柄分析履歴
│   └── stock_selection_analysis.csv   # 銘柄選定分析履歴
└── README.md                     # このファイル
```

## 🔧 初回セットアップ

```bash
# スクリプトに実行権限を付与
chmod +x *.sh

# データディレクトリの初期化（自動実行されます）
mkdir -p data
```

## 🛠️ トラブルシューティング

### ポート 8501 が使用中の場合

```bash
# 使用中のプロセスを確認
lsof -i :8501

# 別のポートで起動
docker run -d --name llm-stock-analyzer-container -p 8502:8501 -v "$(pwd)/data:/app/data" llm-stock-analyzer
```

### データが保存されない場合

```bash
# dataディレクトリの権限を確認
ls -la data/

# 権限を修正
chmod 755 data/
```

### Docker 関連の問題

```bash
# コンテナとイメージを全削除
docker rm -f llm-stock-analyzer-container
docker rmi llm-stock-analyzer

# 再ビルド・再起動
docker build -t llm-stock-analyzer .
docker run -d --name llm-stock-analyzer-container -p 8501:8501 -v "$(pwd)/data:/app/data" llm-stock-analyzer
```

## ⚠️ 注意事項

- このツールは検証目的であり、実際の投資判断には使用しないでください
- 株価データは yfinance から取得するため、インターネット接続が必要です
- 実際の取引手数料や税金は考慮されていません
- 過去のパフォーマンスは将来の結果を保証するものではありません

## 📝 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

---

**⚠️ 投資に関する免責事項**

このツールは教育・研究目的で作成されており、実際の投資助言を提供するものではありません。投資判断は自己責任で行ってください。
