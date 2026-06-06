import streamlit as st
from datetime import date
from modules.auth import get_current_user
from modules.board_ops import (
    get_personal_tasks, create_personal_task, toggle_personal_task, delete_personal_task,
    add_personal_checklist_item, toggle_personal_checklist_item,
    get_personal_notes, save_personal_note, delete_personal_note,
)
from modules.ui_components import page_header, PRIORITY_COLORS, ICONS

def show_personal_page():
    user = get_current_user()
    page_header("Área Pessoal", f"Sua área privada, {user['name'].split()[0]}. Apenas você pode visualizar este conteúdo.")

    tab1, tab2 = st.tabs(["Minhas Tarefas", "Notas e Anotações"])

    # ═══════════════════════════════════════════════════════════════
    # TAB 1 — TASKS
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        with st.expander("Nova Tarefa Pessoal", expanded=False):
            with st.form("new_pt"):
                pt_title = st.text_input("Título")
                pt_desc  = st.text_area("Descrição", height=72)
                pa, pb   = st.columns(2)
                with pa: pt_due  = st.date_input("Prazo", value=None)
                with pb: pt_prio = st.selectbox("Prioridade", ["média","alta","crítica","baixa"])
                if st.form_submit_button("Criar Tarefa", use_container_width=True):
                    if pt_title:
                        create_personal_task(user["id"], pt_title.strip(), pt_desc,
                                             str(pt_due) if pt_due else None, pt_prio)
                        st.rerun()
                    else:
                        st.error("Título obrigatório.")

        tasks   = get_personal_tasks(user["id"])
        pending = [t for t in tasks if not t["completed"]]
        done_t  = [t for t in tasks if  t["completed"]]

        if not tasks:
            st.markdown(f"""
            <div class="empty-state">
                <div style="margin-bottom:10px;opacity:0.3">{ICONS['task'].replace('width="14"','width="48"').replace('height="14"','height="48"')}</div>
                <div class="empty-state-title">Nenhuma tarefa pessoal</div>
                <div class="empty-state-sub">Crie sua primeira tarefa acima</div>
            </div>""", unsafe_allow_html=True)
        else:
            if pending:
                st.markdown('<div class="section-title">Pendentes</div>', unsafe_allow_html=True)
                for t in pending:
                    _render_pt(t, user["id"])

            if done_t:
                with st.expander(f"Concluídas ({len(done_t)})", expanded=False):
                    for t in done_t:
                        _render_pt(t, user["id"])

    # ═══════════════════════════════════════════════════════════════
    # TAB 2 — NOTES
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        left, right = st.columns([2, 3], gap="medium")

        with left:
            st.markdown('<div class="section-title">Minhas Notas</div>', unsafe_allow_html=True)

            with st.expander("Nova Nota", expanded=False):
                with st.form("new_note"):
                    nt = st.text_input("Título", placeholder="Título da nota...")
                    nc = st.text_area("Conteúdo", height=100, placeholder="Escreva aqui...")
                    if st.form_submit_button("Salvar", use_container_width=True):
                        if nt:
                            save_personal_note(user["id"], nt.strip(), nc)
                            st.rerun()

            notes = get_personal_notes(user["id"])
            if not notes:
                st.markdown('<div style="color:var(--text-3);font-size:13px;padding:8px 0">Nenhuma nota criada.</div>', unsafe_allow_html=True)
            else:
                for note in notes:
                    na, nb = st.columns([5, 1])
                    with na:
                        title_short = note['title'][:30] + ("…" if len(note['title']) > 30 else "")
                        is_sel = st.session_state.get("selected_note") == note["id"]
                        st.markdown(f"""
                        <div class="pnote" style="{'border-color:var(--primary);' if is_sel else ''}">
                            <div class="pnote-title">{title_short}</div>
                            <div class="pnote-date">{str(note.get('updated_at',''))[:16]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Editar", key=f"sel_n_{note['id']}", use_container_width=True):
                            st.session_state.selected_note = note["id"]
                            st.rerun()
                    with nb:
                        if st.button(ICONS["trash"], key=f"del_n_{note['id']}", help="Excluir"):
                            delete_personal_note(note["id"], user["id"])
                            if st.session_state.get("selected_note") == note["id"]:
                                st.session_state.selected_note = None
                            st.rerun()

        with right:
            sel_id = st.session_state.get("selected_note")
            if sel_id:
                notes_map = {n["id"]: n for n in get_personal_notes(user["id"])}
                note = notes_map.get(sel_id)
                if note:
                    st.markdown(f'<div class="section-title">Editando: {note["title"][:40]}</div>', unsafe_allow_html=True)
                    with st.form(f"edit_note_{sel_id}"):
                        et = st.text_input("Título", value=note["title"])
                        ec = st.text_area("Conteúdo", value=note.get("content",""), height=320)
                        if st.form_submit_button("Salvar Nota", use_container_width=True):
                            save_personal_note(user["id"], et.strip(), ec, sel_id)
                            st.success("Nota salva.")
                            st.rerun()
                    st.markdown(f'<div style="font-size:11px;color:var(--text-3)">Última edição: {str(note.get("updated_at",""))[:16]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="empty-state" style="margin-top:40px">
                    <div style="margin-bottom:10px;opacity:0.3">{ICONS['note'].replace('width="14"','width="48"').replace('height="14"','height="48"')}</div>
                    <div class="empty-state-title">Selecione uma nota para editar</div>
                </div>""", unsafe_allow_html=True)


