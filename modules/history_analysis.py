import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.data_manager import DataManager


def show_history_tabs(fixed_df, selection_df):
    """履歴分析のタブを表示"""
    # タブで分析を分ける
    tab1, tab2, tab3 = st.tabs(
        ["🎯 固定銘柄分析履歴", "📈 銘柄選定分析履歴", "🏆 総合統計"]
    )

    with tab1:
        if not fixed_df.empty:
            show_fixed_stock_history(fixed_df)
        else:
            st.info("固定銘柄分析の履歴がありません。")

    with tab2:
        if not selection_df.empty:
            show_stock_selection_history(selection_df)
        else:
            st.info("銘柄選定分析の履歴がありません。")

    with tab3:
        if not fixed_df.empty or not selection_df.empty:
            show_comprehensive_stats(fixed_df, selection_df)
        else:
            st.info("分析履歴がありません。")


def show_fixed_stock_history(df):
    """固定銘柄分析履歴を表示"""
    st.subheader("🎯 固定銘柄分析履歴")

    # フィルタリング機能
    with st.expander("🔍 フィルター設定"):
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            models = ["全て"] + list(df["model_id"].unique())
            selected_model = st.selectbox("LLMモデル", models, key="fixed_model")

        with filter_col2:
            stocks = ["全て"] + list(df["stock_code"].unique())
            selected_stock = st.selectbox("銘柄", stocks, key="fixed_stock")

        with filter_col3:
            min_accuracy = st.slider("最小予測精度(%)", 0, 100, 0, key="fixed_accuracy")

    # フィルタリング適用
    filtered_df = df.copy()
    if selected_model != "全て":
        filtered_df = filtered_df[filtered_df["model_id"] == selected_model]
    if selected_stock != "全て":
        filtered_df = filtered_df[filtered_df["stock_code"] == selected_stock]
    if min_accuracy > 0:
        filtered_df = filtered_df[filtered_df["prediction_accuracy"] >= min_accuracy]

    if filtered_df.empty:
        st.warning("フィルター条件に該当するデータがありません。")
        return

    # 統計サマリー
    _show_fixed_stock_summary(filtered_df)

    # データテーブル
    _show_fixed_stock_table(filtered_df)

    # チャート分析
    if len(filtered_df) > 1:
        _show_fixed_stock_charts(filtered_df)


