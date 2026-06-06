import streamlit as st
from datetime import datetime, date
from modules.auth import get_current_user, require_role
from modules.board_ops import (
    get_board, get_columns, get_cards_by_column, create_column, update_column, delete_column,
    create_card, move_card, archive_card, get_card, update_card,
    get_comments, add_comment, get_checklists, add_checklist, add_checklist_item,
    toggle_checklist_item, delete_checklist_item, get_card_history, get_card_labels,
    set_card_labels, get_labels, add_label, get_all_cards_filtered,
)
from modules.auth import get_all_users
from modules.ui_components import (
    page_header, priority_pill, label_chip, avatar, icon, ICONS,
    PRIORITY_COLORS, PRIORITY_ICON,
)

def show_kanban_page():
    user = get_current_user()
    board_id = st.session_state.get("current_board")
    if not board_id:
        st.warning("Nenhum quadro selecionado.")
        if st.button("Voltar aos Quadros"):
            st.session_state.page = "boards"
            st.rerun()
        return

    board = get_board(board_id)
    if not board:
        st.error("Quadro não encontrado.")
        return

    all_users = get_all_users()
    user_map  = {u["id"]: u["name"] for u in all_users}
    columns   = get_columns(board_id)

    # ── Header ──────────────────────────────────────────────────────────────
    h1, h2, h3 = st.columns([5, 1, 1])
    with h1:
        bcolor = board.get("color","#C0392B")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
            <div style="width:12px;height:12px;background:{bcolor};border-radius:3px;flex-shrink:0"></div>
            <div class="pg-title">{board['name']}</div>
        </div>
        {f'<div class="pg-sub">{board["description"]}</div>' if board.get("description") else ""}
        """, unsafe_allow_html=True)
    with h2:
        if st.button(f"{ICONS['back']} Quadros", use_container_width=True):
            st.session_state.page = "boards"
            st.rerun()
    with h3:
        show_filter = st.toggle("Filtros", key="kbfilter")

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    # ── Filters ─────────────────────────────────────────────────────────────
    if show_filter:
        with st.container():
            st.markdown('<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;margin-bottom:12px">', unsafe_allow_html=True)
            fc = st.columns(5)
            with fc[0]: f_search   = st.text_input("Buscar", placeholder="Título...", label_visibility="visible")
            with fc[1]:
                resp_opts = [None] + [u["id"] for u in all_users]
                f_resp = st.selectbox("Responsável", resp_opts,
                    format_func=lambda x: "Todos" if x is None else user_map.get(x,""))
            with fc[2]: f_prio = st.selectbox("Prioridade", [None,"crítica","alta","média","baixa"],
                    format_func=lambda x: "Todas" if x is None else x.capitalize())
            with fc[3]: f_sector  = st.text_input("Setor", placeholder="Setor...")
            with fc[4]: f_overdue = st.checkbox("Somente atrasadas")
            st.markdown('</div>', unsafe_allow_html=True)

            results = get_all_cards_filtered(board_id=board_id,
                responsible_id=f_resp, sector=f_sector or None,
                priority=f_prio, search=f_search or None, overdue_only=f_overdue)
            st.markdown(f'<div class="section-title">{len(results)} tarefa(s) encontrada(s)</div>', unsafe_allow_html=True)
            for fc_card in results:
                pcolor = PRIORITY_COLORS.get(fc_card.get("priority","média"), "#8A9AB0")
                over   = fc_card.get("due_date") and fc_card["due_date"] < str(date.today()) and fc_card.get("status") != "concluído"
                st.markdown(f"""
                <div class="kb-card" style="margin-bottom:6px">
                    <div class="kb-card-stripe" style="background:{pcolor}"></div>
                    <div class="kb-card-title">{fc_card['title']}</div>
                    <div class="kb-card-footer">
                        <span style="font-size:11px;color:var(--text-3)">{ICONS['board']} {fc_card.get('column_name','')}</span>
                        {f'<span style="font-size:11px;color:var(--text-3)">{ICONS["user"]} {fc_card.get("responsible_name","")}</span>' if fc_card.get("responsible_name") else ""}
                        {'<span class="overdue-tag">' + ICONS["warning"] + ' Atrasada</span>' if over else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Abrir #{fc_card['id']}", key=f"flt_{fc_card['id']}"):
                    st.session_state.selected_card = fc_card["id"]
                    st.session_state.show_card_modal = True
                    st.rerun()
            st.markdown("---")

    # ── Card modal ──────────────────────────────────────────────────────────
    if st.session_state.get("show_card_modal") and st.session_state.get("selected_card"):
        _card_detail(st.session_state.selected_card, board_id, user, all_users, user_map)
        st.markdown("---")

    # ── Column manager ───────────────────────────────────────────────────────
    if require_role("administrador","gestor"):
        with st.expander("Gerenciar Colunas", expanded=False):
            for col in columns:
                cc = st.columns([3,2,1,1])
                with cc[0]: nn = st.text_input("", value=col["name"], key=f"cn_{col['id']}", label_visibility="collapsed")
                with cc[1]: nc = st.color_picker("", value=col.get("color","#C0392B"), key=f"cc_{col['id']}", label_visibility="collapsed")
                with cc[2]:
                    if st.button(ICONS["save"], key=f"sc_{col['id']}", help="Salvar"):
                        update_column(col["id"], nn, nc); st.rerun()
                with cc[3]:
                    if st.button(ICONS["trash"], key=f"dc_{col['id']}", help="Excluir"):
                        delete_column(col["id"]); st.rerun()

            st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            na, nb = st.columns([4,1])
            with na: new_col_name = st.text_input("Nova coluna", placeholder="Nome da coluna...", label_visibility="collapsed")
            with nb:
                if st.button("Adicionar", key="add_col"):
                    if new_col_name:
                        create_column(board_id, new_col_name.strip()); st.rerun()

    # ── Kanban columns ──────────────────────────────────────────────────────
    if not columns:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-title">Nenhuma coluna criada</div>
            <div class="empty-state-sub">Use "Gerenciar Colunas" acima para criar as colunas do seu quadro</div>
        </div>""", unsafe_allow_html=True)
        return

    board_cols = st.columns(len(columns), gap="small")
    for idx, col in enumerate(columns):
        cards = get_cards_by_column(col["id"])
        with board_cols[idx]:
            col_color = col.get("color","#C0392B")
            st.markdown(f"""
            <div class="kb-column">
                <div class="kb-col-header" style="border-bottom-color:{col_color}40">
                    <span class="kb-col-title">
                        <span style="width:8px;height:8px;background:{col_color};border-radius:50%;display:inline-block"></span>
                        {col['name']}
                    </span>
                    <span class="kb-count">{len(cards)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for card in cards:
                _render_card(card, col, columns, user, user_map, board_id)

            # Add card
            if require_role("administrador","gestor","colaborador"):
                with st.expander(f"+ Nova tarefa", expanded=False):
                    with st.form(f"nc_{col['id']}"):
                        ct = st.text_input("Título", key=f"ct_{col['id']}")
                        cd = st.text_area("Descrição", key=f"cd_{col['id']}", height=68)
                        ro = [None]+[u["id"] for u in all_users]
                        cr = st.selectbox("Responsável", ro,
                            format_func=lambda x: "Nenhum" if x is None else user_map.get(x,""),
                            key=f"cr_{col['id']}")
                        cp = st.selectbox("Prioridade", ["média","alta","crítica","baixa"], key=f"cp_{col['id']}")
                        cd2 = st.date_input("Prazo", value=None, key=f"cd2_{col['id']}")
                        if st.form_submit_button("Criar Tarefa", use_container_width=True):
                            if ct:
                                create_card(col["id"], board_id, ct.strip(), cd, cr,
                                            user["id"], None, cp, str(cd2) if cd2 else None, user["id"])
                                st.rerun()
                            else:
                                st.error("Título obrigatório")


def _render_card(card, current_col, all_columns, user, user_map, board_id):
    pcolor   = PRIORITY_COLORS.get(card.get("priority","média"), "#8A9AB0")
    card_id  = card["id"]
    today    = str(date.today())
    due      = card.get("due_date") or ""
    overdue  = due and due < today and card.get("status") != "concluído"
    due_soon = due and today <= due and not overdue
    pct      = card.get("completion_percent", 0) or 0
    responsible = card.get("responsible_name","")
    labels   = get_card_labels(card_id)

    # Build date badge
    if overdue:
        date_html = f'<span class="kb-date-badge kb-date-over">{ICONS["warning"]} {due}</span>'
    elif due_soon:
        date_html = f'<span class="kb-date-badge kb-date-warn">{ICONS["calendar"]} {due}</span>'
    elif due:
        date_html = f'<span class="kb-date-badge kb-date-ok">{ICONS["calendar"]} {due}</span>'
    else:
        date_html = ""

    label_html = " ".join(label_chip(l["name"], l["color"]) for l in labels)

    desc_html = ""
    if card.get("description"):
        desc = card["description"][:70]
        if len(card["description"]) > 70: desc += "…"
        desc_html = f'<div class="kb-card-desc">{desc}</div>'

    user_chip = ""
    if responsible:
        initials = "".join(p[0].upper() for p in responsible.split()[:2])
        user_chip = f'<span class="kb-user-chip"><span class="kb-avatar">{initials}</span> {responsible}</span>'

    progress_html = ""
    if pct > 0:
        progress_html = f'<div class="kb-progress"><div class="kb-progress-fill" style="width:{pct}%"></div></div>'

    st.markdown(f"""
    <div class="kb-card">
        <div class="kb-card-stripe" style="background:{pcolor}"></div>
        <div class="kb-card-title">{card['title']}</div>
        {desc_html}
        {f'<div style="margin:4px 0;display:flex;flex-wrap:wrap;gap:4px">{label_html}</div>' if labels else ""}
        <div class="kb-card-footer">
            {user_chip}
            {date_html}
        </div>
        {progress_html}
    </div>
    """, unsafe_allow_html=True)

    # Action row — open + move
    ac1, ac2 = st.columns([1,1])
    with ac1:
        if st.button("Abrir", key=f"op_{card_id}", use_container_width=True):
            st.session_state.selected_card = card_id
            st.session_state.show_card_modal = True
            st.rerun()
    with ac2:
        move_opts = [c for c in all_columns if c["id"] != current_col["id"]]
        if move_opts:
            dest = st.selectbox("",
                [None]+[c["id"] for c in move_opts],
                format_func=lambda x: "Mover para..." if x is None else next((c["name"] for c in all_columns if c["id"]==x),""),
                key=f"mv_{card_id}", label_visibility="collapsed")
            if dest:
                move_card(card_id, dest, user["id"])
                st.rerun()


def _card_detail(card_id, board_id, user, all_users, user_map):
    card = get_card(card_id)
    if not card:
        st.session_state.show_card_modal = False
        return

    labels      = get_labels(board_id)
    card_labels = get_card_labels(card_id)
    card_lids   = [l["id"] for l in card_labels]

    with st.container():
        st.markdown(f"""
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-xl);
                    padding:20px 22px;margin-bottom:12px;box-shadow:var(--shadow-sm)">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px">
                <div style="font-size:17px;font-weight:800;color:var(--text)">{card['title']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        close_col, _ = st.columns([1, 5])
        with close_col:
            if st.button("Fechar", key="close_modal"):
                st.session_state.show_card_modal = False
                st.session_state.selected_card   = None
                st.rerun()

        tabs = st.tabs(["Detalhes", "Checklist", "Comentários", "Etiquetas", "Histórico"])

        # ── TAB 1 DETAILS ──────────────────────────────────────────────────
        with tabs[0]:
            can_edit = require_role("administrador","gestor","colaborador")
            with st.form(f"ecard_{card_id}"):
                r1, r2 = st.columns([3,1])
                with r1: new_title = st.text_input("Título", value=card["title"])
                with r2:
                    pr = ["crítica","alta","média","baixa"]
                    new_prio = st.selectbox("Prioridade", pr,
                        index=pr.index(card.get("priority","média")))

                new_desc = st.text_area("Descrição", value=card.get("description",""), height=90)

                r2a, r2b, r2c = st.columns(3)
                with r2a:
                    ro = [None]+[u["id"] for u in all_users]
                    ci = ro.index(card.get("responsible_id")) if card.get("responsible_id") in ro else 0
                    new_resp = st.selectbox("Responsável", ro, index=ci,
                        format_func=lambda x: "Nenhum" if x is None else user_map.get(x,""))
                with r2b:
                    new_sector = st.text_input("Setor", value=card.get("sector",""))
                with r2c:
                    st_opts = ["aberto","em andamento","aguardando","concluído","cancelado"]
                    cur_st  = card.get("status","aberto")
                    new_status = st.selectbox("Status", st_opts,
                        index=st_opts.index(cur_st) if cur_st in st_opts else 0)

                r3a, r3b = st.columns(2)
                with r3a:
                    due_val = None
                    if card.get("due_date"):
                        try: due_val = datetime.strptime(card["due_date"], "%Y-%m-%d").date()
                        except: pass
                    new_due = st.date_input("Prazo", value=due_val)
                with r3b:
                    new_pct = st.slider("% Conclusão", 0, 100, int(card.get("completion_percent",0) or 0))

                if can_edit and st.form_submit_button("Salvar Alterações", use_container_width=True):
                    update_card(card_id, title=new_title, description=new_desc,
                                responsible_id=new_resp, sector=new_sector,
                                priority=new_prio, status=new_status,
                                due_date=str(new_due) if new_due else None,
                                completion_percent=new_pct)
                    st.success("Alterações salvas.")
                    st.rerun()

        # ── TAB 2 CHECKLIST ───────────────────────────────────────────────
        with tabs[1]:
            checklists = get_checklists(card_id)
            for cl in checklists:
                st.markdown(f'<div style="font-weight:700;font-size:13px;color:var(--text);margin-bottom:6px">{cl["title"]}</div>', unsafe_allow_html=True)
                items = cl["items"]
                done_c = sum(1 for i in items if i["completed"])
                if items:
                    st.progress(done_c/len(items), text=f"{done_c}/{len(items)}")
                for item in items:
                    ia, ib = st.columns([9,1])
                    with ia:
                        val = st.checkbox(item["text"], value=bool(item["completed"]), key=f"chk_{item['id']}")
                        if val != bool(item["completed"]):
                            toggle_checklist_item(item["id"]); st.rerun()
                    with ib:
                        if st.button(ICONS["trash"], key=f"dchk_{item['id']}"):
                            delete_checklist_item(item["id"]); st.rerun()
                with st.form(f"ai_{cl['id']}"):
                    ni = st.text_input("", placeholder="Adicionar item...", label_visibility="collapsed", key=f"ni_{cl['id']}")
                    if st.form_submit_button("Adicionar"):
                        if ni: add_checklist_item(cl["id"], ni); st.rerun()
                st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

            if require_role("administrador","gestor","colaborador"):
                with st.form("add_cl"):
                    cl_t = st.text_input("Nome do checklist", placeholder="Ex: Etapas de execução")
                    if st.form_submit_button("Criar Checklist"):
                        if cl_t: add_checklist(card_id, cl_t); st.rerun()

        # ── TAB 3 COMMENTS ───────────────────────────────────────────────
        with tabs[2]:
            comments = get_comments(card_id)
            if not comments:
                st.markdown('<div style="color:var(--text-3);font-size:13px;padding:8px 0">Nenhum comentário ainda.</div>', unsafe_allow_html=True)
            for cm in comments:
                uname = cm.get("user_name","?")
                initials = "".join(p[0].upper() for p in uname.split()[:2])
                st.markdown(f"""
                <div class="cmt-wrap">
                    <div class="kb-avatar" style="width:30px;height:30px;font-size:11px;margin-top:2px">{initials}</div>
                    <div class="cmt-body">
                        <div class="cmt-header">
                            <span class="cmt-name">{uname}</span>
                            <span class="cmt-time">{cm['created_at'][:16]}</span>
                        </div>
                        <div class="cmt-text">{cm['message']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.form("add_cmt"):
                msg = st.text_area("Comentário", height=80, label_visibility="collapsed", placeholder="Escreva um comentário...")
                if st.form_submit_button("Comentar", use_container_width=True):
                    if msg.strip(): add_comment(card_id, user["id"], msg.strip()); st.rerun()

        # ── TAB 4 LABELS ─────────────────────────────────────────────────
        with tabs[3]:
            if not labels:
                st.info("Nenhuma etiqueta criada para este quadro.")
            else:
                selected_ids = []
                for lbl in labels:
                    la, lb = st.columns([1,8])
                    with la: chk = st.checkbox("", value=lbl["id"] in card_lids, key=f"lbl_{lbl['id']}_{card_id}")
                    with lb: st.markdown(f'<div style="margin-top:6px">{label_chip(lbl["name"], lbl["color"])}</div>', unsafe_allow_html=True)
                    if chk: selected_ids.append(lbl["id"])
                if st.button("Salvar Etiquetas"):
                    set_card_labels(card_id, selected_ids); st.success("Etiquetas salvas."); st.rerun()

            st.markdown("---")
            with st.form("new_lbl"):
                la, lb = st.columns([3,1])
                with la: ln = st.text_input("Nova etiqueta", placeholder="Nome...")
                with lb: lc = st.color_picker("Cor", "#C0392B")
                if st.form_submit_button("Criar"):
                    if ln: add_label(board_id, ln.strip(), lc); st.rerun()

        # ── TAB 5 HISTORY ────────────────────────────────────────────────
        with tabs[4]:
            history = get_card_history(card_id)
            if not history:
                st.markdown('<div style="color:var(--text-3);font-size:13px">Nenhum histórico registrado.</div>', unsafe_allow_html=True)
            else:
                action_icons = {"criação": ICONS["plus"], "movimentação": ICONS["move"],
                                "comentário": ICONS["comment"], "arquivamento": ICONS["archive"],
                                "alteração": ICONS["edit"]}
                for h in history:
                    h = dict(h)
                    ico = action_icons.get(h.get("action",""), ICONS["info"])
                    uname = h.get("user_name") or "Sistema"
                    st.markdown(f"""
                    <div class="hist-row">
                        <div class="hist-icon">{ico}</div>
                        <div>
                            <div class="hist-text">
                                <strong>{uname}</strong> — {h.get('action','')}
                                {f'<br><span style="color:var(--text-3)">{h.get("detail","")}</span>' if h.get("detail") else ""}
                            </div>
                            <div class="hist-meta">{str(h.get('created_at',''))[:16]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
