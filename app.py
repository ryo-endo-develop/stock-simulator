import warnings

import streamlit as st

from modules.data_manager import DataManager
from modules.ui_components import (
    show_fixed_stock_analysis,
    show_history_analysis,
    show_main_page,
    show_stock_selection_analysis,
)

warnings.filterwarnings("ignore")

# アプリケーション起動時にデータベースを初期化
print("🚀 アプリケーション起動中...")
init_result = DataManager.init_database()
if init_result:
    print("✅ データベース初期化完了")
else:
    print("❌ データベース初期化に問題が発生しました")

# ページ設定
st.set_page_config(
    page_title="LLM投資アイデア検証ツール",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS スタイル
st.markdown(
    """
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .danger-card {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .info-card {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    """メインアプリケーション"""

    # サイドバーでページ選択
    st.sidebar.title("🤖 LLM投資アイデア検証ツール")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "分析タイプを選択",
        ["🏠 ホーム", "📊 固定銘柄分析", "🎯 銘柄選定分析", "📈 履歴分析・統計"],
    )

    # ページルーティング
    if page == "🏠 ホーム":
        show_main_page()
    elif page == "📊 固定銘柄分析":
        show_fixed_stock_analysis()
    elif page == "🎯 銘柄選定分析":
        show_stock_selection_analysis()
    elif page == "📈 履歴分析・統計":
        show_history_analysis()

    # サイドバーフッター
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📋 使用方法
    1. 分析タイプを選択
    2. 必要な情報を入力
    3. シミュレーション実行
    4. 結果を確認・保存
    """)

    st.sidebar.markdown("""
    ### ⚠️ 注意
    - 検証目的のツールです
    - 投資判断には使用しないでください
    - 手数料・税金は考慮されていません
    """)


if __name__ == "__main__":
    main()
