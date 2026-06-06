import streamlit as st
from modules.auth import get_current_user
from modules.board_ops import (
    get_notifications, mark_notification_read,
    mark_all_notifications_read, count_unread_notifications,
)
from modules.ui_components import page_header, ICONS

TYPE_META = {
    "info":    (ICONS["info"],    "#2980B9", "#EBF5FB"),
    "warning": (ICONS["warning"], "#E67E22", "#FEF5EC"),
    "success": (ICONS["check"],   "#27AE60", "#EAF7EF"),
    "danger":  (ICONS["warning"], "#C0392B", "#FDEDEC"),
    "comment": (ICONS["comment"], "#8E44AD", "#F5EEF8"),
    "task":    (ICONS["task"],    "#2980B9", "#EBF5FB"),
}

def show_notifications_page():
    user = get_current_user()
    page_header("Notificações", "Central de alertas e avisos do sistema")

    unread = count_unread_notifications(user["id"])

    h1, h2 = st.columns([4, 1])
    with h1:
        if unread > 0:
            st.markdown(f'<div style="font-size:13px;font-weight:600;color:#E67E22;padding:6px 0">{ICONS["bell"]} {unread} notificação(ões) não lida(s)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="font-size:13px;font-weight:600;color:#27AE60;padding:6px 0">{ICONS["check"]} Todas as notificações foram lidas</div>', unsafe_allow_html=True)
    with h2:
        if unread > 0:
            if st.button("Marcar todas como lidas", use_container_width=True):
                mark_all_notifications_read(user["id"])
                st.rerun()

    notifs = get_notifications(user["id"])

    if not notifs:
        st.markdown(f"""
        <div class="empty-state">
            <div style="margin-bottom:10px;opacity:0.3">{ICONS['bell'].replace('width="16"','width="48"').replace('height="16"','height="48"')}</div>
            <div class="empty-state-title">Nenhuma notificação</div>
            <div class="empty-state-sub">Você está em dia!</div>
        </div>""", unsafe_allow_html=True)
        return

    for notif in notifs:
        notif = dict(notif)
        ntype  = notif.get("type","info")
        ico, color, bg = TYPE_META.get(ntype, TYPE_META["info"])
        is_unread = not notif.get("read", False)
        border = f"border-left:3px solid {color};" if is_unread else ""
        bg_val = bg if is_unread else "var(--surface)"

        new_badge = f'<span style="background:{color};color:#fff;font-size:9px;padding:1px 6px;border-radius:100px;font-weight:700;margin-left:6px">NOVO</span>' if is_unread else ""

        na, nb = st.columns([9, 1])
        with na:
            st.markdown(f"""
            <div class="notif-item {'unread' if is_unread else ''}"
                 style="background:{bg_val};{border}">
                <div style="width:32px;height:32px;background:{color}22;border-radius:50%;
                            display:flex;align-items:center;justify-content:center;flex-shrink:0">
                    <span style="color:{color}">{ico}</span>
                </div>
                <div style="flex:1">
                    <div style="font-size:13px;font-weight:700;color:var(--text)">
                        {notif['title']}{new_badge}
                    </div>
                    <div style="font-size:12.5px;color:var(--text-2);margin-top:2px">{notif['message']}</div>
                    <div style="font-size:11px;color:var(--text-3);margin-top:4px">{str(notif.get('created_at',''))[:16]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with nb:
            if is_unread:
                if st.button(ICONS["check"], key=f"rd_{notif['id']}", help="Marcar como lida"):
                    mark_notification_read(notif["id"]); st.rerun()
