import hashlib
import streamlit as st
from modules.database import get_connection
from datetime import datetime

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def login(login_str: str, password: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE login=? AND active=1", (login_str,))
    user = c.fetchone()
    if user and verify_password(password, user["password_hash"]):
        c.execute("UPDATE users SET last_login=? WHERE id=?",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"]))
        conn.commit()
        log_action(user["id"], "login", f"Login realizado", conn=conn)
        conn.close()
        return dict(user)
    conn.close()
    return None

def logout():
    if "user" in st.session_state:
        log_action(st.session_state.user["id"], "logout", "Logout realizado")
    for key in ["user", "current_board", "selected_card"]:
        if key in st.session_state:
            del st.session_state[key]

def get_current_user():
    return st.session_state.get("user")

def require_role(*roles):
    user = get_current_user()
    if not user:
        return False
    return user["role"] in roles

def log_action(user_id, action, detail=None, conn=None):
    close = False
    if conn is None:
        conn = get_connection()
        close = True
    try:
        conn.execute("INSERT INTO system_logs (user_id, action, detail) VALUES (?,?,?)",
                     (user_id, action, detail))
        conn.commit()
    except:
        pass
    if close:
        conn.close()

# ---- User CRUD ----
def get_all_users():
    conn = get_connection()
    users = conn.execute("SELECT * FROM users WHERE active=1 ORDER BY name").fetchall()
    conn.close()
    return [dict(u) for u in users]

def get_user_by_id(uid):
    conn = get_connection()
    u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(u) if u else None

def create_user(name, login_str, password, role, sector, position):
    conn = get_connection()
    try:
        conn.execute("""INSERT INTO users (name, login, password_hash, role, sector, position)
                        VALUES (?,?,?,?,?,?)""",
                     (name, login_str, hash_password(password), role, sector, position))
        conn.commit()
        conn.close()
        return True, "Usuário criado com sucesso"
    except Exception as e:
        conn.close()
        return False, str(e)

def update_user(uid, name, role, sector, position):
    conn = get_connection()
    conn.execute("UPDATE users SET name=?, role=?, sector=?, position=? WHERE id=?",
                 (name, role, sector, position, uid))
    conn.commit()
    conn.close()

def change_password(uid, new_password):
    conn = get_connection()
    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password), uid))
    conn.commit()
    conn.close()

def deactivate_user(uid):
    conn = get_connection()
    conn.execute("UPDATE users SET active=0 WHERE id=?", (uid,))
    conn.commit()
    conn.close()
