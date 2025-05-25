from datetime import datetime, timedelta

import plotly.graph_objects as go
import streamlit as st

from modules.data_manager import DataManager
from modules.stock_analyzer import StockAnalyzer


def show_main_page():
    """メインページを表示"""
    st.title("🤖 LLM投資アイデア検証ツール")
    st.markdown("---")

    # 概要説明
    with st.expander("📋 ツール概要", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🎯 主要機能
            
            **1. 固定銘柄でのLLM予測精度検証**
            - 同一銘柄に対する複数LLMの予測精度を比較
            - 価格予測と実際の結果を定量評価
            
            **2. LLM銘柄選定能力検証**
            - LLMの銘柄選定能力を期間別に検証
            - 短期・中期の選定精度分析
            
            **3. 包括的な履歴分析・統計機能**
            - 過去の分析結果の統計的評価
            - モデル別・期間別成果ランキング
            """)

        with col2:
            st.markdown("""
            ### 📊 分析指標
            
            **予測精度**
            ```
            予測精度(%) = 100 - |実際価格 - 予測価格| / 実際価格 × 100
            ```
            
            **騰落率**
            ```
            騰落率(%) = (売却価格 - 購入価格) / 購入価格 × 100
            ```
            
            **勝率**
            ```
            勝率(%) = 利益が出た回数 / 総回数 × 100
            ```
            """)

    # 使用方法
    with st.expander("🚀 使用方法"):
        st.markdown("""
        ### 基本的な流れ
        
        1. **サイドバーから分析タイプを選択**
           - 固定銘柄分析：特定銘柄でのLLM予測精度を検証
           - 銘柄選定分析：LLMの銘柄選定能力を検証
           - 履歴分析：過去の分析結果を統計的に評価
        
        2. **必要な情報を入力**
           - LLMモデル名、銘柄コード、予測価格など
           - 購入日・売却日を指定
        
        3. **シミュレーション実行**
           - 自動で株価データを取得
           - 損益・騰落率・予測精度を自動計算
        
        4. **結果の確認・保存**
           - 結果を確認してデータベースに保存
           - 履歴分析で統計情報を確認
        """)

    # 注意事項
    with st.expander("⚠️ 注意事項"):
        st.warning("""
        - このツールは検証目的であり、実際の投資判断には使用しないでください
        - 株価データはyfinanceから取得するため、インターネット接続が必要です
        - 指定日が市場休場日の場合、直後の営業日のデータを使用します
        - 実際の取引手数料や税金は考慮されていません
        - 過去のパフォーマンスは将来の結果を保証するものではありません
        """)

    # 最近の分析サマリー
    st.markdown("---")
    st.subheader("📈 最近の分析サマリー")

    # データ読み込み（SQLiteデータベースから）
    fixed_df = DataManager.load_fixed_stock_data()
    selection_df = DataManager.load_stock_selection_data()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_analyses = len(fixed_df) + len(selection_df)
        st.metric("総分析回数", total_analyses)

    with col2:
        if not fixed_df.empty or not selection_df.empty:
            # 勝率計算
            all_returns = []
            if not fixed_df.empty:
                all_returns.extend(fixed_df["return_rate"].tolist())
            if not selection_df.empty:
                all_returns.extend(selection_df["return_rate"].tolist())

            if all_returns:
                win_rate = sum(1 for r in all_returns if r > 0) / len(all_returns) * 100
                st.metric("全体勝率", f"{win_rate:.1f}%")
            else:
                st.metric("全体勝率", "0.0%")
        else:
            st.metric("全体勝率", "0.0%")

    with col3:
        if not fixed_df.empty:
            avg_accuracy = fixed_df["prediction_accuracy"].mean()
            st.metric("平均予測精度", f"{avg_accuracy:.1f}%")
        else:
            st.metric("平均予測精度", "0.0%")

    with col4:
        if not fixed_df.empty or not selection_df.empty:
            unique_models = set()
            if not fixed_df.empty:
                unique_models.update(fixed_df["model_id"].unique())
            if not selection_df.empty:
                unique_models.update(selection_df["model_id"].unique())
            st.metric("分析LLMモデル数", len(unique_models))
        else:
            st.metric("分析LLMモデル数", 0)


def show_fixed_stock_analysis():
    """固定銘柄分析ページ"""
    st.title("📊 固定銘柄でのLLM予測精度検証")
    st.markdown("同一銘柄に対する複数LLMの予測精度を比較分析します。")
    st.markdown("---")

    # セッション状態の初期化
    if "fixed_stock_saved" not in st.session_state:
        st.session_state.fixed_stock_saved = False

    # 保存成功後のメッセージ表示
    if st.session_state.fixed_stock_saved:
        st.success(
            "✅ 前回のデータが正常に保存されました！履歴分析ページで確認できます。"
        )
        st.session_state.fixed_stock_saved = False

    # 入力フォーム
    with st.form("fixed_stock_form"):
        col1, col2 = st.columns(2)

        with col1:
            model_id = st.text_input(
                "🤖 LLMモデル名",
                placeholder="例: ChatGPT-4, Gemini-Pro, Claude-3",
                help="分析するLLMモデル名を入力してください",
            )

            stock_code = st.text_input(
                "📈 銘柄コード",
                placeholder="例: 7203 (トヨタ), 6758 (ソニー)",
                help="4桁の銘柄コードを入力してください",
            )

            predicted_price = st.number_input(
                "🔮 LLM予測価格 (円)",
                min_value=0.0,
                step=0.01,
                help="LLMが予測した株価を入力してください",
            )

        with col2:
            buy_date = st.date_input(
                "📅 購入日", value=datetime.now().date(), help="株式を購入した日付"
            )

            sell_date = st.date_input(
                "📅 売却日",
                value=datetime.now().date() + timedelta(days=30),
                help="株式を売却した（する予定の）日付",
            )

            notes = st.text_area(
                "📝 備考",
                placeholder="LLMの予測根拠や特記事項があれば記入してください",
                help="オプション：追加情報があれば記入",
            )

        submitted = st.form_submit_button("🚀 シミュレーション実行", type="primary")

    if submitted:
        _process_fixed_stock_simulation(
            model_id, stock_code, predicted_price, buy_date, sell_date, notes
        )


def _process_fixed_stock_simulation(
    model_id, stock_code, predicted_price, buy_date, sell_date, notes
):
    """固定銘柄分析のシミュレーション処理"""
    # バリデーション
    if not all([model_id, stock_code, predicted_price > 0]):
        st.error("必須項目を全て入力してください。")
        return

    if buy_date >= sell_date:
        st.error("売却日は購入日より後の日付を選択してください。")
        return

    # 株価データ取得と計算
    with st.spinner("株価データを取得中..."):
        buy_price, actual_buy_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, buy_date.strftime("%Y-%m-%d")
        )
        sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, sell_date.strftime("%Y-%m-%d")
        )

    if buy_price is None or sell_price is None:
        st.error("株価データの取得に失敗しました。銘柄コードを確認してください。")
        return

    # 計算実行
    profit_loss = sell_price - buy_price
    return_rate = StockAnalyzer.calculate_return_rate(buy_price, sell_price)
    prediction_accuracy = StockAnalyzer.calculate_prediction_accuracy(
        sell_price, predicted_price
    )
    period_days = (sell_date - buy_date).days

    # 結果表示
    st.success("✅ シミュレーション完了！")

    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 総損益", f"¥{profit_loss:,.2f}", delta=f"{return_rate:+.2f}%")

    with col2:
        st.metric(
            "📊 騰落率",
            f"{return_rate:+.2f}%",
            delta="利益" if return_rate > 0 else "損失",
        )

    with col3:
        st.metric(
            "🎯 予測精度",
            f"{prediction_accuracy:.2f}%",
            delta="高精度" if prediction_accuracy > 80 else "要改善",
        )

    with col4:
        st.metric(
            "📅 保有期間",
            f"{period_days}日",
            delta=f"実際: {(datetime.strptime(actual_sell_date, '%Y-%m-%d') - datetime.strptime(actual_buy_date, '%Y-%m-%d')).days}日",
        )

    # 詳細情報
    with st.expander("📋 詳細情報", expanded=True):
        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            st.markdown(f"""
            **📈 株価情報**
            - 購入価格: ¥{buy_price:,.2f} ({actual_buy_date})
            - 売却価格: ¥{sell_price:,.2f} ({actual_sell_date})
            - LLM予測価格: ¥{predicted_price:,.2f}
            - 予測誤差: ¥{abs(sell_price - predicted_price):,.2f}
            """)

        with detail_col2:
            st.markdown(f"""
            **🤖 LLM分析情報**
            - モデル: {model_id}
            - 銘柄: {stock_code}
            - 分析期間: {period_days}日間
            - 予測精度: {prediction_accuracy:.2f}%
            """)

    # 保存確認
    if st.button("💾 結果を保存", type="primary", key="save_fixed_stock"):
        save_data = {
            "execution_date": datetime.now(),
            "model_id": model_id,
            "stock_code": stock_code,
            "buy_date": actual_buy_date,
            "buy_price": buy_price,
            "sell_date": actual_sell_date,
            "sell_price": sell_price,
            "predicted_price": predicted_price,
            "profit_loss": profit_loss,
            "return_rate": return_rate,
            "prediction_accuracy": prediction_accuracy,
            "period_days": period_days,
            "notes": notes,
        }

        if DataManager.save_fixed_stock_analysis(save_data):
            st.session_state.fixed_stock_saved = True
            st.rerun()  # ページを再読み込み
        else:
            st.error("❌ データの保存に失敗しました。")


def show_stock_selection_analysis():
    """銘柄選定分析ページ"""
    st.title("🎯 LLM銘柄選定能力検証")
    st.markdown("LLMの銘柄選定能力を期間別に検証・分析します。")
    st.markdown("---")

    # セッション状態の初期化
    if "stock_selection_saved" not in st.session_state:
        st.session_state.stock_selection_saved = False

    # 保存成功後のメッセージ表示
    if st.session_state.stock_selection_saved:
        st.success(
            "✅ 前回のデータが正常に保存されました！履歴分析ページで確認できます。"
        )
        st.session_state.stock_selection_saved = False

    # 入力フォーム
    with st.form("stock_selection_form"):
        col1, col2 = st.columns(2)

        with col1:
            analysis_period = st.selectbox(
                "📊 分析期間",
                ["1週間", "1ヶ月", "3ヶ月", "6ヶ月", "1年"],
                help="LLMの銘柄選定を検証する期間を選択",
            )

            model_id = st.text_input(
                "🤖 LLMモデル名",
                placeholder="例: ChatGPT-4, Gemini-Pro, Claude-3",
                help="分析するLLMモデル名を入力してください",
            )

            stock_code = st.text_input(
                "📈 選定銘柄コード",
                placeholder="例: 7203 (トヨタ), 6758 (ソニー)",
                help="LLMが選定した銘柄コードを入力してください",
            )

        with col2:
            selection_reason = st.text_area(
                "💡 LLM選定理由",
                placeholder="LLMが提示した選定理由を入力してください",
                help="LLMがこの銘柄を選んだ理由・根拠",
                height=100,
            )

            buy_date = st.date_input(
                "📅 購入日", value=datetime.now().date(), help="株式を購入した日付"
            )

            notes = st.text_area(
                "📝 備考",
                placeholder="追加の特記事項があれば記入してください",
                help="オプション：追加情報があれば記入",
            )

        submitted = st.form_submit_button("🚀 シミュレーション実行", type="primary")

    if submitted:
        _process_stock_selection_simulation(
            analysis_period, model_id, stock_code, selection_reason, buy_date, notes
        )


def _process_stock_selection_simulation(
    analysis_period, model_id, stock_code, selection_reason, buy_date, notes
):
    """銘柄選定分析のシミュレーション処理"""
    # バリデーション
    if not all([analysis_period, model_id, stock_code, selection_reason]):
        st.error("必須項目を全て入力してください。")
        return

    # 売却日を分析期間から自動計算
    period_mapping = {"1週間": 7, "1ヶ月": 30, "3ヶ月": 90, "6ヶ月": 180, "1年": 365}

    sell_date = buy_date + timedelta(days=period_mapping[analysis_period])

    # 株価データ取得と計算
    with st.spinner("株価データを取得中..."):
        buy_price, actual_buy_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, buy_date.strftime("%Y-%m-%d")
        )
        sell_price, actual_sell_date = StockAnalyzer.get_closest_business_day_price(
            stock_code, sell_date.strftime("%Y-%m-%d")
        )

    if buy_price is None or sell_price is None:
        st.error("株価データの取得に失敗しました。銘柄コードを確認してください。")
        return

    # 計算実行
    profit_loss = sell_price - buy_price
    return_rate = StockAnalyzer.calculate_return_rate(buy_price, sell_price)
    actual_period_days = (
        datetime.strptime(actual_sell_date, "%Y-%m-%d")
        - datetime.strptime(actual_buy_date, "%Y-%m-%d")
    ).days

    # 結果表示
    st.success("✅ シミュレーション完了！")

    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 総損益", f"¥{profit_loss:,.2f}", delta=f"{return_rate:+.2f}%")

    with col2:
        st.metric(
            "📊 騰落率",
            f"{return_rate:+.2f}%",
            delta="✅ 成功" if return_rate > 0 else "❌ 失敗",
        )

    with col3:
        st.metric("📅 分析期間", analysis_period, delta=f"実際: {actual_period_days}日")

    with col4:
        success_rate = "100%" if return_rate > 0 else "0%"
        st.metric(
            "🎯 選定成功",
            success_rate,
            delta="利益獲得" if return_rate > 0 else "損失発生",
        )

    # 詳細情報
    with st.expander("📋 詳細分析結果", expanded=True):
        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            st.markdown(f"""
            **📈 株価・収益情報**
            - 購入価格: ¥{buy_price:,.2f} ({actual_buy_date})
            - 売却価格: ¥{sell_price:,.2f} ({actual_sell_date})
            - 総損益: ¥{profit_loss:,.2f}
            - 騰落率: {return_rate:+.2f}%
            - 実際の保有期間: {actual_period_days}日
            """)

        with detail_col2:
            st.markdown(f"""
            **🤖 LLM選定情報**
            - モデル: {model_id}
            - 選定銘柄: {stock_code}
            - 分析期間設定: {analysis_period}
            - 選定成功: {"✅ 成功" if return_rate > 0 else "❌ 失敗"}
            """)

        st.markdown("**💡 LLM選定理由:**")
        st.info(selection_reason)

    # 株価チャート表示
    _show_stock_chart(
        stock_code,
        actual_buy_date,
        actual_sell_date,
        buy_price,
        sell_price,
        analysis_period,
    )

    # 保存確認
    if st.button("💾 結果を保存", type="primary", key="save_stock_selection"):
        save_data = {
            "execution_date": datetime.now(),
            "analysis_period": analysis_period,
            "model_id": model_id,
            "stock_code": stock_code,
            "selection_reason": selection_reason,
            "buy_date": actual_buy_date,
            "buy_price": buy_price,
            "sell_date": actual_sell_date,
            "sell_price": sell_price,
            "profit_loss": profit_loss,
            "return_rate": return_rate,
            "period_days": actual_period_days,
            "notes": notes,
        }

        if DataManager.save_stock_selection_analysis(save_data):
            st.session_state.stock_selection_saved = True
            st.rerun()  # ページを再読み込み
        else:
            st.error("❌ データの保存に失敗しました。")


def _show_stock_chart(
    stock_code,
    actual_buy_date,
    actual_sell_date,
    buy_price,
    sell_price,
    analysis_period,
):
    """株価チャートを表示"""
    with st.spinner("株価チャートを生成中..."):
        chart_start = (
            datetime.strptime(actual_buy_date, "%Y-%m-%d") - timedelta(days=30)
        ).strftime("%Y-%m-%d")
        chart_end = (
            datetime.strptime(actual_sell_date, "%Y-%m-%d") + timedelta(days=10)
        ).strftime("%Y-%m-%d")
        chart_data = StockAnalyzer.get_stock_data(stock_code, chart_start, chart_end)

        if chart_data is not None and not chart_data.empty:
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=chart_data.index,
                    y=chart_data["Close"],
                    mode="lines",
                    name="株価",
                    line=dict(color="blue", width=2),
                )
            )

            # 購入・売却ポイントをマーク
            fig.add_trace(
                go.Scatter(
                    x=[actual_buy_date],
                    y=[buy_price],
                    mode="markers",
                    name=f"購入 (¥{buy_price:,.2f})",
                    marker=dict(color="green", size=12, symbol="triangle-up"),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=[actual_sell_date],
                    y=[sell_price],
                    mode="markers",
                    name=f"売却 (¥{sell_price:,.2f})",
                    marker=dict(color="red", size=12, symbol="triangle-down"),
                )
            )

            fig.update_layout(
                title=f"{stock_code} 株価チャート ({analysis_period}間)",
                xaxis_title="日付",
                yaxis_title="株価 (円)",
                hovermode="x unified",
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)


def show_history_analysis():
    """履歴分析ページ"""
    st.title("📊 履歴分析・統計")
    st.markdown("過去の分析結果を統計的に評価し、LLMのパフォーマンスを比較します。")
    st.markdown("---")

    # データの強制再読み込みボタン
    if st.button("🔄 データを再読み込み", type="secondary"):
        st.cache_data.clear()
        st.rerun()

    # データ読み込み（SQLiteデータベースから）
    fixed_df = DataManager.load_fixed_stock_data()
    selection_df = DataManager.load_stock_selection_data()

    # デバッグ情報を表示
    if st.checkbox("🔍 デバッグ情報を表示", key="debug_info"):
        st.write("**データベース情報:**")
        debug_info = DataManager.get_debug_info()
        st.json(debug_info)

        st.write("**データ情報:**")
        st.write(f"固定銘柄分析データ数: {len(fixed_df)}")
        st.write(f"銘柄選定分析データ数: {len(selection_df)}")

        if not fixed_df.empty:
            st.write("**固定銘柄分析データ（最新5件）:**")
            st.dataframe(fixed_df.head())

        if not selection_df.empty:
            st.write("**銘柄選定分析データ（最新5件）:**")
            st.dataframe(selection_df.head())

        # データベース管理機能
        st.write("**データベース管理:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📤 CSVエクスポート"):
                DataManager.export_to_csv()
        with col2:
            if st.button("🧪 データベーステスト"):
                DataManager.test_database_connection()
        with col3:
            if st.button("🗑️ 全データ削除", type="secondary"):
                if st.button("本当に削除しますか？", type="secondary"):
                    DataManager.clear_all_data()

    if fixed_df.empty and selection_df.empty:
        st.warning(
            "📝 分析履歴がありません。まず他のページでシミュレーションを実行してください。"
        )
        return

    # 履歴分析モジュールをインポートして実行
    from modules.history_analysis import show_history_tabs

    show_history_tabs(fixed_df, selection_df)
