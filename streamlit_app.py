"""
【最高級別防魔改與功能復活】完全體重構 v2.0
========================================
核心承諾：
✅ 完整保留登入註冊系統（不修改不重寫）
✅ 強制復活五大財報模組（from streamlit_app_backup.py）  
✅ 強制復活MACD Plotly互動圖表（from mainn.py）
✅ 實現雙模式全域分析框架
✅ 使用 st.components.v1.html() 完美渲染 Plotly
========================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(layout="wide")  # ✔ 這行也要有

# ==== 頁面基礎設定 ====
st.set_page_config(
    page_title="台股🍄smart分析系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    :root {
        /* ===== Primary Brand Purple ===== */
        --purple-main: #6D28D9;
        --purple-dark: #4C1D95;
        --purple-light: #8B5CF6;
        --purple-soft: #EDE9FE;

        /* ===== Neutral Background ===== */
       --bg-0: #F7F8FC;
        --bg-1: #EEF1F8;

        /* ===== Text ===== */
        --ink-0: #1F1B24;
        --ink-1: #6B7280;

        /* ===== Borders ===== */
        --line-0: rgba(91, 75, 255, 0.10);
        --line-1: rgba(17, 24, 39, 0.08);

        /* ===== Surface ===== */
        --surface: rgba(255, 255, 255, 0.85);
    }

    .stApp {
        background: linear-gradient(180deg, #F7F8FC 0%, #EEF1F8 100%) !important;
        color: var(--ink-0);
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background: transparent !important;
        height: 0 !important;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F7F8FC, #EEF1F8);
        border-right: 1px solid rgba(91, 75, 255, 0.10);
        box-shadow: 8px 0 24px rgba(17, 24, 39, 0.06);
    }
    [data-testid="stSidebar"] * {
        color: var(--ink-0) !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, div, span, li {
        letter-spacing: 0 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--purple-1), var(--sage-0)) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 24px rgba(75, 53, 109, 0.18) !important;
        transition: transform .18s ease, box-shadow .18s ease, filter .18s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(75, 53, 109, 0.24) !important;
        filter: saturate(1.05);
    }

    .stMetric {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(91, 75, 255, 0.10);
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 34px rgba(17, 24, 39, 0.10);
    }

    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid var(--line-0);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 10px 22px rgba(65, 46, 92, 0.06);
    }

    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--line-0);
        border-radius: 14px;
        box-shadow: 0 10px 24px rgba(65, 46, 92, 0.05);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.55);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid var(--line-0);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 14px;
        background: transparent;
        color: var(--ink-1);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(91, 75, 255, 0.12) !important;
        color: var(--purple-main) !important;
        box-shadow: inset 0 0 0 1px rgba(91, 75, 255, 0.25);
       border-radius: 10px;
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
        border: 1px solid var(--line-0);
        backdrop-filter: blur(10px);
    }

    [data-testid="stSpinner"] > div {
        color: var(--purple-1);
    }

    .hero-band {
        background: rgba(255,255,255,0.92);

        color: var(--ink-0);

        border-radius: 18px;

        padding: 16px 18px;

        border: 1px solid rgba(91, 75, 255, 0.10);

        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);

        overflow: hidden;
    }

    .soft-card {
        background: rgba(255,255,255,0.86);
        border: 1px solid var(--line-0);
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 12px 24px rgba(61, 44, 86, 0.05);
    }

    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox div,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p {
        color: var(--ink-0) !important;
    }

    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255, 255, 255, 0.88) !important;
        border: 1px solid rgba(127, 159, 138, 0.22) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.04);
        color: var(--ink-0) !important;
        caret-color: var(--purple-1);
    }

    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(87, 80, 99, 0.68) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="radio"] {
        background: rgba(255, 255, 255, 0.42);
        border: 1px solid rgba(127, 159, 138, 0.14);
        border-radius: 14px;
        padding: 4px 8px;
    }

    .block-container {
        padding-top: 1.2rem;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    .stMetric,
    [data-testid="stDataFrame"],
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.88) !important;
        border: 1px solid rgba(91, 75, 255, 0.10) !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06) !important;
        transition: all 0.18s ease;
    }

    .stMetric:hover,
    [data-testid="stExpander"]:hover,
    [data-testid="stDataFrame"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 34px rgba(17, 24, 39, 0.10) !important;
    }

    p, label, div {
        line-height: 1.6;
    }

        /* ===== Card System（新增商業感核心）===== */

    .card {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(91, 75, 255, 0.10);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
        margin-bottom: 16px;
        transition: all 0.18s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 34px rgba(17, 24, 39, 0.10);
    }

    /* ===== KPI Text Style ===== */

    .kpi-title {
        font-size: 12px;
        color: var(--ink-1);
    }

    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--ink-0);
    }

    .kpi-delta {
        font-size: 12px;
        color: #22c55e;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# ==== 全域常數 ====
DB_PATH = Path.cwd() / "streamlit.db"
PROJECT_ROOT = Path(__file__).parent.parent
APP_DIR = Path(__file__).parent
LAST_FINAL_PROJECT_PATH = APP_DIR / "last_final_project"

try:
    import yfinance as yf
    HAS_YFINANCE = True
except:
    HAS_YFINANCE = False
# ==== 本地爬蟲模組設定（供模式一股利資料使用） ====
CRAWLER_PATH = Path(__file__).parent.parent / "crawler" / "tse_crawler"
if CRAWLER_PATH.exists():
    sys.path.insert(0, str(CRAWLER_PATH / "src"))
    try:
        from crawldata.crawl_div import CrawlDiv
        from crawldata.lib.dbinfo import DBInfo
        HAS_CRAWLER = True
    except:
        HAS_CRAWLER = False
else:
    HAS_CRAWLER = False

# ==== 登入大門：數據庫初始化與認證函數（完全保留） ====

def init_users_database():
    """初始化 users 表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def check_user_exists(userid):
    """檢查用戶是否存在"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE userid = ?", (userid,))
        count = c.fetchone()[0]
        conn.close()
        return count > 0
    except:
        return False

def verify_login(userid, password):
    """驗證登入"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE userid = ?", (userid,))
        result = c.fetchone()
        conn.close()
        return result and result[0] == password
    except:
        return False

def register_user(userid, password):
    """註冊新用戶"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (userid, password) VALUES (?, ?)", (userid, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def init_session_state():
    """初始化會話狀態"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None

# 初始化
init_session_state()
init_users_database()

# ============================================================================
# 模式一：個股財報分析完整輔助函式（來自 streamlit_app_backup.py）
# ============================================================================

def get_numeric_value(val):
    """安全的數值轉換"""
    try:
        if pd.isna(val):
            return 0
        return float(val)
    except:
        return 0

def convert_unit(val):
    """將金額單位轉換為千元"""
    try:
        return get_numeric_value(val) / 1000
    except:
        return 0

def get_column_by_keyword(df, keywords):
    """根據關鍵詞查找列（模糊匹配）"""
    if df is None or len(df) == 0 or len(df.columns) == 0:
        return None
    
    # 多層次匹配：精確 > 包含
    for keyword in keywords:
        keyword_lower = keyword.lower()
        for i, col in enumerate(df.columns):
            col_lower = str(col).lower()
            if col_lower == keyword_lower:
                return i
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        for i, col in enumerate(df.columns):
            col_lower = str(col).lower()
            if keyword_lower in col_lower:
                return i
    
    return None

def parse_excel_file(uploaded_file):
    """解析上傳的 Excel 文件"""
    try:
        # 方法1：嘗試使用 skiprows=2（標準 TEJ 格式）
        try:
            df = pd.read_excel(uploaded_file, skiprows=2)
        except:
            # 方法2：如果失敗，重新上傳並嘗試不跳過行
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file)
        
        # 移除逗號：Excel 中的金額可能帶有逗號，需要先移除再轉為數值
        for col in df.columns:
            if df[col].dtype == 'object':  # 只處理字串型別
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        
        # 重命名第一列為「年/月」（如果還不是）
        date_col = df.columns[0]
        if date_col not in ['季度', '年/月', '年月']:
            df = df.rename(columns={date_col: '年/月'})
            date_col = '年/月'
        else:
            date_col = df.columns[0]
        
        # 將日期列轉換為 datetime（處理多種格式）
        try:
            df[date_col] = pd.to_datetime(df[date_col], format='%Y/%m', errors='coerce')
        except:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # 移除日期列為 NaT 的行
        df = df.dropna(subset=[date_col])
        
        # 排序：從舊到新
        df = df.sort_values(date_col).reset_index(drop=True)
        
        # 將日期列重命名為「季度」供後續使用
        df = df.rename(columns={date_col: '季度'})
        
        if len(df) == 0:
            st.error("Excel 檔案中沒有有效的日期數據")
            return None
        
        return df
    except Exception as e:
        st.error(f"Excel 解析失敗: {str(e)}")
        import traceback
        st.error(f"詳細信息: {traceback.format_exc()}")
        return None

