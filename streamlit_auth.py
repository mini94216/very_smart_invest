import sqlite3
from pathlib import Path
from datetime import datetime

# =========================
# DB 路徑（重點：跟 app 同一顆 DB）
# =========================
DB_PATH = Path(__file__).resolve().parent / "streamlit.db"


# =========================
# 建立資料庫（只建立，不亂執行）
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# 註冊帳號
# =========================
def register_user(userid: str, password: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO users (userid, password, created_at)
            VALUES (?, ?, ?)
        """, (userid, password, created_at))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        return False

    except Exception:
        return False


# =========================
# 登入驗證（標準化回傳）
# =========================
def verify_login(userid: str, password: str) -> str:
    """
    return:
        success / wrong_password / user_not_found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT password FROM users WHERE userid = ?
    """, (userid,))

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return "user_not_found"

    if result[0] != password:
        return "wrong_password"

    return "success"


# =========================
# 檢查帳號是否存在
# =========================
def check_user_exists(userid: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM users WHERE userid = ?
    """, (userid,))

    exists = cursor.fetchone() is not None

    conn.close()
    return exists


# =========================
# 初始化（給 app 呼叫）
# =========================
init_db()