def _show_fixed_stock_summary(filtered_df):
    """固定銘柄分析の統計サマリーを表示"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        win_rate = (filtered_df["return_rate"] > 0).mean() * 100
        st.metric("勝率", f"{win_rate:.1f}%")

    with col2:
        avg_return = filtered_df["return_rate"].mean()
        st.metric("平均騰落率", f"{avg_return:+.2f}%")

    with col3:
        avg_accuracy = filtered_df["prediction_accuracy"].mean()
        st.metric("平均予測精度", f"{avg_accuracy:.1f}%")

    with col4:
        total_profit = filtered_df["profit_loss"].sum()
        st.metric("累計損益", f"¥{total_profit:,.2f}")


def _show_fixed_stock_table(filtered_df):
    """固定銘柄分析のデータテーブルを表示"""
    st.subheader("📋 詳細データ")

    # 表示用のデータフレームを準備
    display_df = filtered_df.copy()
    display_df["execution_date"] = pd.to_datetime(
        display_df["execution_date"]
    ).dt.strftime("%Y-%m-%d %H:%M")
    display_df["profit_loss"] = display_df["profit_loss"].apply(lambda x: f"¥{x:,.2f}")
    display_df["return_rate"] = display_df["return_rate"].apply(lambda x: f"{x:+.2f}%")
    display_df["prediction_accuracy"] = display_df["prediction_accuracy"].apply(
        lambda x: f"{x:.1f}%"
    )

    # 列名を日本語に変更
    column_mapping = {
        "execution_date": "実行日時",
        "model_id": "LLMモデル",
        "stock_code": "銘柄コード",
        "buy_date": "購入日",
        "buy_price": "購入価格",
        "sell_date": "売却日",
        "sell_price": "売却価格",
        "predicted_price": "予測価格",
        "profit_loss": "総損益",
        "return_rate": "騰落率",
        "prediction_accuracy": "予測精度",
        "period_days": "期間(日)",
        "notes": "備考",
    }

    display_df = display_df.rename(columns=column_mapping)
    st.dataframe(display_df, use_container_width=True)


def _show_fixed_stock_charts(filtered_df):
    """固定銘柄分析のチャートを表示"""
    st.subheader("📊 グラフ分析")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # モデル別パフォーマンス
        model_stats = (
            filtered_df.groupby("model_id")
            .agg({"return_rate": "mean", "prediction_accuracy": "mean"})
            .reset_index()
        )

        fig = px.scatter(
            model_stats,
            x="prediction_accuracy",
            y="return_rate",
            text="model_id",
            title="モデル別：予測精度 vs 平均騰落率",
            labels={
                "prediction_accuracy": "平均予測精度(%)",
                "return_rate": "平均騰落率(%)",
            },
        )
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        # 時系列パフォーマンス
        time_df = filtered_df.copy()
        time_df["execution_date"] = pd.to_datetime(time_df["execution_date"])
        time_df = time_df.sort_values("execution_date")
        time_df["cumulative_return"] = time_df["return_rate"].cumsum()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time_df["execution_date"],
                y=time_df["cumulative_return"],
                mode="lines+markers",
                name="累積騰落率",
            )
        )
        fig.update_layout(
            title="時系列パフォーマンス（累積騰落率）",
            xaxis_title="実行日",
            yaxis_title="累積騰落率(%)",
        )
        st.plotly_chart(fig, use_container_width=True)


def show_stock_selection_history(df):
    """銘柄選定分析履歴を表示"""
    st.subheader("📈 銘柄選定分析履歴")

    # フィルタリング機能
    with st.expander("🔍 フィルター設定"):
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            models = ["全て"] + list(df["model_id"].unique())
            selected_model = st.selectbox("LLMモデル", models, key="selection_model")

        with filter_col2:
            periods = ["全て"] + list(df["analysis_period"].unique())
            selected_period = st.selectbox("分析期間", periods, key="selection_period")

        with filter_col3:
            profit_only = st.checkbox("利益のみ表示", key="selection_profit")

    # フィルタリング適用
    filtered_df = df.copy()
    if selected_model != "全て":
        filtered_df = filtered_df[filtered_df["model_id"] == selected_model]
    if selected_period != "全て":
        filtered_df = filtered_df[filtered_df["analysis_period"] == selected_period]
    if profit_only:
        filtered_df = filtered_df[filtered_df["return_rate"] > 0]

    if filtered_df.empty:
        st.warning("フィルター条件に該当するデータがありません。")
        return

    # 統計サマリー
    _show_selection_summary(filtered_df)

    # データテーブル
    _show_selection_table(filtered_df)

    # 期間別パフォーマンス分析
    if len(filtered_df) > 1:
        _show_selection_charts(filtered_df)


def _show_selection_summary(filtered_df):
    """銘柄選定分析の統計サマリーを表示"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        win_rate = (filtered_df["return_rate"] > 0).mean() * 100
        st.metric("勝率", f"{win_rate:.1f}%")

    with col2:
        avg_return = filtered_df["return_rate"].mean()
        st.metric("平均騰落率", f"{avg_return:+.2f}%")

    with col3:
        total_profit = filtered_df["profit_loss"].sum()
        st.metric("累計損益", f"¥{total_profit:,.2f}")

    with col4:
        avg_period = filtered_df["period_days"].mean()
        st.metric("平均保有期間", f"{avg_period:.0f}日")


def _show_selection_table(filtered_df):
    """銘柄選定分析のデータテーブルを表示"""
    st.subheader("📋 詳細データ")

    # 表示用のデータフレームを準備
    display_df = filtered_df.copy()
    display_df["execution_date"] = pd.to_datetime(
        display_df["execution_date"]
    ).dt.strftime("%Y-%m-%d %H:%M")
    display_df["profit_loss"] = display_df["profit_loss"].apply(lambda x: f"¥{x:,.2f}")
    display_df["return_rate"] = display_df["return_rate"].apply(lambda x: f"{x:+.2f}%")

    # 列名を日本語に変更
    column_mapping = {
        "execution_date": "実行日時",
        "analysis_period": "分析期間",
        "model_id": "LLMモデル",
        "stock_code": "銘柄コード",
        "selection_reason": "選定理由",
        "buy_date": "購入日",
        "buy_price": "購入価格",
        "sell_date": "売却日",
        "sell_price": "売却価格",
        "profit_loss": "総損益",
        "return_rate": "騰落率",
        "period_days": "期間(日)",
        "notes": "備考",
    }

    display_df = display_df.rename(columns=column_mapping)
    st.dataframe(display_df, use_container_width=True)


