import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ChartGenerator:
    """チャート生成クラス"""

    @staticmethod
    def create_stock_price_chart(
        chart_data, stock_code, buy_date, sell_date, buy_price, sell_price, period_name
    ):
        """株価チャートを作成"""
        if chart_data is None or chart_data.empty:
            return None

        fig = go.Figure()

        # 株価ライン
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["Close"],
                mode="lines",
                name="株価",
                line=dict(color="blue", width=2),
            )
        )

        # 購入ポイント
        fig.add_trace(
            go.Scatter(
                x=[buy_date],
                y=[buy_price],
                mode="markers",
                name=f"購入 (¥{buy_price:,.2f})",
                marker=dict(color="green", size=12, symbol="triangle-up"),
            )
        )

        # 売却ポイント
        fig.add_trace(
            go.Scatter(
                x=[sell_date],
                y=[sell_price],
                mode="markers",
                name=f"売却 (¥{sell_price:,.2f})",
                marker=dict(color="red", size=12, symbol="triangle-down"),
            )
        )

        fig.update_layout(
            title=f"{stock_code} 株価チャート ({period_name})",
            xaxis_title="日付",
            yaxis_title="株価 (円)",
            hovermode="x unified",
            height=400,
        )

        return fig

    @staticmethod
    def create_model_performance_scatter(model_stats):
        """モデルパフォーマンス散布図を作成"""
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
        return fig

    @staticmethod
    def create_cumulative_return_chart(time_df):
        """累積リターンチャートを作成"""
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
        return fig

    @staticmethod
    def create_period_performance_bar(period_stats):
        """期間別パフォーマンス棒グラフを作成"""
        fig = px.bar(
            period_stats,
            x="analysis_period",
            y="avg_return",
            title="期間別平均騰落率",
            labels={"analysis_period": "分析期間", "avg_return": "平均騰落率(%)"},
        )
        return fig

    @staticmethod
    def create_model_comparison_scatter(model_df):
        """モデル比較散布図を作成"""
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
        return fig


class DataFormatter:
    """データフォーマット用クラス"""

    @staticmethod
    def format_currency(value):
        """通貨フォーマット"""
        return f"¥{value:,.2f}"

    @staticmethod
    def format_percentage(value):
        """パーセンテージフォーマット"""
        return f"{value:+.2f}%"

    @staticmethod
    def format_accuracy(value):
        """精度フォーマット"""
        return f"{value:.1f}%"

    @staticmethod
    def format_datetime(dt):
        """日時フォーマット"""
        return pd.to_datetime(dt).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def prepare_display_dataframe(df, column_mapping, format_rules):
        """表示用データフレームを準備"""
        display_df = df.copy()

        # フォーマット適用
        for column, formatter in format_rules.items():
            if column in display_df.columns:
                display_df[column] = display_df[column].apply(formatter)

        # 列名変更
        display_df = display_df.rename(columns=column_mapping)

        return display_df