def calculate_metrics(df):
    """計算所有財務指標"""
    df = df.copy()
    
    # 金額欄位轉換為千元
    amount_cols = [
        '營業收入淨額', '營業利益', '常續性稅後淨利',
        '存貨', '應收帳款及票據', '應付帳款及票據',
        '合約負債－流動', '來自營運之現金流量', '投資活動之現金流量'
    ]
    
    for col in amount_cols:
        col_idx = get_column_by_keyword(df, [col])
        if col_idx is not None:
            col_name = df.columns[col_idx]
            df[col_name] = df[col_name].astype(float).apply(convert_unit)
    
    # 計算利潤率指標
    revenue_col = get_column_by_keyword(df, ['營業收入淨額'])
    profit_col = get_column_by_keyword(df, ['營業利益'])
    net_profit_col = get_column_by_keyword(df, ['常續性稅後淨利'])
    
    if revenue_col is not None and profit_col is not None:
        df['營業利益率'] = [
            (get_numeric_value(df.iloc[i, profit_col]) / max(get_numeric_value(df.iloc[i, revenue_col]), 0.001)) * 100
            for i in range(len(df))
        ]
    
    if revenue_col is not None and net_profit_col is not None:
        df['稅後淨利率'] = [
            (get_numeric_value(df.iloc[i, net_profit_col]) / max(get_numeric_value(df.iloc[i, revenue_col]), 0.001)) * 100
            for i in range(len(df))
        ]
    
# 1. 抓取欄位資訊
    inventory_turnover_col = get_column_by_keyword(df, ['存貨週轉率', '存貨週轉次數'])
    ar_turnover_col = get_column_by_keyword(df, ['應收帳款週轉次數', '應收帳款週轉率'])
    ap_days_col = get_column_by_keyword(df, ['應付帳款付現天數', '應付帳款週轉天數']) # 這是現成的天數欄位
    ap_turnover_col = get_column_by_keyword(df, ['應付帳款週轉次數', '應付帳款週轉率'])

    # 2. 計算存貨與應收週轉天數 (需除以 90)
    if inventory_turnover_col is not None:
        df['存貨週轉天數'] = [90 / max(get_numeric_value(x), 0.1) for x in df.iloc[:, inventory_turnover_col]]
    
    if ar_turnover_col is not None:
        df['應收帳款週轉天數'] = [90 / max(get_numeric_value(x), 0.1) for x in df.iloc[:, ar_turnover_col]]

    # 3. 處理應付帳款 (核心修正：有現成天數就直接抓，沒有才用次數計算)
    if ap_days_col is not None:
        # 直接使用原始天數，不進行除法運算！
        df['應付帳款週轉天數'] = df.iloc[:, ap_days_col].apply(get_numeric_value)
    elif ap_turnover_col is not None:
        # 只有在找不到天數欄位時，才用次數倒算
        df['應付帳款週轉天數'] = [90 / max(get_numeric_value(x), 0.1) for x in df.iloc[:, ap_turnover_col]]
    
    # 4. 計算 CCC (這時三個欄位單位統一，直接相加減)
    if all(col in df.columns for col in ['存貨週轉天數', '應收帳款週轉天數', '應付帳款週轉天數']):
        df['CCC'] = df['存貨週轉天數'] + df['應收帳款週轉天數'] - df['應付帳款週轉天數']
    
    # 業外收支佔營收比重
    # 優先查找精確的 "業外收支/營收" 欄位，其次查找業外相關欄位
    business_outside_ratio_col = get_column_by_keyword(df, ['業外收支/營收'])
    if business_outside_ratio_col is not None:
        # 如果 Excel 已有直接計算的比率欄位，直接使用
        df['業外收支/營收'] = df.iloc[:, business_outside_ratio_col].astype(float)
    else:
        # 否則從業外收入/支出欄位計算
        business_outside_col = get_column_by_keyword(df, ['業外收入', '業外支出', '業外淨收支'])
        if business_outside_col is not None and revenue_col is not None:
            df['業外收支/營收'] = [
                (get_numeric_value(df.iloc[i, business_outside_col]) / max(get_numeric_value(df.iloc[i, revenue_col]), 0.001)) * 100
                for i in range(len(df))
            ]
    
    # 利息保障倍數 - 直接取用 Excel 原始數值
    interest_col = get_column_by_keyword(df, ['利息保障', '利息倍數'])
    if interest_col is not None:
        df['利息保障倍數'] = df.iloc[:, interest_col].astype(float)
    
    return df

def fetch_stock_price(stock_code):
    """從 yfinance 獲取股票價格"""
    if not HAS_YFINANCE:
        return None
    
    try:
        symbol = f"{stock_code}.TW"
        stock = yf.Ticker(symbol)
        
        # 獲取最新價格
        hist = stock.history(period="1d")
        if hist is None or len(hist) == 0:
            return None
        
        return float(hist['Close'].iloc[-1])
    except:
        return None

def fetch_full_history_price(stock_code):
    """從 yfinance 獲取完整歷史股價（最長可用歷史）"""
    if not HAS_YFINANCE:
        return None
    
    try:
        symbol = f"{stock_code}.TW"
        # 使用 period="max" 獲取完整歷史數據
        hist = yf.download(symbol, period="max", progress=False)
        
        if hist is None or hist.empty:
            return None
        
        # 扁平化 MultiIndex columns（yfinance 返回 ('Close', '2330.TW') 格式）
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.get_level_values(0)
        
        # 重置索引以將日期轉換為列
        hist = hist.reset_index()
        # 確保日期列為正確的格式（無時區、無微秒）
        hist['Date'] = pd.to_datetime(hist['Date']).dt.normalize()
        # 將 Date 設定為索引
        hist = hist.set_index('Date')
        # 確保 Close 收盤價欄位是乾淨的數值型態
        hist['Close'] = pd.to_numeric(hist['Close'], errors='coerce')
        
        return hist
    except Exception as e:
        st.warning(f"無法獲取歷史股價：{str(e)}")
        return None

def fetch_annual_eps(stock_code):
    """
    專注 4 年度（2022-2025）的年度 EPS 數據抓取
    
    執行邏輯（3 管道）：
    - 管道 1：直接從 yfinance earnings 年度物件提取（最穩定）
    - 管道 2：掃描年度財報 financials，搜尋 Diluted EPS、Basic EPS、Net Income
    - 管道 3：最新未完結年份用 Ticker.info['trailingEps']（TTM 數據兜底）
    
    年份限制：嚴格限制在 2022、2023、2024、2025，避免舊年份 yfinance 斷訊問題
    數據完全接受微小除權息還原調整誤差（如 13.52、44.67），後端僅執行 round(x, 2)
    """
    if not HAS_YFINANCE:
        return None
    
    try:
        symbol = f"{stock_code}.TW"
        ticker = yf.Ticker(symbol)
        
        # 初始化 4 年結果字典（2022-2025）
        eps_result = {}
        target_years = [2022, 2023, 2024, 2025]
        current_year = datetime.now().year
        
        for year in target_years:
            eps_value = None
            
            # ========== 管道 1：yfinance 官方 earnings 物件 ==========
            try:
                # 嘗試 get_earnings() 或 earnings 屬性
                earnings_data = None
                if hasattr(ticker, 'get_earnings'):
                    earnings_data = ticker.get_earnings()
                elif hasattr(ticker, 'earnings'):
                    earnings_data = ticker.earnings
                
                if earnings_data is not None and not earnings_data.empty:
                    # earnings DataFrame 通常以 Date 為索引，包含 Earnings 欄
                    for date, row in earnings_data.iterrows():
                        if hasattr(date, 'year') and date.year == year:
                            # 搜尋包含 EPS、Diluted、Basic 等欄位
                            for col in earnings_data.columns:
                                if any(kw in str(col).lower() for kw in ['eps', 'diluted', 'basic']):
                                    value = get_numeric_value(row[col])
                                    if value is not None and value != 0:
                                        eps_value = round(float(value), 2)
                                        break
                            if eps_value is not None:
                                break
            except:
                pass
            
            # ========== 管道 2：年度財報 financials 表掃描 ==========
            if eps_value is None:
                try:
                    annual_financials = ticker.financials
                    if annual_financials is not None and not annual_financials.empty:
                        # 優先搜尋 Diluted EPS、Basic EPS
                        for idx in annual_financials.index:
                            idx_str = str(idx).strip().lower()
                            if any(kw in idx_str for kw in ['diluted eps', 'basic eps', 'eps']):
                                row = annual_financials.loc[idx]
                                for date, value in row.items():
                                    if hasattr(date, 'year') and date.year == year:
                                        val = get_numeric_value(value)
                                        if val is not None and val != 0:
                                            eps_value = round(float(val), 2)
                                            break
                                if eps_value is not None:
                                    break
                        
                        # 若仍未找到，嘗試 Net Income / Shares Outstanding
                        if eps_value is None:
                            net_income_val = None
                            net_income_idx = None
                            for idx in annual_financials.index:
                                if 'net income' in str(idx).lower():
                                    net_income_idx = idx
                                    break
                            
                            if net_income_idx is not None:
                                row = annual_financials.loc[net_income_idx]
                                for date, value in row.items():
                                    if hasattr(date, 'year') and date.year == year:
                                        net_income_val = get_numeric_value(value)
                                        break
                            
                            if net_income_val is not None:
                                try:
                                    shares = ticker.info.get('sharesOutstanding')
                                    if shares and shares > 0:
                                        eps_value = round(float(net_income_val) / float(shares), 2)
                                except (TypeError, ValueError, ZeroDivisionError):
                                    pass
                except:
                    pass
            
            # ========== 管道 3：TTM 終極兜底（最新未完結年份或落後年份） ==========
            # 針對 2025 年（如今年是 2025，用 TTM；如今年 > 2025，仍用 TTM 兜底）
            if eps_value is None and (year == current_year or year == 2025):
                try:
                    trailing_eps = ticker.info.get('trailingEps')
                    if trailing_eps is not None:
                        val = get_numeric_value(trailing_eps)
                        if val is not None:
                            eps_value = round(float(val), 2)
                except (TypeError, ValueError):
                    pass
            
            # ========== 型態檢查防呆：確保 eps_value 是安全的數字或 None ==========
            if eps_value is not None:
                try:
                    eps_value = float(eps_value)
                    eps_result[year] = round(eps_value, 2)
                except (TypeError, ValueError):
                    # 無效型態，該年份留白
                    pass
        
        # ========== 建立最終 DataFrame（包含缺失年份） ==========
        if eps_result:
            final_data = []
            for year in sorted(target_years, reverse=True):
                final_data.append({
                    'Year': year,
                    'EPS': eps_result.get(year, np.nan)  # 缺失年份顯示為 NaN（空白）
                })
            
            result_df = pd.DataFrame(final_data)
            return result_df
    
    except Exception as e:
        # 靜默失敗，返回 None 而不是拋出異常
        pass
    
    return None

