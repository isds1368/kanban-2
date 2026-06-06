import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import init_database, seed_default_data
from modules.auth import get_current_user, logout
from modules.ui_components import inject_css, ICONS, ROLE_LABELS

init_database()
seed_default_data()

st.set_page_config(
    page_title="KanbanPro",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%23C0392B' d='M4 5h3v14H4zm6 0h3v8h-3zm6 0h3v11h-3z'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Must run before inject_css so the sidebar-lock styles load first
st.markdown("""
<style>
/* ── Lock sidebar — hide all collapse/expand controls ─────────────────── */
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarNavCollapseIcon"],
[data-testid="stSidebarNavExpandIcon"],
button[kind="header"] {
    display:          none !important;
    visibility:       hidden !important;
    pointer-events:   none !important;
    width:            0 !important;
    height:           0 !important;
    overflow:         hidden !important;
}
[data-testid="stSidebar"] {
    min-width: 224px !important;
    max-width: 224px !important;
    width:     224px !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; overflow-x: hidden !important; }

/* ── Sidebar nav buttons ───────────────────────────────────────────────── */
[data-testid="stSidebar"] .stButton > button {
    background:      transparent !important;
    color:           rgba(255,255,255,0.88) !important;
    border:          none !important;
    border-radius:   6px !important;
    font-size:       13px !important;
    font-weight:     500 !important;
    text-align:      left !important;
    justify-content: flex-start !important;
    padding:         9px 14px !important;
    width:           calc(100% - 16px) !important;
    margin:          1px 8px !important;
    box-shadow:      none !important;
    transform:       none !important;
    letter-spacing:  0 !important;
    transition:      background 0.12s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.10) !important;
    transform:  none !important;
    box-shadow: none !important;
    color:      #fff !important;
}
[data-testid="stSidebar"] .stButton > button:disabled {
    background: rgba(192,57,43,0.70) !important;
    color:      #fff !important;
    opacity:    1 !important;
    font-weight: 600 !important;
    cursor:     default !important;
}
</style>
""", unsafe_allow_html=True)

inject_css()

user = get_current_user()

if not user:
    from modules.page_login import show_login_page
    show_login_page()
    st.stop()

# ── Session defaults ───────────────────────────────────────────────────────
for k, v in [("page","boards"), ("current_board",None), ("selected_card",None),
             ("show_card_modal",False), ("selected_note",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo
    st.markdown(f"""
    <div class="sb-logo">
        <div style="width:32px;height:32px;background:var(--primary);border-radius:8px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0">
            {ICONS['logo']}
        </div>
        <span class="sb-logo-text">KanbanPro</span>
    </div>
    """, unsafe_allow_html=True)

    # User chip
    initials   = "".join(p[0].upper() for p in user["name"].split()[:2])
    role_label = ROLE_LABELS.get(user["role"], user["role"])
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-avatar">{initials}</div>
        <div>
            <div class="sb-name">{user['name'].split()[0]}</div>
            <div class="sb-role">{role_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Navegação</div>', unsafe_allow_html=True)

    from modules.board_ops import count_unread_notifications, get_dashboard_stats
    unread       = count_unread_notifications(user["id"])
    current_page = st.session_state.page

    # Each item: (session_key, icon_key, display_label)
    nav_items = [
        ("boards",        "home",     "Quadros"),
        ("kanban",        "board",    "Kanban"),
        ("dashboard",     "chart",    "Dashboard"),
        ("personal",      "lock",     "Área Pessoal"),
        ("notifications", "bell",     f"Notificações{f'  ·  {unread}' if unread > 0 else ''}"),
    ]
    if user["role"] == "administrador":
        nav_items.append(("admin", "settings", "Administração"))

    for page_key, ico_key, label in nav_items:
        is_active = current_page == page_key
        # Icon + label in button text — Streamlit buttons accept plain text only,
        # so we put the icon as a unicode-safe prefix via a zero-width trick:
        # Instead, render icon+label as styled HTML above the button, then overlay.
        # Cleanest working approach: just put text in the button and rely on CSS styling.
        # We use disabled=True for the active item (CSS gives it the red highlight).
        btn_label = f"  {label}"   # leading spaces give visual indent matching the icon gap
        # Render icon separately just above (negative margin trick via CSS is unreliable;
        # instead we embed icon in a markdown row and keep button below it visually)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'padding:9px 14px;margin:1px 8px;border-radius:6px;'
            f'{"background:rgba(192,57,43,0.70);" if is_active else ""}'
            f'pointer-events:none;user-select:none;">'
            f'  <span style="line-height:0;opacity:0.85;flex-shrink:0">{ICONS[ico_key]}</span>'
            f'  <span style="font-size:13px;{"font-weight:600;" if is_active else "font-weight:500;"}'
            f'color:rgba(255,255,255,{0.98 if is_active else 0.88})">{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if not is_active:
            # Transparent clickable button placed immediately below; negative top-margin
            # pulls it up to overlap the HTML row above, making the whole row clickable.
            st.markdown('<style>[data-testid="stSidebar"] .nav-btn-overlap{margin-top:-42px!important;}</style>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="nav-btn-overlap">', unsafe_allow_html=True)
                if st.button(
                    "\u00a0",          # non-breaking space — renders as empty but not truly empty
                    key=f"nav_{page_key}",
                    use_container_width=True,
                ):
                    st.session_state.page        = page_key
                    st.session_state.show_card_modal = False
                    st.session_state.selected_card   = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Logout
    st.markdown('<div class="sb-section" style="margin-top:8px">Sistema</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;padding:9px 14px;margin:1px 8px;'
        f'border-radius:6px;pointer-events:none;user-select:none;">'
        f'  <span style="line-height:0;opacity:0.85;flex-shrink:0">{ICONS["logout"]}</span>'
        f'  <span style="font-size:13px;font-weight:500;color:rgba(255,255,255,0.88)">Sair</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    with st.container():
        st.markdown('<div class="nav-btn-overlap">', unsafe_allow_html=True)
        if st.button("\u00a0", key="nav_logout", use_container_width=True):
            logout()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer stats
    stats        = get_dashboard_stats()
    over_color   = "#E74C3C" if stats["overdue"] > 0 else "#fff"
    st.markdown(f"""
    <div class="sb-footer">
        <div class="sb-section" style="padding:0 0 4px">Status Geral</div>
        <div class="sb-stat-row">
            <div class="sb-stat">
                <div class="sb-stat-n">{stats['open']}</div>
                <div class="sb-stat-l">Abertas</div>
            </div>
            <div class="sb-stat">
                <div class="sb-stat-n" style="color:{over_color}">{stats['overdue']}</div>
                <div class="sb-stat-l">Atrasadas</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── PAGE ROUTER ────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "boards":
    from modules.page_boards import show_boards_page
    show_boards_page()
elif page == "kanban":
    if not st.session_state.get("current_board"):
        from modules.page_boards import show_boards_page
        show_boards_page()
    else:
        from modules.page_kanban import show_kanban_page
        show_kanban_page()
elif page == "dashboard":
    from modules.page_dashboard import show_dashboard_page
    show_dashboard_page()
elif page == "personal":
    from modules.page_personal import show_personal_page
    show_personal_page()
elif page == "notifications":
    from modules.page_notifications import show_notifications_page
    show_notifications_page()
elif page == "admin":
    from modules.page_admin import show_admin_page
    show_admin_page()
else:
    st.session_state.page = "boards"
    st.rerun()
