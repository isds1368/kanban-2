import streamlit as st
import os
from modules.auth import (
    get_current_user, require_role, get_all_users,
    create_user, update_user, deactivate_user, change_password,
)
from modules.ui_components import page_header, ROLE_LABELS, ICONS
from modules.backup import create_backup, list_backups
from modules.database import get_connection, DB_PATH

ROLE_COLORS = {
    "administrador": ("#C0392B","#FDEDEC"),
    "gestor":        ("#8E44AD","#F5EEF8"),
    "colaborador":   ("#2980B9","#EBF5FB"),
    "leitor":        ("#8A9AB0","#F0F1F3"),
}

def show_admin_page():
    user = get_current_user()
    if not require_role("administrador"):
        st.error("Acesso negado. Apenas administradores podem acessar esta área.")
        return

    page_header("Administração", "Gestão de usuários, sistema e configurações")

    tab1, tab2, tab3, tab4 = st.tabs(["Usuários", "Backup", "Logs", "Sistema"])

    # ═══════════════════════════════════════════════════════════════
    # TAB 1 — USERS
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="section-title">Usuários do Sistema</div>', unsafe_allow_html=True)

        with st.expander("Criar Novo Usuário", expanded=False):
            with st.form("create_user"):
                ua, ub = st.columns(2)
                with ua:
                    u_name     = st.text_input("Nome Completo")
                    u_login    = st.text_input("Login")
                    u_password = st.text_input("Senha", type="password")
                with ub:
                    u_role     = st.selectbox("Perfil",
                        ["colaborador","gestor","leitor","administrador"],
                        format_func=lambda x: ROLE_LABELS[x])
                    u_sector   = st.text_input("Setor")
                    u_position = st.text_input("Cargo")

                if st.form_submit_button("Criar Usuário", use_container_width=True):
                    if u_name and u_login and u_password:
                        ok, msg = create_user(u_name.strip(), u_login.strip(),
                                              u_password, u_role, u_sector, u_position)
                        if ok:
                            st.success(msg); st.rerun()
                        else:
                            st.error(f"Erro: {msg}")
                    else:
                        st.error("Nome, login e senha são obrigatórios.")

        users = get_all_users()
        st.markdown(f'<div style="font-size:12px;color:var(--text-3);margin-bottom:10px">{len(users)} usuário(s) ativo(s)</div>', unsafe_allow_html=True)

        for u in users:
            c, bg  = ROLE_COLORS.get(u["role"], ("#8A9AB0","#F0F1F3"))
            initials = "".join(p[0].upper() for p in u["name"].split()[:2])

            with st.expander(
                f"{u['name']}  ·  {ROLE_LABELS.get(u['role'],u['role'])}  ·  {u.get('sector','') or '—'}",
                expanded=False
            ):
                info_col, form_col = st.columns([1, 2])
                with info_col:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
                        <div style="width:38px;height:38px;background:{c};border-radius:50%;
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:13px;font-weight:700;color:#fff">{initials}</div>
                        <div>
                            <div style="font-weight:700;font-size:14px;color:var(--text)">{u['name']}</div>
                            <span style="background:{bg};color:{c};padding:2px 8px;border-radius:4px;
                                         font-size:11px;font-weight:600">{ROLE_LABELS.get(u['role'],u['role'])}</span>
                        </div>
                    </div>
                    <div style="font-size:12px;color:var(--text-3);line-height:2">
                        <b style="color:var(--text-2)">Login:</b> {u['login']}<br>
                        <b style="color:var(--text-2)">Setor:</b> {u.get('sector','—') or '—'}<br>
                        <b style="color:var(--text-2)">Cargo:</b> {u.get('position','—') or '—'}<br>
                        <b style="color:var(--text-2)">Último acesso:</b> {u.get('last_login','Nunca') or 'Nunca'}
                    </div>
                    """, unsafe_allow_html=True)

                with form_col:
                    with st.form(f"edit_u_{u['id']}"):
                        en_name = st.text_input("Nome", value=u["name"])
                        en_role = st.selectbox("Perfil",
                            ["colaborador","gestor","leitor","administrador"],
                            index=["colaborador","gestor","leitor","administrador"].index(u["role"]),
                            format_func=lambda x: ROLE_LABELS[x])
                        er1, er2 = st.columns(2)
                        with er1: en_sector   = st.text_input("Setor",   value=u.get("sector","")   or "")
                        with er2: en_position = st.text_input("Cargo",   value=u.get("position","") or "")
                        en_pass = st.text_input("Nova senha (em branco = manter)", type="password")

                        ec1, ec2 = st.columns(2)
                        with ec1:
                            if st.form_submit_button("Salvar", use_container_width=True):
                                update_user(u["id"], en_name, en_role, en_sector, en_position)
                                if en_pass:
                                    change_password(u["id"], en_pass)
                                st.success("Alterações salvas.")
                                st.rerun()
                        with ec2:
                            if u["id"] != user["id"]:
                                if st.form_submit_button("Desativar", use_container_width=True):
                                    deactivate_user(u["id"]); st.rerun()

    # ═══════════════════════════════════════════════════════════════
    # TAB 2 — BACKUP
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-title">Backup do Sistema</div>', unsafe_allow_html=True)

        if st.button("Criar Backup Agora"):
            with st.spinner("Criando backup..."):
                path = create_backup()
            st.success(f"Backup criado: {os.path.basename(path)}")

        st.markdown("---")
        backups = list_backups()
        if not backups:
            st.markdown('<div style="color:var(--text-3);font-size:13px">Nenhum backup encontrado.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-title">Backups Disponíveis</div>', unsafe_allow_html=True)
            for bk in backups:
                ba, bb, bc = st.columns([4,2,1])
                with ba:
                    st.markdown(f'<div style="font-size:13px;font-weight:600;color:var(--text)">{ICONS["archive"]} {bk["name"]}</div>', unsafe_allow_html=True)
                with bb:
                    st.markdown(f'<div style="font-size:12px;color:var(--text-3)">{bk["created"]} &nbsp;·&nbsp; {bk["size"]//1024} KB</div>', unsafe_allow_html=True)
                with bc:
                    with open(bk["path"],"rb") as f:
                        st.download_button(ICONS["download"], f,
                            file_name=bk["name"], mime="application/zip",
                            key=f"dl_{bk['name']}")

    # ═══════════════════════════════════════════════════════════════
    # TAB 3 — LOGS
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-title">Logs do Sistema</div>', unsafe_allow_html=True)

        conn = get_connection()
        raw_logs = conn.execute("""
            SELECT l.id, l.user_id, l.action, l.detail, l.ip_address, l.created_at,
                   u.name as user_name
            FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC LIMIT 300
        """).fetchall()
        conn.close()

        # Convert to plain dicts to avoid sqlite3.Row.get() issue
        logs = [dict(row) for row in raw_logs]

        actions = sorted(set(lg["action"] for lg in logs if lg.get("action")))
        f_action = st.selectbox("Filtrar por ação", ["todas"] + actions)

        action_icons = {
            "login":      ICONS["person"],
            "logout":     ICONS["logout"],
            "criação":    ICONS["plus"],
            "alteração":  ICONS["edit"],
            "exclusão":   ICONS["trash"],
            "movimentação": ICONS["move"],
            "arquivamento": ICONS["archive"],
            "comentário": ICONS["comment"],
        }

        visible = [lg for lg in logs if f_action == "todas" or f_action in (lg.get("action") or "")]

        if not visible:
            st.markdown('<div style="color:var(--text-3);font-size:13px">Nenhum log encontrado.</div>', unsafe_allow_html=True)

        for lg in visible:
            action  = lg.get("action") or ""
            ico_key = next((k for k in action_icons if k in action.lower()), None)
            ico     = action_icons[ico_key] if ico_key else ICONS["info"]
            uname   = lg.get("user_name") or "Sistema"
            detail  = lg.get("detail") or ""
            created = str(lg.get("created_at") or "")[:16]

            st.markdown(f"""
            <div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;
                        border-bottom:1px solid var(--border);font-size:12.5px">
                <span style="color:var(--text-3);margin-top:1px">{ico}</span>
                <div style="flex:1;color:var(--text-2)">
                    <span style="font-weight:600;color:var(--text)">{uname}</span>
                    <span> — {action}</span>
                    {f'<span style="color:var(--text-3)"> · {detail[:100]}</span>' if detail else ""}
                </div>
                <span style="color:var(--text-3);white-space:nowrap;font-size:11px">{created}</span>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # TAB 4 — SYSTEM
    # ═══════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="section-title">Informações do Sistema</div>', unsafe_allow_html=True)

        db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        conn2   = get_connection()
        total_cards  = conn2.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        total_users  = conn2.execute("SELECT COUNT(*) FROM users WHERE active=1").fetchone()[0]
        total_boards = conn2.execute("SELECT COUNT(*) FROM boards WHERE archived=0").fetchone()[0]
        total_logs   = conn2.execute("SELECT COUNT(*) FROM system_logs").fetchone()[0]
        conn2.close()

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Banco de Dados",  f"{db_size//1024} KB")
        with m2: st.metric("Usuários Ativos", total_users)
        with m3: st.metric("Quadros Ativos",  total_boards)
        with m4: st.metric("Total de Cards",  total_cards)

        st.markdown("---")

        st.markdown(f"""
        <div style="background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius-lg);
                    padding:16px 18px;font-size:13px;color:var(--text-2)">
            <div style="margin-bottom:6px"><b style="color:var(--text)">Caminho do banco:</b> <code style="font-size:12px">{DB_PATH}</code></div>
            <div style="margin-bottom:6px"><b style="color:var(--text)">Registros de log:</b> {total_logs}</div>
            <div style="margin-bottom:6px"><b style="color:var(--text)">Versão:</b> KanbanPro v2.0.0</div>
            <div><b style="color:var(--text)">Stack:</b> Python · Streamlit · SQLite</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Segurança</div>', unsafe_allow_html=True)

        with st.expander("Alterar minha senha", expanded=False):
            with st.form("chg_pw"):
                p1 = st.text_input("Nova senha", type="password")
                p2 = st.text_input("Confirmar senha", type="password")
                if st.form_submit_button("Alterar Senha", use_container_width=True):
                    if p1 and p1 == p2:
                        change_password(user["id"], p1)
                        st.success("Senha alterada com sucesso.")
                    elif p1 != p2:
                        st.error("As senhas não coincidem.")
                    else:
                        st.error("Preencha os campos de senha.")
