import os
import sqlite3
import sys
from datetime import datetime
from typing import Dict

import pandas as pd
import streamlit as st

# データベースファイルのパス
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_FILE = os.path.join(DB_DIR, "llm_analysis.db")


class DatabaseManager:
    """SQLiteデータベース管理クラス"""

    @staticmethod
    def get_system_info():
        """システム情報を取得"""
        info = {
            "python_version": sys.version,
            "current_working_directory": os.getcwd(),
            "data_directory": os.path.abspath(DB_DIR),
            "database_file": os.path.abspath(DB_FILE),
            "environment_variables": {},
            "file_permissions": {},
            "directory_contents": {},
        }

        # 環境変数を確認
        for key in ["HOME", "USER", "PATH", "PYTHONPATH"]:
            info["environment_variables"][key] = os.environ.get(key, "N/A")

        # ファイル権限を確認
        try:
            if os.path.exists(DB_DIR):
                stat_info = os.stat(DB_DIR)
                info["file_permissions"]["data_dir"] = oct(stat_info.st_mode)
                info["file_permissions"]["data_dir_uid"] = stat_info.st_uid
                info["file_permissions"]["data_dir_gid"] = stat_info.st_gid
        except:
            pass

        try:
            if os.path.exists(DB_FILE):
                stat_info = os.stat(DB_FILE)
                info["file_permissions"]["db_file"] = oct(stat_info.st_mode)
                info["file_permissions"]["db_file_uid"] = stat_info.st_uid
                info["file_permissions"]["db_file_gid"] = stat_info.st_gid
        except:
            pass

        # ディレクトリ内容を確認
        try:
            if os.path.exists(DB_DIR):
                info["directory_contents"]["data_dir"] = os.listdir(DB_DIR)
        except:
            pass

        try:
            info["directory_contents"]["root_dir"] = os.listdir(".")
        except:
            pass

        return info

    @staticmethod
    def init_database():
        """データベースとテーブルを初期化"""
        try:
            # データディレクトリが存在しない場合は作成
            if not os.path.exists(DB_DIR):
                os.makedirs(DB_DIR)
                print(f"データディレクトリを作成しました: {DB_DIR}")

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                # 固定銘柄分析テーブル
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fixed_stock_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_date TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    stock_code TEXT NOT NULL,
                    buy_date TEXT NOT NULL,
                    buy_price REAL NOT NULL,
                    sell_date TEXT NOT NULL,
                    sell_price REAL NOT NULL,
                    predicted_price REAL NOT NULL,
                    profit_loss REAL NOT NULL,
                    return_rate REAL NOT NULL,
                    prediction_accuracy REAL NOT NULL,
                    period_days INTEGER NOT NULL,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)

                # 銘柄選定分析テーブル
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_selection_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_date TEXT NOT NULL,
                    analysis_period TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    stock_code TEXT NOT NULL,
                    selection_reason TEXT NOT NULL,
                    buy_date TEXT NOT NULL,
                    buy_price REAL NOT NULL,
                    sell_date TEXT NOT NULL,
                    sell_price REAL NOT NULL,
                    profit_loss REAL NOT NULL,
                    return_rate REAL NOT NULL,
                    period_days INTEGER NOT NULL,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)

                conn.commit()
                print(f"データベースを初期化しました: {DB_FILE}")
                return True
        except Exception as e:
            print(f"データベース初期化エラー: {str(e)}")
            import traceback

            print(f"詳細エラー: {traceback.format_exc()}")
            if "st" in globals():
                st.error(f"データベース初期化エラー: {str(e)}")
            return False

    @staticmethod
    def save_fixed_stock_analysis(data: Dict) -> bool:
        """固定銘柄分析データを保存"""
        try:
            # データベースを初期化
            init_success = DatabaseManager.init_database()
            if not init_success:
                st.error("データベースの初期化に失敗しました")
                return False

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                INSERT INTO fixed_stock_analysis (
                    execution_date, model_id, stock_code, buy_date, buy_price,
                    sell_date, sell_price, predicted_price, profit_loss,
                    return_rate, prediction_accuracy, period_days, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data["execution_date"].isoformat(),
                        data["model_id"],
                        data["stock_code"],
                        data["buy_date"],
                        data["buy_price"],
                        data["sell_date"],
                        data["sell_price"],
                        data["predicted_price"],
                        data["profit_loss"],
                        data["return_rate"],
                        data["prediction_accuracy"],
                        data["period_days"],
                        data["notes"],
                    ),
                )

                conn.commit()

                # 保存確認
                cursor.execute("SELECT COUNT(*) FROM fixed_stock_analysis")
                count = cursor.fetchone()[0]
                st.success(
                    f"✅ 固定銘柄分析データを保存しました（総データ数: {count}件）"
                )

                return True
        except Exception as e:
            st.error(f"固定銘柄分析データ保存エラー: {str(e)}")
            import traceback

            st.error(f"詳細エラー: {traceback.format_exc()}")
            return False

    @staticmethod
    def save_stock_selection_analysis(data: Dict) -> bool:
        """銘柄選定分析データを保存"""
        try:
            # データベースを初期化
            init_success = DatabaseManager.init_database()
            if not init_success:
                st.error("データベースの初期化に失敗しました")
                return False

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                INSERT INTO stock_selection_analysis (
                    execution_date, analysis_period, model_id, stock_code,
                    selection_reason, buy_date, buy_price, sell_date, sell_price,
                    profit_loss, return_rate, period_days, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data["execution_date"].isoformat(),
                        data["analysis_period"],
                        data["model_id"],
                        data["stock_code"],
                        data["selection_reason"],
                        data["buy_date"],
                        data["buy_price"],
                        data["sell_date"],
                        data["sell_price"],
                        data["profit_loss"],
                        data["return_rate"],
                        data["period_days"],
                        data["notes"],
                    ),
                )

                conn.commit()

                # 保存確認
                cursor.execute("SELECT COUNT(*) FROM stock_selection_analysis")
                count = cursor.fetchone()[0]
                st.success(
                    f"✅ 銘柄選定分析データを保存しました（総データ数: {count}件）"
                )

                return True
        except Exception as e:
            st.error(f"銘柄選定分析データ保存エラー: {str(e)}")
            import traceback

            st.error(f"詳細エラー: {traceback.format_exc()}")
            return False

    @staticmethod
    def load_fixed_stock_data() -> pd.DataFrame:
        """固定銘柄分析データを読み込み"""
        try:
            if not os.path.exists(DB_FILE):
                DatabaseManager.init_database()
                return pd.DataFrame()

            with sqlite3.connect(DB_FILE) as conn:
                df = pd.read_sql_query(
                    """
                SELECT execution_date, model_id, stock_code, buy_date, buy_price,
                       sell_date, sell_price, predicted_price, profit_loss,
                       return_rate, prediction_accuracy, period_days, notes
                FROM fixed_stock_analysis
                ORDER BY created_at DESC
                """,
                    conn,
                )

                if not df.empty:
                    df["execution_date"] = pd.to_datetime(df["execution_date"])

                return df
        except Exception as e:
            st.error(f"固定銘柄分析データ読み込みエラー: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def load_stock_selection_data() -> pd.DataFrame:
        """銘柄選定分析データを読み込み"""
        try:
            if not os.path.exists(DB_FILE):
                DatabaseManager.init_database()
                return pd.DataFrame()

            with sqlite3.connect(DB_FILE) as conn:
                df = pd.read_sql_query(
                    """
                SELECT execution_date, analysis_period, model_id, stock_code,
                       selection_reason, buy_date, buy_price, sell_date, sell_price,
                       profit_loss, return_rate, period_days, notes
                FROM stock_selection_analysis
                ORDER BY created_at DESC
                """,
                    conn,
                )

                if not df.empty:
                    df["execution_date"] = pd.to_datetime(df["execution_date"])

                return df
        except Exception as e:
            st.error(f"銘柄選定分析データ読み込みエラー: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def get_database_info() -> Dict:
        """データベース情報を取得"""
        try:
            system_info = DatabaseManager.get_system_info()

            info = {
                "system_info": system_info,
                "database_file_exists": os.path.exists(DB_FILE),
                "database_size": 0,
                "fixed_stock_count": 0,
                "stock_selection_count": 0,
                "tables": [],
            }

            if os.path.exists(DB_FILE):
                info["database_size"] = os.path.getsize(DB_FILE)

                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()

                        # テーブル一覧を取得
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                        info["tables"] = [row[0] for row in cursor.fetchall()]

                        # 各テーブルのレコード数を取得
                        try:
                            cursor.execute("SELECT COUNT(*) FROM fixed_stock_analysis")
                            info["fixed_stock_count"] = cursor.fetchone()[0]
                        except:
                            pass

                        try:
                            cursor.execute(
                                "SELECT COUNT(*) FROM stock_selection_analysis"
                            )
                            info["stock_selection_count"] = cursor.fetchone()[0]
                        except:
                            pass
                except Exception as db_error:
                    info["database_error"] = str(db_error)

            return info
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def export_to_csv() -> bool:
        """データベースからCSVにエクスポート"""
        try:
            # 固定銘柄分析データ
            fixed_df = DatabaseManager.load_fixed_stock_data()
            if not fixed_df.empty:
                fixed_df.to_csv(
                    os.path.join(DB_DIR, "fixed_stock_analysis_export.csv"),
                    index=False,
                    encoding="utf-8-sig",
                )

            # 銘柄選定分析データ
            selection_df = DatabaseManager.load_stock_selection_data()
            if not selection_df.empty:
                selection_df.to_csv(
                    os.path.join(DB_DIR, "stock_selection_analysis_export.csv"),
                    index=False,
                    encoding="utf-8-sig",
                )

            st.success("✅ データをCSVファイルにエクスポートしました")
            return True
        except Exception as e:
            st.error(f"CSVエクスポートエラー: {str(e)}")
            return False

    @staticmethod
    def clear_all_data() -> bool:
        """全データを削除（注意して使用）"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM fixed_stock_analysis")
                cursor.execute("DELETE FROM stock_selection_analysis")
                conn.commit()

            st.success("✅ 全データを削除しました")
            return True
        except Exception as e:
            st.error(f"データ削除エラー: {str(e)}")
            return False

    @staticmethod
    def test_database_connection():
        """データベース接続をテスト"""
        try:
            st.write("🧪 データベース接続テスト開始...")

            # システム情報を表示
            system_info = DatabaseManager.get_system_info()
            st.json(system_info)

            # テストデータを挿入
            test_data = {
                "execution_date": datetime.now(),
                "analysis_period": "テスト",
                "model_id": "テストモデル",
                "stock_code": "0000",
                "selection_reason": "データベーステスト",
                "buy_date": "2024-01-01",
                "buy_price": 1000.0,
                "sell_date": "2024-01-31",
                "sell_price": 1100.0,
                "profit_loss": 100.0,
                "return_rate": 10.0,
                "period_days": 30,
                "notes": "テストデータ",
            }

            # データを保存
            success = DatabaseManager.save_stock_selection_analysis(test_data)

            if success:
                # データを読み込み
                df = DatabaseManager.load_stock_selection_data()
                st.write(f"✅ テスト完了。読み込みデータ数: {len(df)}件")

                if not df.empty:
                    st.write("最新のテストデータ:")
                    st.dataframe(df.head(1))

                return True
            else:
                st.error("❌ テストデータの保存に失敗")
                return False

        except Exception as e:
            st.error(f"データベーステストエラー: {str(e)}")
            import traceback

            st.error(f"詳細エラー: {traceback.format_exc()}")
            return False


# 下位互換性のためのDataManager（既存コードとの互換性を保つ）
class DataManager(DatabaseManager):
    """既存コードとの互換性を保つためのクラス"""

    @staticmethod
    def load_data(file_type: str) -> pd.DataFrame:
        """既存のload_dataメソッドとの互換性"""
        if "fixed_stock" in file_type:
            return DatabaseManager.load_fixed_stock_data()
        elif "stock_selection" in file_type:
            return DatabaseManager.load_stock_selection_data()
        else:
            return pd.DataFrame()

    @staticmethod
    def load_fixed_stock_data() -> pd.DataFrame:
        """固定銘柄分析データを読み込み"""
        return DatabaseManager.load_fixed_stock_data()

    @staticmethod
    def load_stock_selection_data() -> pd.DataFrame:
        """銘柄選定分析データを読み込み"""
        return DatabaseManager.load_stock_selection_data()

    @staticmethod
    def save_fixed_stock_analysis(data: Dict) -> bool:
        """固定銘柄分析データを保存"""
        return DatabaseManager.save_fixed_stock_analysis(data)

    @staticmethod
    def save_stock_selection_analysis(data: Dict) -> bool:
        """銘柄選定分析データを保存"""
        return DatabaseManager.save_stock_selection_analysis(data)

    @staticmethod
    def get_file_paths():
        """既存コードとの互換性（実際にはDBを使用）"""
        return {
            "fixed_stock": "database:fixed_stock",
            "stock_selection": "database:stock_selection",
        }

    @staticmethod
    def get_debug_info():
        """デバッグ情報を取得"""
        return DatabaseManager.get_database_info()

    @staticmethod
    def test_database_connection():
        """データベース接続をテスト"""
        return DatabaseManager.test_database_connection()

    @staticmethod
    def export_to_csv() -> bool:
        """データをCSVにエクスポート"""
        return DatabaseManager.export_to_csv()

    @staticmethod
    def clear_all_data() -> bool:
        """全データを削除"""
        return DatabaseManager.clear_all_data()

    @staticmethod
    def export_data(df: pd.DataFrame, filename: str) -> bool:
        """データエクスポート（下位互換性）"""
        return DatabaseManager.export_to_csv()
