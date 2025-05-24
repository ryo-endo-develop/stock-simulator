from datetime import timedelta
from typing import Optional, Tuple

import pandas as pd
import streamlit as st
import yfinance as yf


class StockAnalyzer:
    """株価分析クラス"""

    @staticmethod
    def get_stock_data(
        symbol: str, start_date: str, end_date: str
    ) -> Optional[pd.DataFrame]:
        """株価データを取得"""
        try:
            # 日本株の場合は.Tを付加
            if not symbol.endswith(".T") and symbol.isdigit():
                symbol = f"{symbol}.T"

            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)

            if data.empty:
                return None

            # インデックスをタイムゾーンなしに変換
            if hasattr(data.index, "tz") and data.index.tz is not None:
                data.index = data.index.tz_localize(None)

            return data
        except Exception as e:
            st.error(f"株価データの取得に失敗しました: {str(e)}")
            return None

    @staticmethod
    def get_closest_business_day_price(
        symbol: str, target_date: str, days_range: int = 10
    ) -> Tuple[Optional[float], Optional[str]]:
        """指定日付に最も近い営業日の株価を取得"""
        try:
            # 文字列の日付をPandasのDatetimeに変換（タイムゾーンなし）
            target_dt = pd.to_datetime(target_date)
            if hasattr(target_dt, "tz") and target_dt.tz is not None:
                target_dt = target_dt.tz_localize(None)

            # 指定日から前後の範囲で株価データを取得
            start_dt = target_dt - timedelta(days=days_range)
            end_dt = target_dt + timedelta(days=days_range)

            start_date = start_dt.strftime("%Y-%m-%d")
            end_date = end_dt.strftime("%Y-%m-%d")

            data = StockAnalyzer.get_stock_data(symbol, start_date, end_date)
            if data is None or data.empty:
                return None, None

            # データのインデックスがタイムゾーンを持っている場合は削除
            if hasattr(data.index, "tz") and data.index.tz is not None:
                data.index = data.index.tz_localize(None)

            # 指定日付に最も近い日付を見つける
            time_diffs = [abs((idx - target_dt).days) for idx in data.index]
            min_diff_idx = time_diffs.index(min(time_diffs))
            closest_date = data.index[min_diff_idx]
            closest_price = data.iloc[min_diff_idx]["Close"]

            return float(closest_price), closest_date.strftime("%Y-%m-%d")
        except Exception as e:
            st.error(f"株価取得エラー: {str(e)}")
            return None, None

    @staticmethod
    def calculate_prediction_accuracy(
        actual_price: float, predicted_price: float
    ) -> float:
        """予測精度を計算"""
        if actual_price == 0:
            return 0.0
        accuracy = 100 - abs(actual_price - predicted_price) / actual_price * 100
        return max(0.0, accuracy)  # 0%未満にならないように調整

    @staticmethod
    def calculate_return_rate(buy_price: float, sell_price: float) -> float:
        """騰落率を計算"""
        if buy_price == 0:
            return 0.0
        return (sell_price - buy_price) / buy_price * 100

    @staticmethod
    def get_stock_info(symbol: str) -> Optional[dict]:
        """銘柄の基本情報を取得"""
        try:
            if not symbol.endswith(".T") and symbol.isdigit():
                symbol = f"{symbol}.T"

            stock = yf.Ticker(symbol)
            info = stock.info

            return {
                "name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "current_price": info.get("currentPrice", 0),
            }
        except Exception:
            return None
