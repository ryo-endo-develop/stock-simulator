import os
from typing import Dict

import pandas as pd
import streamlit as st

# データ保存ディレクトリの作成
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

FIXED_STOCK_FILE = os.path.join(DATA_DIR, "fixed_stock_analysis.csv")
STOCK_SELECTION_FILE = os.path.join(DATA_DIR, "stock_selection_analysis.csv")


class DataManager:
    """データ管理クラス"""

    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """CSVファイルからデータを読み込み"""
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                if "execution_date" in df.columns:
                    df["execution_date"] = pd.to_datetime(df["execution_date"])
                return df
            except Exception as e:
                st.error(f"データ読み込みエラー: {str(e)}")
                return pd.DataFrame()
        return pd.DataFrame()

    @staticmethod
    def save_fixed_stock_analysis(data: Dict) -> bool:
        """固定銘柄分析データを保存"""
        try:
            # 既存データを読み込み
            df = DataManager.load_data(FIXED_STOCK_FILE)

            # 新しいデータを追加
            new_row = pd.DataFrame([data])
            if not df.empty:
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row

            # CSVに保存
            df.to_csv(FIXED_STOCK_FILE, index=False, encoding="utf-8-sig")
            return True
        except Exception as e:
            st.error(f"データ保存エラー: {str(e)}")
            return False

    @staticmethod
    def save_stock_selection_analysis(data: Dict) -> bool:
        """銘柄選定分析データを保存"""
        try:
            # 既存データを読み込み
            df = DataManager.load_data(STOCK_SELECTION_FILE)

            # 新しいデータを追加
            new_row = pd.DataFrame([data])
            if not df.empty:
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row

            # CSVに保存
            df.to_csv(STOCK_SELECTION_FILE, index=False, encoding="utf-8-sig")
            return True
        except Exception as e:
            st.error(f"データ保存エラー: {str(e)}")
            return False

    @staticmethod
    def delete_record(file_path: str, index: int) -> bool:
        """レコードを削除"""
        try:
            df = DataManager.load_data(file_path)
            if not df.empty and 0 <= index < len(df):
                df = df.drop(index=index).reset_index(drop=True)
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
                return True
            return False
        except Exception as e:
            st.error(f"データ削除エラー: {str(e)}")
            return False

    @staticmethod
    def export_data(df: pd.DataFrame, filename: str) -> bool:
        """データをエクスポート"""
        try:
            export_path = os.path.join(DATA_DIR, f"export_{filename}")
            df.to_csv(export_path, index=False, encoding="utf-8-sig")
            return True
        except Exception as e:
            st.error(f"エクスポートエラー: {str(e)}")
            return False

    @staticmethod
    def get_file_paths():
        """ファイルパスを取得"""
        return {
            "fixed_stock": FIXED_STOCK_FILE,
            "stock_selection": STOCK_SELECTION_FILE,
        }