def fetch_dividend_data_from_crawler(stock_code, years_back=10):
    """使用本地爬蟲外抓股利數據"""
    if not HAS_CRAWLER:
        return None
    
    try:
        # 設置數據庫路徑
        db_path = CRAWLER_PATH / "crawldata.sqlite3"
        if not db_path.exists():
            return None
        
        # 連接數據庫
        conn = sqlite3.connect(str(db_path))
        
        # 查詢股利數據
        query = """
        SELECT Year, CashDiv, StockDiv 
        FROM Dividend 
        WHERE StockID = ? 
        ORDER BY Year DESC 
        LIMIT ?
        """
        
        div_df = pd.read_sql_query(query, conn, params=(stock_code, years_back))
        conn.close()
        
        return div_df if not div_df.empty else None
    except:
        return None

def get_quarter_label(date):
    """從日期獲取季度標籤"""
    if pd.isna(date):
        return "N/A"
    month = date.month
    quarter = (month - 1) // 3 + 1
    year = date.year
    return f"{year}Q{quarter}"

# ==== 模式二：MACD 圖表強制渲染 ====

def download_stock_history_for_macd(stock_code, period="5y"):
    """依股票代碼自動從 Yahoo Finance 下載模式二回測所需股價資料"""
    if not HAS_YFINANCE:
        return None, None

    clean_code = str(stock_code).strip().upper()
    if not clean_code:
        return None, None

    candidates = [clean_code]
    if "." not in clean_code:
        candidates = [f"{clean_code}.TW", f"{clean_code}.TWO", clean_code]

    for symbol in candidates:
        try:
            data = yf.download(symbol, period=period, progress=False, auto_adjust=False)
            if data is None or data.empty:
                continue

            data_clean = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            if isinstance(data_clean.columns, pd.MultiIndex):
                data_clean.columns = data_clean.columns.get_level_values(0)

            if not isinstance(data_clean.index, pd.DatetimeIndex):
                data_clean.index = pd.to_datetime(data_clean.index)

            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                data_clean[col] = pd.to_numeric(data_clean[col], errors='coerce')

            data_clean = data_clean.dropna()
            if not data_clean.empty:
                data_clean.index.name = "Date"
                return data_clean, symbol
        except Exception:
            continue

    return None, None

def make_macd_figure_plotly(
    df,
    show_sma_week=True,
    show_sma_month=True,
    show_sma_quarter=True,
    show_sma_year=True,
    trades_detail=None,
    title="股價圖與 MACD 技術分析圖"
):
    """建立來自 mainn.py 邏輯的 Plotly 股價 + MACD 互動圖"""
    try:
        df = df.copy()
        
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
        
        if 'Date' not in df.columns:
            df['Date'] = df.index
        
        df = df.sort_values('Date', ignore_index=True).reset_index(drop=True)
        
        dates = pd.to_datetime(df['Date'])
        close = df['Close'].astype(float)
        
        project_path = LAST_FINAL_PROJECT_PATH
        if str(project_path) not in sys.path:
            sys.path.insert(0, str(project_path))
        from strategy import _macd_array, _signal_array

        macd_vals = np.asarray(_macd_array(close, 12, 26))
        sig_vals = np.asarray(_signal_array(close, 12, 26, 9))
        hist_vals = macd_vals - sig_vals
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            row_heights=[0.65, 0.35],
            subplot_titles=("股價圖", "MACD 指標")
        )
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=close,
                name='股價（收盤價）',
                line=dict(color='blue', width=1.7)
            ),
            row=1, col=1
        )

        if show_sma_week:
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=df['Close'].rolling(window=5, min_periods=1).mean(),
                    mode='lines',
                    name='SMA（周 5）',
                    line=dict(color='magenta', width=1.5)
                ),
                row=1, col=1
            )
        if show_sma_month:
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=df['Close'].rolling(window=20, min_periods=1).mean(),
                    mode='lines',
                    name='SMA（月 20）',
                    line=dict(color='orange', width=1.5)
                ),
                row=1, col=1
            )
        if show_sma_quarter:
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=df['Close'].rolling(window=60, min_periods=1).mean(),
                    mode='lines',
                    name='SMA（季 60）',
                    line=dict(color='darkgreen', width=1.5)
                ),
                row=1, col=1
            )
        if show_sma_year:
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=df['Close'].rolling(window=240, min_periods=1).mean(),
                    mode='lines',
                    name='SMA（年 240）',
                    line=dict(color='navy', width=1.5)
                ),
                row=1, col=1
            )

        if trades_detail:
            buy_x, buy_y, sell_x, sell_y = [], [], [], []
            for trade in trades_detail:
                entry_time = trade.get('entry_time')
                exit_time = trade.get('exit_time')
                entry_price = trade.get('entry_price')
                exit_price = trade.get('exit_price')
                if entry_time and entry_price is not None:
                    buy_x.append(pd.to_datetime(entry_time))
                    buy_y.append(float(entry_price))
                if exit_time and exit_price is not None:
                    sell_x.append(pd.to_datetime(exit_time))
                    sell_y.append(float(exit_price))

            if buy_x:
                fig.add_trace(
                    go.Scatter(
                        x=buy_x,
                        y=buy_y,
                        mode='markers',
                        name='買進點',
                        marker=dict(symbol='triangle-up', color='green', size=11)
                    ),
                    row=1, col=1
                )
            if sell_x:
                fig.add_trace(
                    go.Scatter(
                        x=sell_x,
                        y=sell_y,
                        mode='markers',
                        name='賣出點',
                        marker=dict(symbol='triangle-down', color='red', size=11)
                    ),
                    row=1, col=1
                )
        
        colors = ['#d62728' if v >= 0 else '#2ca02c' for v in np.nan_to_num(hist_vals, nan=0.0)]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=np.nan_to_num(hist_vals, nan=0.0),
                marker=dict(color=colors, line=dict(width=0)),
                name='MACD 柱',
                showlegend=False
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=macd_vals,
                name='快線（DIF）',
                line=dict(color='rgba(31,119,180,0.7)', width=1.6)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sig_vals,
                name='慢線（Signal）',
                line=dict(color='rgba(255,127,14,0.7)', width=1.6)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=title,
            height=850,
            hovermode='x unified',
            template='plotly_white',
            showlegend=True
        )
        
        fig.update_xaxes(tickformat='%Y-%m', rangeslider_visible=False)
        fig.update_xaxes(title_text="日期", row=2, col=1)
        fig.update_yaxes(title_text="股價（元）", row=1, col=1)
        fig.update_yaxes(title_text="MACD", row=2, col=1)
        
        return fig
    except Exception as e:
        st.error(f"圖表生成失敗: {e}")
        return None

# ==== 登入判斷：第一道阻斷大門 ====

if not st.session_state.logged_in:
    st.title("台股🍄smart分析系統")
    
    auth_mode = st.radio("第一次登入，點選**帳號註冊**\n\n已註冊過帳號，點選**會員登入**", ["會員登入", "帳號註冊"], horizontal=True)
    st.divider()
    
    if auth_mode == "會員登入":
        st.markdown("### 會員登入")
        
        with st.form(key="login_form", clear_on_submit=False):
            login_userid = st.text_input("帳號", placeholder="輸入帳號", key="login_userid_form")
            login_password = st.text_input("密碼", type="password", placeholder="輸入密碼", key="login_password_form")
            
            login_submit = st.form_submit_button("✅ 登入", use_container_width=True)
            
            if login_submit:
                final_userid = login_userid.strip()
                final_password = login_password.strip()
                
                if not final_userid or not final_password:
                    st.error("帳號與密碼不可為空！")
                elif verify_login(final_userid, final_password):
                    st.session_state.logged_in = True
                    st.session_state.username = final_userid
                    st.success(f"✅ 登入成功！歡迎 {final_userid}")
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤")
    
    else:
        st.markdown("### 帳號註冊")
        
        with st.form(key="register_form", clear_on_submit=False):
            reg_userid = st.text_input("設定帳號", placeholder="輸入新帳號", key="reg_userid_form")
            reg_password = st.text_input("設定密碼", type="password", placeholder="輸入密碼", key="reg_password_form")
            reg_confirm = st.text_input("確認密碼", type="password", placeholder="再次輸入密碼", key="reg_confirm_form")
            
            submit_button = st.form_submit_button("✅ 提交註冊", use_container_width=True)
            
            if submit_button:
                final_userid = reg_userid.strip()
                final_password = reg_password.strip()
                final_confirm = reg_confirm.strip()
                
                if not final_userid or not final_password or not final_confirm:
                    st.error("帳號與密碼不可為空！")
                elif final_password != final_confirm:
                    st.error("兩次輸入的密碼不一致！")
                elif check_user_exists(final_userid):
                    st.error("該帳號已被註冊！")
                elif register_user(final_userid, final_password):
                    st.success("✅ 註冊成功！請切換至登入選項")
                    st.rerun()
                else:
                    st.error("❌ 註冊失敗")
    
    st.stop()