def _show_selection_charts(filtered_df):
    """銘柄選定分析のチャートを表示"""
    st.subheader("📊 期間別パフォーマンス分析")

    period_stats = (
        filtered_df.groupby("analysis_period")
        .agg({"return_rate": ["mean", "count"], "profit_loss": "sum"})
        .reset_index()
    )

    period_stats.columns = ["analysis_period", "avg_return", "count", "total_profit"]
    period_stats["win_rate"] = (
        filtered_df.groupby("analysis_period")["return_rate"]
        .apply(lambda x: (x > 0).mean() * 100)
        .values
    )

    fig = px.bar(
        period_stats,
        x="analysis_period",
        y="avg_return",
        title="期間別平均騰落率",
        labels={"analysis_period": "分析期間", "avg_return": "平均騰落率(%)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def show_comprehensive_stats(fixed_df, selection_df):
    """総合統計を表示"""
    st.subheader("🏆 総合統計分析")

    # 全体サマリー
    _show_overall_summary(fixed_df, selection_df)

    # モデル別ランキング
    if not fixed_df.empty or not selection_df.empty:
        _show_model_rankings(fixed_df, selection_df)

    # データエクスポート機能
    _show_export_options(fixed_df, selection_df)


def _show_overall_summary(fixed_df, selection_df):
    """全体サマリーを表示"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_analyses = len(fixed_df) + len(selection_df)
        st.metric("総分析回数", total_analyses)

    with col2:
        # 全体勝率
        all_returns = []
        if not fixed_df.empty:
            all_returns.extend(fixed_df["return_rate"].tolist())
        if not selection_df.empty:
            all_returns.extend(selection_df["return_rate"].tolist())

        if all_returns:
            overall_win_rate = (
                sum(1 for r in all_returns if r > 0) / len(all_returns) * 100
            )
            st.metric("全体勝率", f"{overall_win_rate:.1f}%")
        else:
            st.metric("全体勝率", "0.0%")

    with col3:
        # 全体平均騰落率
        if all_returns:
            avg_return = sum(all_returns) / len(all_returns)
            st.metric("全体平均騰落率", f"{avg_return:+.2f}%")
        else:
            st.metric("全体平均騰落率", "0.0%")

    with col4:
        # 累計損益
        total_profit = 0
        if not fixed_df.empty:
            total_profit += fixed_df["profit_loss"].sum()
        if not selection_df.empty:
            total_profit += selection_df["profit_loss"].sum()
        st.metric("累計損益", f"¥{total_profit:,.2f}")


def _show_model_rankings(fixed_df, selection_df):
    """モデル別ランキングを表示"""
    st.subheader("🥇 LLMモデル別ランキング")

    model_stats = []

    # 固定銘柄分析のモデル統計
    if not fixed_df.empty:
        for model in fixed_df["model_id"].unique():
            model_data = fixed_df[fixed_df["model_id"] == model]
            model_stats.append(
                {
                    "model_id": model,
                    "type": "固定銘柄",
                    "count": len(model_data),
                    "win_rate": (model_data["return_rate"] > 0).mean() * 100,
                    "avg_return": model_data["return_rate"].mean(),
                    "avg_accuracy": model_data["prediction_accuracy"].mean(),
                    "total_profit": model_data["profit_loss"].sum(),
                }
            )

    # 銘柄選定分析のモデル統計
    if not selection_df.empty:
        for model in selection_df["model_id"].unique():
            model_data = selection_df[selection_df["model_id"] == model]
            model_stats.append(
                {
                    "model_id": model,
                    "type": "銘柄選定",
                    "count": len(model_data),
                    "win_rate": (model_data["return_rate"] > 0).mean() * 100,
                    "avg_return": model_data["return_rate"].mean(),
                    "avg_accuracy": None,  # 銘柄選定では予測精度なし
                    "total_profit": model_data["profit_loss"].sum(),
                }
            )

    if model_stats:
        model_df = pd.DataFrame(model_stats)

        # ランキング表示
        ranking_col1, ranking_col2 = st.columns(2)

        with ranking_col1:
            st.markdown("**勝率ランキング**")
            win_ranking = model_df.sort_values("win_rate", ascending=False).head(10)
            for idx, row in win_ranking.iterrows():
                accuracy_text = (
                    f" | 精度: {row['avg_accuracy']:.1f}%"
                    if row["avg_accuracy"] is not None
                    else ""
                )
                st.text(
                    f"{row['model_id']} ({row['type']}): {row['win_rate']:.1f}%{accuracy_text}"
                )

        with ranking_col2:
            st.markdown("**平均騰落率ランキング**")
            return_ranking = model_df.sort_values("avg_return", ascending=False).head(
                10
            )
            for idx, row in return_ranking.iterrows():
                st.text(f"{row['model_id']} ({row['type']}): {row['avg_return']:+.2f}%")

    # モデル比較チャート
    if len(model_df) > 1:
        st.subheader("📊 モデル比較チャート")

        fig = px.scatter(
            model_df,
            x="win_rate",
            y="avg_return",
            color="type",
            size="count",
            hover_data=["model_id", "total_profit"],
            title="LLMモデル比較：勝率 vs 平均騰落率",
            labels={"win_rate": "勝率(%)", "avg_return": "平均騰落率(%)"},
        )
        st.plotly_chart(fig, use_container_width=True)


def _show_export_options(fixed_df, selection_df):
    """データエクスポート機能を表示"""
    st.subheader("💾 データエクスポート")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        if st.button("固定銘柄分析データをエクスポート") and not fixed_df.empty:
            if DataManager.export_data(fixed_df, "fixed_stock_analysis.csv"):
                st.success("✅ 固定銘柄分析データをエクスポートしました")

    with export_col2:
        if st.button("銘柄選定分析データをエクスポート") and not selection_df.empty:
            if DataManager.export_data(selection_df, "stock_selection_analysis.csv"):
                st.success("✅ 銘柄選定分析データをエクスポートしました")
