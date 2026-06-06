import streamlit as st
from modules.auth import login
from modules.ui_components import inject_css, ICONS

def show_login_page():
    inject_css()
    st.markdown("""
    <style>
    .stApp { background: #1a1a1a !important; }
    .login-wrap {
        min-height: 100vh; display:flex; align-items:center; justify-content:center;
    }
    .login-card {
        background: #FFFFFF; border-radius: 16px;
        padding: 44px 40px 40px; width: 100%; max-width: 400px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.35);
    }
    @media (prefers-color-scheme: dark) {
        .stApp { background: #111318 !important; }
        .login-card { background: #1E2128; border: 1px solid #363C47; }
        .login-card .login-title { color: #E8EAF0; }
        .login-card .login-sub   { color: #9AA5B8; }
    }
    .login-logo {
        width:44px; height:44px; background: #C0392B; border-radius:12px;
        display:flex; align-items:center; justify-content:center; margin-bottom:16px;
    }
    .login-title { font-size:22px; font-weight:800; color:#1A1D23; margin-bottom:4px; letter-spacing:-0.3px; }
    .login-sub   { font-size:13px; color:#8A9AB0; margin-bottom:28px; }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(f"""
        <div class="login-card">
            <div class="login-logo">{ICONS['logo']}</div>
            <div class="login-title">KanbanPro</div>
            <div class="login-sub">Sistema de Gestão Corporativa</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            login_input = st.text_input("Usuário", placeholder="Digite seu login")
            password_input = st.text_input("Senha", placeholder="••••••••", type="password")
            st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Entrar", use_container_width=True)

        if submitted:
            if not login_input or not password_input:
                st.error("Preencha todos os campos.")
            else:
                user = login(login_input.strip(), password_input)
                if user:
                    st.session_state.user = user
                    st.session_state.page = "boards"
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos.")

        st.markdown("""
        <div style="text-align:center;margin-top:16px;font-size:11px;color:#8A9AB0">
            KanbanPro © 2025 &nbsp;·&nbsp; Gestão Corporativa
        </div>
        """, unsafe_allow_html=True)