# ==== 已登入：雙模式全域分析框架 ====

# ==== 側邊欄：全域聯動元件 ====
with st.sidebar:
    st.markdown(f"### 🌷{st.session_state.username}")
    
    if st.button("登出", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    st.divider()
    
    # 全域股票代碼輸入（自動補上 .TW）
    stock_code = st.text_input(
        "請輸入台股代碼",
        value="",  # 🌟 一開始保持空白
        placeholder="例如：2330、2317"
    )

    
    st.divider()
    
    # 分析模式選擇
    # 獲取 URL 參數或使用默認值
    mode_index = 1 if st.query_params.get("mode") == "2" else 0
    
# 分析模式選擇 (這段保留你的熊熊)
    mode_index = 1 if st.query_params.get("mode") == "2" else 0
    
    selected_mode = st.radio(
        "分析模式",
        [
            "🐻個股財報分析",
            "🐻‍❄️MACD技術分析回測"
        ],
        index=mode_index
    )

    # 翻譯模式名稱，保留原汁原味
    if "個股財報分析" in selected_mode:
        selected_mode = "📄 模式一：個股財報分析（基本面）"
    elif "MACD技術分析" in selected_mode:
        selected_mode = "📈 模式二：技術分析回測（MACD）"

    # --- 統一設計，保留標題的熊符號與細緻樣式 ---
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 14px; color: #31333F; font-weight: 500; margin-bottom: 8px;">
        系統服務
    </div>
    """, unsafe_allow_html=True)
    
    # 按鈕樣式統一，看起來更專業
    st.link_button(
        "🐶功能建議與回饋", 
        "https://forms.gle/nDyRNa4BvSzuecqe8", 
        use_container_width=True
    )

# ==== 主頁面標題 ====
st.title("台股🍄smart分析系統")
st.markdown(f"尊貴的🌷**{st.session_state.username}**您好，本平台提供**個股財報分析**和**MACD回測系統**服務，請在左側選擇分析模式並輸入股票代碼，開始您的智能分析之旅！")
st.divider()

# ⬇️ 貼在這裡 (主頁面索取區)
st.subheader("🐑索取 TEJ 財報資料")
with st.expander("點擊展開：索取 TEJ 財報檔案"):
    st.info("若您需要TEJ財報檔案，請點擊下方按鈕前往表單填寫，我們會盡速處理。")
    st.link_button("前往索取財報表單", "https://forms.gle/XJog13NrWsBdXTfQA", use_container_width=True)

st.divider()


# ==== 模式一：個股財報分析（基本面）- 使用 streamlit_app_backup.py 完整內容 ====
if "個股財報分析" in selected_mode:
    st.markdown("### 🐻個股財報分析")
    
    uploaded_file = st.file_uploader(
        "上傳 TEJ Excel 財務報表",
        type=['xlsx', 'xls'],
        help="請上傳 TEJ Excel 財務報表（系統會自動跳過前 2 行）"
    )
    
    if not stock_code or stock_code.strip() == "" or uploaded_file is None:
        st.info("請在左側輸入股票代碼，並在此處上傳 TEJ Excel 財務報表，即可進入五個分析標籤。")
    else:
        df = parse_excel_file(uploaded_file)
        
        if df is not None:
            df = calculate_metrics(df)
            st.subheader(f"{stock_code} 財報分析")
            # 建立標籤頁（5 個標籤）
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🌸 股價資訊",
                "🍀 季報分析",
                "🍁 深度分析",
                "🌻 股利資訊",
                "🌱 估值預測"
            ])
            
            # ====================================================================
            # 標籤一：數據預覽
            # ====================================================================
            with tab1:

                current_price = fetch_stock_price(stock_code)
                if current_price:
                    hist = fetch_full_history_price(stock_code)

                    if hist is not None and not hist.empty:
                        try:
                            import plotly.graph_objects as go

                            hist_clean = hist.copy()
                            hist_clean['Close'] = hist_clean['Close'].round(2)
                            hist_clean['Return%'] = hist_clean['Close'].pct_change().fillna(0) * 100

                            latest_close = float(hist_clean['Close'].iloc[-1])
                            prev_close = float(hist_clean['Close'].iloc[-2]) if len(hist_clean) > 1 else latest_close
                            diff = latest_close - prev_close
                            diff_pct = (diff / prev_close * 100) if prev_close else 0
                            latest_date = hist_clean.index.max().date()

                            col_left, col_right = st.columns([1, 3])
                            with col_left:
                                st.markdown("#### 即時股價")
                                st.metric("最新收盤價", f"{latest_close:.2f} 元", delta=f"{diff:+.2f} 元")
                                st.caption(f"資料日期：{latest_date}")
                                st.caption(f"單日漲跌幅：{diff_pct:+.2f}%")
                                st.caption(f"資料筆數：{len(hist_clean):,}")

                            with col_right:
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=hist_clean.index,
                                    y=hist_clean['Close'],
                                    mode='lines',
                                    name='收盤價',
                                    line=dict(color='#6f63b6', width=2.2),
                                    hovertemplate='<b>日期: %{x|%Y-%m-%d}</b><br>收盤價: <b>%{y:.2f} 元</b><extra></extra>',
                                    connectgaps=False
                                ))
                                fig.update_xaxes(
                                    showspikes=True,
                                    spikemode='across',
                                    spikesnap='cursor',
                                    showline=True,
                                    linewidth=1,
                                    linecolor='rgba(93, 108, 124, 0.18)',
                                    spikecolor='rgba(93, 108, 124, 0.32)',
                                    spikethickness=1
                                )
                                fig.update_yaxes(
                                    showspikes=True,
                                    spikemode='across',
                                    spikecolor='rgba(93, 108, 124, 0.18)',
                                    spikethickness=1
                                )
                                fig.update_xaxes(
                                    rangeslider_visible=True,
                                    rangeslider_thickness=0.05,
                                    rangeselector=dict(
                                        buttons=list([
                                            dict(count=1, label="1m", step="month"),
                                            dict(count=6, label="6m", step="month"),
                                            dict(count=1, label="1y", step="year"),
                                            dict(count=3, label="3y", step="year"),
                                            dict(count=5, label="5y", step="year"),
                                            dict(step="all", label="全部")
                                        ])
                                    )
                                )
                                fig.update_layout(
                                    title=f"{stock_code} 完整歷史股價走勢",
                                    xaxis_title="日期",
                                    yaxis_title="股價（元）",
                                    hovermode='x unified',
                                    height=520,
                                    margin=dict(l=30, r=20, t=70, b=65),
                                    template="plotly_white",
                                    font=dict(size=12),
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(255,255,255,0.96)'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning(f"無法載入股價圖表：{str(e)}")
                    else:
                        st.info("暫無歷史股價數據")
                else:
                    st.warning(f"無法取得 {stock_code} 的實時股價")
                
                st.divider()
                st.subheader("原始財務數據")
                
                # 將數據表格放入 expander
                with st.expander("查看原始財務數據表", expanded=False):
                    display_df = df.copy()
                    display_df['季度'] = display_df['季度'].apply(get_quarter_label)
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    st.markdown(f"**總筆數**: {len(df)} 季 | **時間跨度**: {get_quarter_label(df['季度'].min())} ~ {get_quarter_label(df['季度'].max())}")
            
            # ====================================================================
            # 標籤二：財報項目季報比較
            # ====================================================================
            with tab2:
                
                # 準備 X 軸（季度標籤）
                df['季度_label'] = df['季度'].apply(get_quarter_label)
                
                # ========================================
                # 🌼獲利指標組
                # ========================================
                with st.container():
                    st.markdown("### 🌼獲利指標組")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown("""
                        **指標說明：**
                        - **左軸**: 營業收入淨額（柱狀圖，千元）
                        - **右軸實線**: 營業利益率（%）
                        - **右軸虛線**: 稅後淨利率（%）
                        
                        用於評估企業獲利能力
                        """)
                    
                    with col2:
                        fig1 = go.Figure()
                        
                        # 左軸：營業收入淨額（柱狀圖，淺藍色）
                        revenue_col = get_column_by_keyword(df, ['營業收入淨額'])
                        if revenue_col is not None:
                            revenue_values = [get_numeric_value(df.iloc[i, revenue_col]) for i in range(len(df))]
                            fig1.add_trace(go.Bar(
                                x=df['季度_label'],
                                y=revenue_values,
                                name='營業收入淨額',
                                marker=dict(color='#2980b9'),
                                yaxis='y1'
                            ))
                        
                        # 右軸：營業利益率（實線）
                        if '營業利益率' in df.columns:
                            fig1.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=df['營業利益率'],
                                mode='lines+markers',
                                name='營業利益率',
                                line=dict(color='#e74c3c', width=2, dash='solid'),
                                yaxis='y2'
                            ))
                        
                        # 右軸：稅後淨利率（虛線）
                        if '稅後淨利率' in df.columns:
                            fig1.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=df['稅後淨利率'],
                                mode='lines+markers',
                                name='稅後淨利率',
                                line=dict(color='#f39c12', width=2, dash='dash'),
                                yaxis='y2'
                            ))
                        
                        fig1.update_layout(
                            title="營業收入 + 獲利率趨勢",
                            xaxis_title="季度",
                            yaxis=dict(
                                title="營業收入淨額（千元）",
                                side='left'
                            ),
                            yaxis2=dict(
                                title="獲利率（%）",
                                overlaying='y',
                                side='right'
                            ),
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig1, use_container_width=True)
                
                st.divider()
                
                # ========================================
# 模組 2️⃣：營運效率組（全天數統一分析）
                # ========================================
                with st.container():
                    st.markdown("### 🌼營運效率組")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown("""
                        **指標說明：**
                        - **存貨週轉天數**: 商品從入庫到銷貨完成的天數。
                        - **應收帳款週轉天數**: 銷貨完成到實質收到現金的天數。
                        - **應付帳款週轉天數**: 向供應商進貨到實際支付貨款的天數。
                                    
                        用於評估企業對內部營運資金的調度與管理效率
                        """)
                    
                    with col2:
                        fig2 = go.Figure()
                        
                        # 1. 存貨週轉率 -> 即時轉換為「存貨週轉天數」
                        inv_turnover_col = get_column_by_keyword(df, ['存貨週轉率'])
                        if inv_turnover_col is not None:
                            inv_days_values = [
                                90 / max(get_numeric_value(df.iloc[i, inv_turnover_col]), 0.1) 
                                for i in range(len(df))
                            ]
                            fig2.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=inv_days_values,
                                mode='lines+markers',
                                name='存貨週轉天數',
                                line=dict(color='#27ae60', width=2)
                            ))
                        
                        # 2. 應收帳款週轉率 -> 即時轉換為「應收帳款週轉天數」
                        ar_turnover_col = get_column_by_keyword(df, ['應收帳款週轉率', '應收帳款週轉次數'])
                        if ar_turnover_col is not None:
                            ar_days_values = [
                                90 / max(get_numeric_value(df.iloc[i, ar_turnover_col]), 0.1) 
                                for i in range(len(df))
                            ]
                            fig2.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=ar_days_values,
                                mode='lines+markers',
                                name='應收帳款週轉天數',
                                line=dict(color='#2980b9', width=2)
                            ))
                        
                        # 3. 應付帳款週轉天數 -> 🌟 保持不變，直接沿用原廠數值
                        ap_days_col = get_column_by_keyword(df, ['應付帳款週轉天數'])
                        if ap_days_col is not None:
                            ap_days_values = [get_numeric_value(df.iloc[i, ap_days_col]) for i in range(len(df))]
                            fig2.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=ap_days_values,
                                mode='lines+markers',
                                name='應付帳款週轉天數',
                                line=dict(color='#9b59b6', width=2)
                            ))
                        
                        # 🌟 圖表佈局修正：拿掉 yaxis2，左邊 Y 軸標題統一改成「單位：天數」
                        fig2.update_layout(
                            title="單季營運天數趨勢分析",
                            xaxis_title="季度",
                            yaxis=dict(
                                title="單位：天數",
                                side='left'
                            ),
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                
                st.divider()
                
                # ========================================
                # 🌼現金流模組
                # ========================================
                with st.container():
                    st.markdown("### 🌼現金流模組")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown("""
                        **指標說明：**
                        - **營運現金流量**: 來自營運活動的現金
                        - **投資現金流量**: 來自投資活動的現金
                        
                        用於評估企業現金生成能力
                        """)
                    
                    with col2:
                        fig3 = go.Figure()
                        
                        # 營運現金流量
                        ocf_col = get_column_by_keyword(df, ['來自營運之現金流量', '營運現金流量'])
                        if ocf_col is not None:
                            ocf_values = [get_numeric_value(df.iloc[i, ocf_col]) for i in range(len(df))]
                            fig3.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=ocf_values,
                                mode='lines+markers',
                                name='營運現金流量',
                                line=dict(color='#2980b9', width=2),
                                connectgaps=True
                            ))
                        
                        # 投資現金流量
                        icf_col = get_column_by_keyword(df, ['投資活動之現金流量', '投資現金流量'])
                        if icf_col is not None:
                            icf_values = [get_numeric_value(df.iloc[i, icf_col]) for i in range(len(df))]
                            fig3.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=icf_values,
                                mode='lines+markers',
                                name='投資現金流量',
                                line=dict(color='#9b59b6', width=2),
                                connectgaps=True
                            ))
                        
                        fig3.update_layout(
                            title="現金流量趨勢（兩條獨立折線）",
                            xaxis_title="季度",
                            yaxis_title="現金流量（千元）",
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig3, use_container_width=True)
                
                st.divider()
                
                # ========================================
                # 🌼業外收支模組（雙軸設計）
                # ========================================
                with st.container():
                    st.markdown("### 🌼業外收支模組")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown("""
                        **指標說明：**
                        - **左軸**: 營業收入金額（柱狀圖，千元）
                        - **右軸**: 業外收支佔營收比（%）
                        
                        用於評估非營業部分影響
                        """)
                    
                    with col2:
                        fig4 = go.Figure()
                        
                        # 左軸：營業收入金額
                        revenue_col = get_column_by_keyword(df, ['營業收入淨額'])
                        if revenue_col is not None:
                            revenue_values = [get_numeric_value(df.iloc[i, revenue_col]) for i in range(len(df))]
                            fig4.add_trace(go.Bar(
                                x=df['季度_label'],
                                y=revenue_values,
                                name='營業收入淨額',
                                marker=dict(color='#2980b9'),
                                yaxis='y1'
                            ))
                        
                        # 右軸：業外收支/營收比（精確欄位綁定）
                        if '業外收支/營收' in df.columns:
                            fig4.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=df['業外收支/營收'],
                                mode='lines+markers',
                                name='業外收支/營收',
                                line=dict(color='#e67e22', width=2),
                                yaxis='y2'
                            ))
                        
                        fig4.update_layout(
                            title="業外收支影響分析",
                            xaxis_title="季度",
                            yaxis=dict(
                                title="營業收入淨額（千元）",
                                side='left'
                            ),
                            yaxis2=dict(
                                title="業外收支/營收（%）",
                                overlaying='y',
                                side='right'
                            ),
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig4, use_container_width=True)
                
                st.divider()
                
                # ========================================
                # 模組 5️⃣：財務風險與估值組（雙軸設計）
                # ========================================
                with st.container():
                    st.markdown("### 🌼財務風險與估值組")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown("""
                        **指標說明：**
                        - **左軸**: 存貨（柱狀圖，千元）
                        - **右軸線**:
                          - 負債比率（%）
                          - 利息保障倍數（倍）
                          - P/E 本益比（倍）
                        
                        用於評估財務風險水位
                        """)
                    
                    with col2:
                        fig5 = go.Figure()
                        
                        # 左軸：存貨（金額，柱狀圖）
                        inventory_col = get_column_by_keyword(df, ['存貨'])
                        if inventory_col is not None:
                            inventory_values = [get_numeric_value(df.iloc[i, inventory_col]) for i in range(len(df))]
                            fig5.add_trace(go.Bar(
                                x=df['季度_label'],
                                y=inventory_values,
                                name='存貨',
                                marker=dict(color='#bdc3c7'),
                                yaxis='y1'
                            ))
                        
                        # 右軸：負債比率
                        debt_col = get_column_by_keyword(df, ['負債比率'])
                        if debt_col is not None:
                            debt_values = [get_numeric_value(df.iloc[i, debt_col]) for i in range(len(df))]
                            fig5.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=debt_values,
                                mode='lines+markers',
                                name='負債比率',
                                line=dict(color='#e74c3c', width=2),
                                yaxis='y2'
                            ))
                        
                        # 右軸：利息保障倍數
                        if '利息保障倍數' in df.columns:
                            fig5.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=df['利息保障倍數'],
                                mode='lines+markers',
                                name='利息保障倍數',
                                line=dict(color='#2980b9', width=2),
                                yaxis='y2'
                            ))
                        
                        # 右軸：P/E
                        pe_col = get_column_by_keyword(df, ['P/E', '當季季底 P/E', '本益比'])
                        if pe_col is not None:
                            pe_values = [get_numeric_value(df.iloc[i, pe_col]) for i in range(len(df))]
                            fig5.add_trace(go.Scatter(
                                x=df['季度_label'],
                                y=pe_values,
                                mode='lines+markers',
                                name='P/E',
                                line=dict(color='#27ae60', width=2),
                                yaxis='y2'
                            ))
                        
                        fig5.update_layout(
                            title="財務風險與估值趨勢",
                            xaxis_title="季度",
                            yaxis=dict(
                                title="存貨（千元）",
                                side='left'
                            ),
                            yaxis2=dict(
                                title="負債比率(%) / 利息倍數 / P/E(倍)",
                                overlaying='y',
                                side='right'
                            ),
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig5, use_container_width=True)
                
                st.divider()
                
                # ========================================
                # 原始財務數據展示（折疊選項）
                # ========================================
                with st.expander("查看原始財務數據表（點此展開）"):
                    st.markdown("### 完整季度財務數據")
                    st.dataframe(df, use_container_width=True)
            
            # ====================================================================
            # 標籤三：改先放深度分析
            # ====================================================================
            with tab3:
                
                col1, col2 = st.columns(2)
                
                # 訂單真實性驗證
                with col1:
                    st.markdown("### 💐訂單真實性驗證")
                    
                    inventory_col = get_column_by_keyword(df, ['存貨'])
                    liability_col = get_column_by_keyword(df, ['合約負債'])
                    
                    if inventory_col is not None and liability_col is not None:
                        df['存貨天數'] = 90 / df['存貨週轉率（次）'].replace(0, np.inf)
                        
                        # 最新數據分析
                        latest_inventory = df.iloc[-1, inventory_col]
                        latest_liability = df.iloc[-1, liability_col]
                        prev_inventory = df.iloc[-2, inventory_col] if len(df) > 1 else latest_inventory
                        prev_liability = df.iloc[-2, liability_col] if len(df) > 1 else latest_liability
                        
                        inv_growth = (latest_inventory - prev_inventory) / max(abs(prev_inventory), 1)
                        liability_growth = (latest_liability - prev_liability) / max(abs(prev_liability), 1)
                        
                        if liability_growth > 0.5 * inv_growth and inv_growth > 0:
                            verdict = "珍珠✨"
                            color = "green"
                            detail = "存貨和合約負債同向增長 → 訂單真實性高"
                        elif inv_growth > 0.3 and liability_growth < 0.05:
                            verdict = "陷阱⚠️"
                            color = "red"
                            detail = "存貨增加但合約負債停滯 → 銷售風險"
                        else:
                            verdict = "正常📊"
                            color = "blue"
                            detail = "變化平穩 → 需求一致"
                        
                        st.markdown(f"**判決**: <span style='color:{color}'>{verdict}</span>", unsafe_allow_html=True)
                        st.markdown(f"**分析**: {detail}")
                        
                        # 圖表
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df['季度_label'],
                            y=[df.iloc[i, inventory_col] for i in range(len(df))],
                            mode='lines+markers',
                            name='存貨'
                        ))
                        fig.add_trace(go.Scatter(
                            x=df['季度_label'],
                            y=[df.iloc[i, liability_col] for i in range(len(df))],
                            mode='lines+markers',
                            name='合約負債',
                            yaxis='y2',

                        ))
                        fig.update_layout(
                            title="存貨 vs 合約負債",
                            xaxis_title="季度",
                            yaxis_title="存貨（千元）",
                            yaxis2=dict(title="合約負債（千元）", overlaying='y', side='right'),
                            height=350
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # 獲利含金量驗證
                with col2:
                    st.markdown("### 💐獲利含金量驗證")
                    
                    eps_col = get_column_by_keyword(df, ['EPS', '每股盈餘'])
                    ocf_col = get_column_by_keyword(df, ['來自營運', '營運現金', 'OCF'])
                    
                    if eps_col is not None and ocf_col is not None:
                        latest_eps = df.iloc[-1, eps_col]
                        latest_ocf = df.iloc[-1, ocf_col]
                        prev_eps = df.iloc[-2, eps_col] if len(df) > 1 else latest_eps
                        prev_ocf = df.iloc[-2, ocf_col] if len(df) > 1 else latest_ocf
                        
                        eps_trend = latest_eps >= prev_eps
                        ocf_trend = latest_ocf >= prev_ocf
                        
                        if eps_trend and ocf_trend:
                            verdict = "高含金量✅"
                            color = "green"
                            detail = f"EPS ({latest_eps:.2f}) 與 OCF ({latest_ocf:.0f}K) 同向增長"
                        elif eps_trend and not ocf_trend and latest_eps > 0:
                            verdict = "虛假獲利風險🚩"
                            color = "red"
                            detail = f"EPS 創高但 OCF 下滑 → 利潤品質堪慮"
                        else:
                            verdict = "中含金量📊"
                            color = "blue"
                            detail = "利潤增長與現金流有差異"
                        
                        st.markdown(f"**判決**: <span style='color:{color}'>{verdict}</span>", unsafe_allow_html=True)
                        st.markdown(f"**分析**: {detail}")
                        
                        # 圖表
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df['季度_label'],
                            y=[df.iloc[i, eps_col] for i in range(len(df))],
                            mode='lines+markers',
                            name='EPS',

                        ))
                        fig.add_trace(go.Scatter(
                            x=df['季度_label'],
                            y=[df.iloc[i, ocf_col] for i in range(len(df))],
                            mode='lines+markers',
                            name='營運現金流',
                            yaxis='y2',

                        ))
                        fig.update_layout(
                            title="EPS vs 營運現金流",
                            xaxis_title="季度",
                            yaxis_title="EPS（元）",
                            yaxis2=dict(title="OCF（千元）", overlaying='y', side='right'),
                            height=350
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                
                col3, col4 = st.columns(2)
                
                # 經營效率轉折（CCC）
                with col3:
                    st.markdown("### 💐經營效率轉折（CCC）")
                    
                    if 'CCC' in df.columns:
                        # 計算 CCC 趨勢
                        ccc_values = df['CCC'].dropna()
                        
                        if len(ccc_values) >= 2:
                            slope = (ccc_values.iloc[-1] - ccc_values.iloc[0]) / len(ccc_values)
                            
                            if slope < -5:
                                verdict = "營運翻轉✨"
                                color = "green"
                                detail = f"CCC 持續下降 (趨勢: {slope:.1f}) → 營運效率明顯改善"
                            elif slope < 0:
                                verdict = "逐步改善⬇️"
                                color = "blue"
                                detail = f"CCC 溫和下降 (趨勢: {slope:.1f}) → 營運體質優化"
                            else:
                                verdict = "效率惡化⚠️"
                                color = "red"
                                detail = f"CCC 上升 (趨勢: {slope:.1f}) → 資金效率下降"
                            
                            st.markdown(f"**判決**: <span style='color:{color}'>{verdict}</span>", unsafe_allow_html=True)
                            st.markdown(f"**分析**: {detail}")
                            
                            # 圖表
                            fig = px.line(
                                x=df['季度_label'],
                                y=df['CCC'],
                                markers=True,
                                title="CCC 營運資金循環趨勢",
                                labels={'x': '季度', 'y': 'CCC（天）'}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
                # 低估值純度檢查
                with col4:
                    st.markdown("### 💐低估值純度檢查")
                    
                    pe_col = get_column_by_keyword(df, ['P/E', '當季季底P/E'])
                    
                    if pe_col is not None:
                        latest_pe = get_numeric_value(df.iloc[-1, pe_col])
                        
                        # 簡化版本：根據 P/E 判斷
                        if latest_pe < 10:
                            verdict = "純低估💎"
                            color = "green"
                            detail = f"P/E = {latest_pe:.1f}（極低） → 高機會低估"
                        elif latest_pe < 15:
                            verdict = "相對純⭐"
                            color = "blue"
                            detail = f"P/E = {latest_pe:.1f}（中低） → 可考慮"
                        elif latest_pe < 20:
                            verdict = "有隱患⚠️"
                            color = "orange"
                            detail = f"P/E = {latest_pe:.1f}（中等） → 業外收支影響"
                        else:
                            verdict = "不夠純❌"
                            color = "red"
                            detail = f"P/E = {latest_pe:.1f}（偏高） → 低估值有限"
                        
                        st.markdown(f"**判決**: <span style='color:{color}'>{verdict}</span>", unsafe_allow_html=True)
                        st.markdown(f"**分析**: {detail}")
                        
                        # 圖表
                        fig = px.line(
                            x=df['季度_label'],
                            y=[df.iloc[i, pe_col] for i in range(len(df))],
                            markers=True,
                            title="P/E 估值趨勢",
                            labels={'x': '季度', 'y': 'P/E'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
            # ====================================================================
            # 標籤四：深度財務分析
            # ====================================================================
            with tab4:
                
                dividend_annual_data = None
                
                # 強制使用 yfinance 年末重採樣 + 智慧季度回推
                if HAS_YFINANCE:
                    try:
                        symbol = f"{stock_code}.TW"
                        ticker = yf.Ticker(symbol)
                        
                        # 官方年度股利數據
                        div_series = ticker.dividends
                        
                        if not div_series.empty:
                            # 確保沒有 timezone 問題
                            if div_series.index.tz is not None:
                                div_series = div_series.tz_localize(None)
                            
                            # ============ 偵測是否為季配息股票 ============
                            # 計算每年的股利支付次數（取最近一年作為基準）
                            current_year = datetime.now().year
                            recent_year_divs = div_series[(div_series.index.year >= current_year - 1)]
                            payments_per_year = len(recent_year_divs) // 2 if len(recent_year_divs) > 0 else 0
                            is_quarterly_payer = payments_per_year > 2  # 一年超過 2 次 = 季配息
                            
                            # ============ 智慧季度所屬年回推邏輯 ============
                            if is_quarterly_payer:
                                # 季配息股票：根據除息日月份進行年份回推
                                div_with_adjusted_year = {}
                                for ex_div_date, dividend_value in div_series.items():
                                    original_year = ex_div_date.year
                                    month = ex_div_date.month
                                    
                                    # 智慧回推規則：1-6月回推至前一年，7-12月保持當前年
                                    if month <= 6:
                                        assigned_year = original_year - 1
                                    else:
                                        assigned_year = original_year
                                    
                                    if assigned_year not in div_with_adjusted_year:
                                        div_with_adjusted_year[assigned_year] = 0
                                    div_with_adjusted_year[assigned_year] += dividend_value
                            else:
                                # 非季配息股票：使用標準年末重採樣
                                div_annual = div_series.resample('YE').sum()
                                div_with_adjusted_year = {}
                                for date, value in div_annual.items():
                                    year = date.year
                                    div_with_adjusted_year[year] = float(value)
                            
                            # 獲取完整歷史股價（用於計算年度平均股價）
                            hist_price = ticker.history(period="max")
                            if isinstance(hist_price.columns, pd.MultiIndex):
                                hist_price.columns = hist_price.columns.get_level_values(0)
                            # 確保歷史股價索引沒有時區
                            if hist_price.index.tz is not None:
                                hist_price.index = hist_price.index.tz_localize(None)
                            
                            # ============ 構建統一的 10 年年度股利數據表 ============
                            all_years = list(range(current_year - 9, current_year + 1))
                            complete_dividend_data = []
                            
                            for year in sorted(all_years, reverse=True):
                                year_start = pd.Timestamp(f"{year}-01-01")
                                year_end = pd.Timestamp(f"{year}-12-31")
                                
                                # 從調整後的股利數據取值
                                annual_dividend = div_with_adjusted_year.get(year, 0)
                                
                                # 計算該年度平均股價（用於殖利率計算）
                                year_prices = hist_price.loc[year_start:year_end, 'Close'] if 'Close' in hist_price.columns else hist_price.loc[year_start:year_end, 0]
                                avg_price = year_prices.mean() if not year_prices.empty else current_price or 1
                                
                                # 現金殖利率 = 年度股利 / 年度平均股價
                                cash_yield = (annual_dividend / avg_price * 100) if avg_price > 0 else 0
                                
                                complete_dividend_data.append({
                                    'Year': year,
                                    'CashDiv': round(annual_dividend, 2),
                                    'AvgPrice': round(avg_price, 2),
                                    'CashYield%': round(cash_yield, 2)
                                })
                            
                            dividend_annual_data = pd.DataFrame(complete_dividend_data)
                            method_name = "智慧季度所屬年回推法" if is_quarterly_payer else "年末重採樣法"
                            st.success(f"成功從 yfinance 官方財報載入 10 年年度股利數據")
                            
                            # 表格展示 - 百分之百使用同一個計算完畢的變數
                            st.markdown("### 🌺過去 10 年股利與殖利率表")
                            st.dataframe(
                                dividend_annual_data[['Year', 'CashDiv', 'AvgPrice', 'CashYield%']],
                                column_config={
                                    'Year': '年份',
                                    'CashDiv': '年度股利 (元/股)',
                                    'AvgPrice': '年度平均股價 (元)',
                                    'CashYield%': '現金殖利率 (%)'
                                },
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # 雙軸圖表 - 百分之百共用同一個變數
                            st.markdown("### 🌺股利與殖利率走勢圖")
                            fig_div = go.Figure()
                            
                            # 左軸：年度股利柱狀圖
                            fig_div.add_trace(go.Bar(
                                x=dividend_annual_data['Year'],
                                y=dividend_annual_data['CashDiv'],
                                name='年度股利',
                                marker=dict(color='#2980b9'),
                                yaxis='y1',
                                hovertemplate='<b>%{x}</b><br>年度股利: <b>%{y:.2f} 元</b><extra></extra>'
                            ))
                            
                            # 右軸：現金殖利率折線（使用平均股價計算）
                            fig_div.add_trace(go.Scatter(
                                x=dividend_annual_data['Year'],
                                y=dividend_annual_data['CashYield%'],
                                mode='lines+markers',
                                name='現金殖利率',
                                line=dict(color='#e67e22', width=3),
                                marker=dict(size=8),
                                yaxis='y2',
                                hovertemplate='<b>%{x}</b><br>殖利率: <b>%{y:.2f}%</b><extra></extra>'
                            ))
                            
                            fig_div.update_layout(
                                title=f"{stock_code} - 過去 10 年官方年度股利與現金殖利率趨勢",
                                xaxis_title="年份",
                                yaxis=dict(
                                    title="年度股利（元/股）",
                                    side='left',
                                    gridcolor='rgba(200, 200, 200, 0.2)'
                                ),
                                yaxis2=dict(
                                    title="現金殖利率（%）",
                                    overlaying='y',
                                    side='right'
                                ),
                                hovermode='x unified',
                                height=450,
                                template="plotly_white",
                                legend=dict(
                                    orientation='h',
                                    yanchor='bottom',
                                    y=1.02,
                                    xanchor='right',
                                    x=1
                                )
                            )
                            
                            st.plotly_chart(fig_div, use_container_width=True)
                        else:
                            st.warning("⚠️ yfinance 查詢失敗：暫無該股票的股利數據")
                    except Exception as e:
                        st.warning(f"⚠️ yfinance 年度股利查詢失敗：{str(e)}")
                else:
                    st.warning("⚠️ 未可用 yfinance 模塊，無法取得官方年度股利數據")
                
                st.divider()
                st.markdown("### 🌺股利計算說明")
                if dividend_annual_data is not None:
                    st.markdown("""
                    * **現金殖利率 (%)**：$$\\text{現金殖利率 (\\%)} = \\left( \\frac{\\text{年度總股利}}{\\text{年度平均股價}} \\right) \\times 100\\%$$
                    * **年度平均股價**：採用該年度所有交易日收盤價之算術平均值，避免單一除息日股價波動之偏誤。
                    """)





            
            # ====================================================================
            # 標籤五：估值預測（10 年年資料）
            # ====================================================================
            with tab5:
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🪴輸入預期參數")
                    
                    # 嘗試從 yfinance 獲取最新年度 EPS
                    latest_eps = None
                    if HAS_YFINANCE:
                        eps_history = fetch_annual_eps(stock_code)
                        if eps_history is not None and not eps_history.empty:
                            latest_eps = get_numeric_value(eps_history.iloc[0]['EPS'])
                    
                    # 備用：從 Excel 季度數據推估
                    if latest_eps is None:
                        eps_col = get_column_by_keyword(df, ['EPS', '每股盈餘'])
                        if eps_col is not None:
                            latest_eps = get_numeric_value(df.iloc[-1, eps_col])
                    
                    if latest_eps is None:
                        latest_eps = 0.0
                    
                    # 輸入框
                    expected_eps = st.number_input(
                        "預期未來全年 EPS (元)",
                        min_value=0.0,
                        value=float(latest_eps),
                        step=0.1,
                        help="輸入預期的年度每股盈餘"
                    )
                    
                    expected_pe = st.number_input(
                        "預期本益比（P/E）",
                        min_value=0.0,
                        value=15.0,
                        step=0.5,
                        help="根據產業平均本益比或歷史本益比設置"
                    )
                    
                    st.divider()
                    
                    # 計算目標價
                    target_price = expected_eps * expected_pe if expected_eps > 0 else 0
                    st.markdown(f"### 🪴目標價格")
                    if target_price > 0:
                        st.markdown(f"# **{target_price:.2f} 元**")
                        st.markdown(f"*(EPS {expected_eps:.2f} × P/E {expected_pe:.1f})*")
                    else:
                        st.warning("請輸入有效的 EPS 與 P/E 比率")
                
                with col2:
                    st.markdown("### 📈現價對比與估值分析")
                    
                    # 從 yfinance 獲取現價
                    current_price = fetch_stock_price(stock_code)
                    
                    if current_price and target_price > 0:
                        st.markdown(f"**現價**: {current_price:.2f} 元")
                        
                        # 計算漲跌
                        diff = target_price - current_price
                        pct_diff = (diff / current_price) * 100
                        
                        st.divider()
                        
                        if pct_diff > 10:
                            st.markdown(f"### 📈<span style='color:#27ae60'>低估</span>", unsafe_allow_html=True)
                            st.markdown(f"**上漲空間**: +{diff:.2f} 元 ({pct_diff:+.1f}%)")
                        elif pct_diff < -10:
                            st.markdown(f"### 📉<span style='color:#e74c3c'>高估</span>", unsafe_allow_html=True)
                            st.markdown(f"**下跌風險**: {diff:.2f} 元 ({pct_diff:+.1f}%)")
                        else:
                            st.markdown(f"### ➡️<span style='color:#3498db'>合理偏高</span>", unsafe_allow_html=True)
                            st.markdown(f"**價差**: {diff:.2f} 元 ({pct_diff:+.1f}%)")
                        
                        st.divider()
                        
                    else:
                        st.warning(f"⚠️ 無法獲取 {stock_code} 的現價或目標價計算失敗")
                
                st.divider()
                st.markdown("### 🪴近4年官方年度 EPS 數據")
                
                # 多軌真實資料校驗鏈 - 嚴格財報精準度
                eps_display_df = None
                
                if HAS_YFINANCE:
                    eps_display_df = fetch_annual_eps(stock_code)
                    if eps_display_df is not None and not eps_display_df.empty:
                        st.success(" 成功抓取4年官方年度 EPS 數據")
                        
                        # 重新命名列並排序
                        eps_display_df = eps_display_df.rename(columns={'Year': '年份', 'EPS': 'EPS (元)'})
                        eps_display_df = eps_display_df.sort_values('年份', ascending=False).reset_index(drop=True)
                        
                        # 格式化 EPS 欄位：NaN 顯示為空白，數字保留 2 位小數
                        eps_display_df['EPS (元)'] = eps_display_df['EPS (元)'].apply(
                            lambda x: f"{x:.2f}" if pd.notna(x) else ""
                        )
                        
                        st.dataframe(eps_display_df, use_container_width=True, hide_index=True)
                        
                        # 顯示缺失數據說明
                        nan_years = [int(year) for year, eps in zip(eps_display_df['年份'], eps_display_df['EPS (元)']) if eps == ""]
                        if nan_years:
                            st.info(f"💡 年份 {', '.join(map(str, sorted(nan_years, reverse=True)))} 無官方財報 EPS 數據（yfinance 底層缺失，非後端填充）")
                    else:
                        st.warning("⚠️ 無法從 yfinance 取得官方年度 EPS 數據")
                else:
                    st.warning("⚠️ 未可用 yfinance 模塊，無法取得官方年度 EPS 數據")
                
                st.divider()
                
# ==== 模式二：技術分析回測（MACD）- 圖表完全復活 ====
else:
    st.markdown("### 🐻‍❄️MACD技術分析回測")

    st.markdown("""
    <div style="font-size:0.92rem; opacity:0.92; margin-bottom: 15px;">
        系統會依股票代碼自動抓取Yahoo Finance歷史資料，在左方直接輸入股價代碼。
    </div>
    """, unsafe_allow_html=True)

# 在這裡放入策略說明，使用者點開才看得到詳細規則
    with st.expander("點擊查看：MACD 交易策略邏輯說明"):
        st.write("""
        本策略利用 MACD 柱狀體 (Histogram) 捕捉市場動能轉折：
        
        * **進場邏輯 (買入)**：
          - 監測 MACD 綠色柱狀圖（負值）。
          - 當綠柱達到波段最低點後，連續 **3 根** 柱狀體數值變小（收斂）。
          - 於第 **4 根** K 棒開盤時執行買入。
          
        * **出場邏輯 (賣出)**：
          - 監測 MACD 紅色柱狀圖（正值）。
          - 當紅柱達到波段最高點後，連續 **3 根** 柱狀體數值變小（收斂）。
          - 於第 **4 根** K 棒開盤時執行賣出。
        """)

    # 接著再放你原本的回測設定與按鈕

    st.markdown("### 回測設定")
    col_period, col_sma = st.columns([1, 2])
    with col_period:
        period_label = st.selectbox(
            "下載期間",
            ["1 年", "2 年", "5 年", "10 年", "完整歷史"],
            index=2
        )
    period_map = {
        "1 年": "1y",
        "2 年": "2y",
        "5 年": "5y",
        "10 年": "10y",
        "完整歷史": "max"
    }

    with col_sma:
        sma_cols = st.columns(4)
        with sma_cols[0]:
            show_sma_week = st.checkbox("周線 5 日", value=True)
        with sma_cols[1]:
            show_sma_month = st.checkbox("月線 20 日", value=True)
        with sma_cols[2]:
            show_sma_quarter = st.checkbox("季線 60 日", value=True)
        with sma_cols[3]:
            show_sma_year = st.checkbox("年線 240 日", value=True)

# 🌟 就在這裡！我幫妳把 CSS 樣式直接插在按鈕上方，這樣就能強制把字體上色囉！
    st.markdown("""
        <style>
        /* 鎖定並修改回測按鈕的文字顏色與外觀 */
        div.stButton > button {
            color: #1E3A8A !important;     /* 🌟 變成明顯的深藍色粗體字 */
            font-weight: 700 !important;   
            font-size: 1.05rem !important; 
            border: 1px solid #CBD5E1 !important; /* 加個精緻的淡淡灰色邊框 */
            background-color: #F8FAFC !important; /* 保持乾淨的底色 */
        }
        /* 滑鼠移過去（Hover）時的帥氣互動反白效果 */
        div.stButton > button:hover {
            color: #FFFFFF !important;     
            background-color: #1E3A8A !important; 
            border-color: #1E3A8A !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    run_backtest = st.button("開始執行執行MACD回測", use_container_width=True)

    if run_backtest:
        if not stock_code or not str(stock_code).strip():
            st.error("請先在左側輸入股票代碼，例如 2330 或 2317。")
        elif not HAS_YFINANCE:
            st.error("未安裝 yfinance，無法從網路下載股價資料。")
        else:
            with st.spinner("正在從 Yahoo Finance 下載股價資料並執行 MACD 回測..."):
                try:
                    data_clean, yf_symbol = download_stock_history_for_macd(
                        stock_code,
                        period=period_map[period_label]
                    )

                    if data_clean is None or data_clean.empty:
                        st.error(f"無法下載 `{stock_code}` 的股價資料，請確認股票代碼是否正確。")
                    elif len(data_clean) < 60:
                        st.error(f"下載到的資料只有 {len(data_clean)} 筆，資料量不足以執行 MACD 回測。")
                    else:
                        project_path = LAST_FINAL_PROJECT_PATH
                        if str(project_path) not in sys.path:
                            sys.path.insert(0, str(project_path))
                        from strategy import backtest_macd

                        equity_df, stats_summary, signal = backtest_macd(data_clean)

                        if equity_df is None or stats_summary is None:
                            st.error("回測返回空結果，可能是資料不足或策略模組無法處理此資料。")
                        else:
                            start_date = data_clean.index.min().date()
                            end_date = data_clean.index.max().date()
                            current_price = float(data_clean['Close'].iloc[-1])

                            st.success(f"已下載 `{yf_symbol}` 共 {len(data_clean)} 筆資料（{start_date} ~ {end_date}）")
                            st.toast("股價資料載入完成", icon="📥")

                            metrics = stats_summary.get('metrics') or {}
                            initial_equity = metrics.get('initial_equity', 1000000)
                            final_equity = metrics.get('final_equity', None)
                            if final_equity is None:
                                try:
                                    final_equity = float(equity_df['Equity'].iloc[-1]) if 'Equity' in equity_df.columns else None
                                except Exception:
                                    final_equity = None

                            try:
                                initial_equity = float(initial_equity)
                            except Exception:
                                initial_equity = 1000000.0

                            if final_equity is not None:
                                try:
                                    final_equity = float(final_equity)
                                    total_return = round(((final_equity / initial_equity) - 1.0) * 100.0, 2)
                                except Exception:
                                    total_return = stats_summary.get('total_return', metrics.get('total_return_pct', 0)) or 0
                            else:
                                total_return = stats_summary.get('total_return', metrics.get('total_return_pct', 0)) or 0

                            annualized = stats_summary.get('annualized_return', metrics.get('CAGR_pct', 0)) or 0
                            max_drawdown = stats_summary.get('max_drawdown', metrics.get('max_drawdown_pct', 0)) or 0
                            trades_count = stats_summary.get('trades', metrics.get('trades_executed', 0)) or 0
                            win_rate = stats_summary.get('win_rate', 0) or 0

                            def format_money(value):
                                try:
                                    return f"{float(value):,.0f} 元"
                                except (TypeError, ValueError):
                                    return "-"

                            def format_percent(value):
                                try:
                                    return f"{float(value):.2f}%"
                                except (TypeError, ValueError):
                                    return "-"

                            st.markdown("### 🐾回測完成")
                            performance_rows = [
                                {"項目": "股票代號", "數值": yf_symbol},
                                {"項目": "資料期間", "數值": f"{start_date} ~ {end_date}"},
                                {"項目": "資料筆數", "數值": f"{len(data_clean):,} 筆"},
                                {"項目": "最新收盤價", "數值": f"{current_price:.2f} 元"},
                                {"項目": "初始資金", "數值": format_money(initial_equity)},
                                {"項目": "最終資產", "數值": format_money(final_equity)},
                                {"項目": "總報酬率", "數值": format_percent(total_return)},
                                {"項目": "年化報酬率", "數值": format_percent(annualized)},
                                {"項目": "最大回撤", "數值": format_percent(max_drawdown)},
                                {"項目": "勝率", "數值": format_percent(win_rate)},
                                {"項目": "交易次數", "數值": f"{int(trades_count)} 次"},
                            ]
                            st.dataframe(
                                pd.DataFrame(performance_rows),
                                use_container_width=True,
                                hide_index=True
                            )


                            st.divider()
                            st.markdown("### 🐾股價圖與 MACD 技術分析圖")
                            plot_data = data_clean.copy()
                            trades_detail = stats_summary.get('trades_detail', [])
                            fig = make_macd_figure_plotly(
                                plot_data,
                                show_sma_week=show_sma_week,
                                show_sma_month=show_sma_month,
                                show_sma_quarter=show_sma_quarter,
                                show_sma_year=show_sma_year,
                                trades_detail=trades_detail,
                                title=f"{yf_symbol} 股價圖與 MACD 技術分析圖"
                            )
                            if fig is not None:
                                plot_html = fig.to_html(
                                    include_plotlyjs=True,
                                    full_html=False,
                                    config={'responsive': True}
                                )
                                st.components.v1.html(
                                    plot_html,
                                    height=900,
                                    scrolling=True
                                )
                                st.toast("圖表已更新", icon="📈")

                            st.divider()
                            st.markdown("### 🐾交易明細表")
                            if trades_detail:
                                trades_df = pd.DataFrame(trades_detail).rename(columns={
                                    'entry_time': '進場時間',
                                    'exit_time': '出場時間',
                                    'entry_price': '買入價',
                                    'exit_price': '賣出價',
                                    '報酬': '報酬率',
                                    '損益': '損益',
                                    'size': '股數'
                                })
                                st.dataframe(trades_df, use_container_width=True, hide_index=True)
                            else:
                                st.info("此期間沒有產生完整買賣交易。")

                            with st.expander("查看計算細節"):
                                detail_rows = [
                                    {"項目": "總報酬率公式", "內容": f"({final_equity:,.0f} / {initial_equity:,.0f}) - 1 = {total_return:.2f}%" if final_equity is not None else "-"},
                                    {"項目": "年化報酬率公式", "內容": stats_summary.get('annualized_formula') or "-"},
                                    {"項目": "夏普比率", "內容": stats_summary.get('sharpe') if stats_summary.get('sharpe') is not None else "-"},
                                ]
                                max_drawdown_info = stats_summary.get('max_drawdown_info') or {}
                                if max_drawdown_info:
                                    detail_rows.extend([
                                        {"項目": "最大回撤高點日期", "內容": max_drawdown_info.get('peak_date', '-')},
                                        {"項目": "最大回撤低點日期", "內容": max_drawdown_info.get('trough_date', '-')},
                                    ])
                                st.dataframe(
                                    pd.DataFrame(detail_rows),
                                    use_container_width=True,
                                    hide_index=True
                                )

                except Exception as e:
                    st.error(f"回測執行錯誤：{e}")
                    import traceback
                    st.text(traceback.format_exc())