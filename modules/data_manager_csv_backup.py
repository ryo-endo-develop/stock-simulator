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
    def initialize_csv_files():
        """CSVファイルを初期化（ファイルが存在しない場合のみ）"""
        # 固定銘柄分析CSVファイルの初期化
        if not os.path.exists(FIXED_STOCK_FILE):
            fixed_columns = [
                'execution_date', 'model_id', 'stock_code', 'buy_date', 'buy_price',
                'sell_date', 'sell_price', 'predicted_price', 'profit_loss',
                'return_rate', 'prediction_accuracy', 'period_days', 'notes'
            ]
            pd.DataFrame(columns=fixed_columns).to_csv(FIXED_STOCK_FILE, index=False, encoding='utf-8-sig')
            st.info(f"固定銘柄分析用CSVファイルを作成しました: {FIXED_STOCK_FILE}")
        
        # 銘柄選定分析CSVファイルの初期化
        if not os.path.exists(STOCK_SELECTION_FILE):
            selection_columns = [
                'execution_date', 'analysis_period', 'model_id', 'stock_code',
                'selection_reason', 'buy_date', 'buy_price', 'sell_date', 'sell_price',
                'profit_loss', 'return_rate', 'period_days', 'notes'
            ]
            pd.DataFrame(columns=selection_columns).to_csv(STOCK_SELECTION_FILE, index=False, encoding='utf-8-sig')
            st.info(f"銘柄選定分析用CSVファイルを作成しました: {STOCK_SELECTION_FILE}")

    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """CSVファイルからデータを読み込み"""
        # ファイルが存在しない場合のみ初期化
        if not os.path.exists(file_path):
            DataManager.initialize_csv_files()
        
        try:
            df = pd.read_csv(file_path)
            
            # 空のファイル（ヘッダーのみ）の場合は空のDataFrameを返す
            if len(df) == 0:
                return pd.DataFrame()
            
            # execution_dateカラムが存在し、値がある場合のみ変換
            if "execution_date" in df.columns and not df["execution_date"].isna().all():
                df["execution_date"] = pd.to_datetime(df["execution_date"])
            
            return df
        except Exception as e:
            st.error(f"データ読み込みエラー: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def save_fixed_stock_analysis(data: Dict) -> bool:
        """固定銘柄分析データを保存"""
        try:
            # ファイルが存在しない場合のみ初期化
            if not os.path.exists(FIXED_STOCK_FILE):
                DataManager.initialize_csv_files()
            
            # 既存データを読み込み
            try:
                df = pd.read_csv(FIXED_STOCK_FILE)
            except:
                df = pd.DataFrame()

            # 新しいデータを追加
            new_row = pd.DataFrame([data])
            if not df.empty:
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row

            # CSVに保存
            df.to_csv(FIXED_STOCK_FILE, index=False, encoding="utf-8-sig")
            
            # 保存確認
            saved_df = pd.read_csv(FIXED_STOCK_FILE)
            st.success(f"✅ 固定銘柄分析データを保存しました。（総データ数: {len(saved_df)}件）")
            
            return True
        except Exception as e:
            st.error(f"固定銘柄分析データ保存エラー: {str(e)}")
            return False

    @staticmethod
    def save_stock_selection_analysis(data: Dict) -> bool:
        """銘柄選定分析データを保存"""
        try:
            # デバッグ情報を表示
            st.write("🔍 保存処理開始...")
            st.write(f"保存データ: {data}")
            
            # ファイルが存在しない場合のみ初期化
            if not os.path.exists(STOCK_SELECTION_FILE):
                st.write("📁 CSVファイルが存在しないため、新規作成します...")
                DataManager.initialize_csv_files()
            
            # 既存データを読み込み
            try:
                df = pd.read_csv(STOCK_SELECTION_FILE)
                st.write(f"📖 既存データ読み込み完了。現在のデータ数: {len(df)}件")
            except Exception as read_error:
                st.write(f"⚠️ 既存データ読み込みエラー: {str(read_error)}")
                df = pd.DataFrame()

            # 新しいデータを追加
            new_row = pd.DataFrame([data])
            st.write(f"➕ 新しいデータを作成: {new_row}")
            
            if not df.empty:
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row
            
            st.write(f"📝 結合後のデータ数: {len(df)}件")

            # CSVに保存
            df.to_csv(STOCK_SELECTION_FILE, index=False, encoding="utf-8-sig")
            st.write(f"💾 CSVファイルに保存完了: {STOCK_SELECTION_FILE}")
            
            # 保存確認
            saved_df = pd.read_csv(STOCK_SELECTION_FILE)
            st.success(f"✅ 銘柄選定分析データを保存しました。（総データ数: {len(saved_df)}件）")
            
            # 保存されたデータの最後の行を表示
            if not saved_df.empty:
                st.write("📋 保存された最新データ:")
                st.dataframe(saved_df.tail(1))
            
            return True
        except Exception as e:
            st.error(f"銘柄選定分析データ保存エラー: {str(e)}")
            import traceback
            st.error(f"詳細エラー: {traceback.format_exc()}")
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

    @staticmethod
    def get_debug_info():
        """デバッグ情報を取得"""
        info = {
            "data_dir_exists": os.path.exists(DATA_DIR),
            "fixed_file_exists": os.path.exists(FIXED_STOCK_FILE),
            "selection_file_exists": os.path.exists(STOCK_SELECTION_FILE),
            "data_dir_path": os.path.abspath(DATA_DIR),
            "fixed_file_path": os.path.abspath(FIXED_STOCK_FILE),
            "selection_file_path": os.path.abspath(STOCK_SELECTION_FILE)
        }
        
        # ファイルサイズ情報
        if os.path.exists(FIXED_STOCK_FILE):
            info["fixed_file_size"] = os.path.getsize(FIXED_STOCK_FILE)
            try:
                fixed_df = pd.read_csv(FIXED_STOCK_FILE)
                info["fixed_data_count"] = len(fixed_df)
            except:
                info["fixed_data_count"] = "読み込みエラー"
                
        if os.path.exists(STOCK_SELECTION_FILE):
            info["selection_file_size"] = os.path.getsize(STOCK_SELECTION_FILE)
            try:
                selection_df = pd.read_csv(STOCK_SELECTION_FILE)
                info["selection_data_count"] = len(selection_df)
            except:
                info["selection_data_count"] = "読み込みエラー"
            
        return info

    @staticmethod
    def check_file_contents():
        """ファイル内容をチェック"""
        results = {}
        
        for file_type, file_path in [("fixed_stock", FIXED_STOCK_FILE), ("stock_selection", STOCK_SELECTION_FILE)]:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    results[file_type] = {
                        "exists": True,
                        "size": len(content),
                        "lines": len(content.split('\n')),
                        "first_100_chars": content[:100]
                    }
                except Exception as e:
                    results[file_type] = {
                        "exists": True,
                        "error": str(e)
                    }
            else:
                results[file_type] = {"exists": False}
        
        return results