def _render_pt(task, user_id):
    pcolor   = PRIORITY_COLORS.get(task.get("priority","média"), "#8A9AB0")
    today    = str(date.today())
    due      = task.get("due_date") or ""
    overdue  = due and due < today and not task["completed"]
    checklist = task.get("checklist", [])
    done_c   = sum(1 for c in checklist if c["completed"])

    done_class = "ptask-done" if task["completed"] else ""
    title_class = "ptask-title-done" if task["completed"] else "ptask-title"

    date_html = ""
    if overdue:
        date_html = f'<span class="overdue-tag" style="font-size:10px">{ICONS["warning"]} {due}</span>'
    elif due:
        date_html = f'<span style="font-size:11px;color:var(--text-3)">{ICONS["calendar"]} {due}</span>'

    checklist_html = f'<span style="font-size:11px;color:var(--text-3)">{ICONS["check"]} {done_c}/{len(checklist)}</span>' if checklist else ""

    st.markdown(f"""
    <div class="ptask {done_class}" style="border-left:3px solid {pcolor}">
        <div style="flex:1">
            <div class="{title_class}">{task['title']}</div>
            {f'<div style="font-size:12px;color:var(--text-3);margin-top:2px">{task["description"][:80]}</div>' if task.get("description") else ""}
            <div style="display:flex;gap:8px;margin-top:4px;align-items:center">{date_html}{checklist_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ca, cb, cc = st.columns([1,1,1])
    with ca:
        label = "Reabrir" if task["completed"] else "Concluir"
        if st.button(label, key=f"tog_{task['id']}", use_container_width=True):
            toggle_personal_task(task["id"]); st.rerun()
    with cb:
        if not task["completed"]:
            with st.popover("+ Item"):
                ni = st.text_input("Novo item", key=f"ni_pt_{task['id']}", label_visibility="collapsed", placeholder="Item do checklist...")
                if st.button("Adicionar", key=f"add_pti_{task['id']}"):
                    if ni: add_personal_checklist_item(task["id"], ni); st.rerun()
    with cc:
        if st.button(ICONS["trash"], key=f"del_pt_{task['id']}", use_container_width=True, help="Excluir"):
            delete_personal_task(task["id"]); st.rerun()

    # Checklist items
    if checklist and not task["completed"]:
        for item in checklist:
            ia, _ = st.columns([10,1])
            with ia:
                val = st.checkbox(item["text"], value=bool(item["completed"]), key=f"pchk_{item['id']}")
                if val != bool(item["completed"]):
                    toggle_personal_checklist_item(item["id"]); st.rerun()
