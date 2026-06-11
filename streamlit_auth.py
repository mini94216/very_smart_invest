import bcrypt
import pandas as pd
# 這裡匯入你剛剛建立的新檔名
from streamlit_supabase_client import supabase 

# =========================
# 註冊帳號
# =========================
def register_user(userid: str, password: str) -> bool:
    try:
        # 將密碼加密 (加鹽處理)
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # 寫入 Supabase
        supabase.table("users").insert({
            "userid": userid,
            "password": hashed_pw
        }).execute()
        
        return True
    except Exception as e:
        print(f"註冊失敗: {e}")
        return False

# =========================
# 登入驗證
# =========================
def verify_login(userid: str, password: str) -> str:
    try:
        # 從 Supabase 查詢使用者
        result = supabase.table("users").select("*").eq("userid", userid).execute()
        
        # 如果找不到帳號 (資料筆數為 0)
        if len(result.data) == 0:
            return "user_not_found"
        
        user = result.data[0]
        
        # 比對加密後的密碼
        if bcrypt.checkpw(password.encode(), user["password"].encode()):
            return "success"
            
        return "wrong_password"
        
    except Exception as e:
        print(f"登入過程錯誤: {e}")
        return "user_not_found"

# =========================
# 檢查帳號是否已存在 (用於註冊前檢查)
# =========================
def check_user_exists(userid: str) -> bool:
    try:
        result = supabase.table("users").select("userid").eq("userid", userid).execute()
        return len(result.data) > 0
    except:
        return False

# =========================
# 取得會員總數 (管理後台用)
# =========================
def get_user_count():
    try:
        result = supabase.table("users").select("id", count="exact").execute()
        return len(result.data)
    except:
        return 0

# =========================
# 取得所有會員清單 (管理後台用)
# =========================
def get_all_users():
    try:
        result = supabase.table("users").select("userid, created_at").order("created_at", desc=True).execute()
        return pd.DataFrame(result.data)
    except:
        return pd.DataFrame()