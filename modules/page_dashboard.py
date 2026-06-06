import streamlit as st
from datetime import date, timedelta
from modules.auth import get_current_user
from modules.board_ops import get_dashboard_stats, get_boards_for_user, get_all_cards_filtered
from modules.ui_components import page_header, PRIORITY_COLORS, ICONS

def show_dashboard_page():
    user = get_current_user()
    page_header("Dashboard Executivo", "Indicadores de produtividade e desempenho operacional")

    boards = get_boards_for_user(user["id"], user["role"])
    board_opts = {None: "Todos os Quadros"}
    board_opts.update({b["id"]: b["name"] for b in boards})

    sel = st.selectbox("Filtrar por Quadro", list(board_opts.keys()),
                       format_func=lambda x: board_opts[x])
    stats = get_dashboard_stats(sel)

    # ── KPIs ──────────────────────────────────────────────────────────────
    total_rate = round(stats["done"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
    kpi = st.columns(5, gap="small")
    kpi_data = [
        (stats["total"],  "Total de Tarefas",  "var(--primary)"),
        (stats["open"],   "Em Aberto",          "#E67E22"),
        (stats["done"],   "Concluídas",         "#27AE60"),
        (stats["overdue"],"Atrasadas",          "#C0392B"),
        (f"{total_rate}%","Taxa de Conclusão",  "#8E44AD"),
    ]
    for col, (val, label, color) in zip(kpi, kpi_data):
        with col:
            st.markdown(f"""
            <div class="dash-stat">
                <div class="dash-stat-n" style="color:{color}">{val}</div>
                <div class="dash-stat-l">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    # ── Charts row 1 ──────────────────────────────────────────────────────
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        _priority_chart(stats["by_priority"])
    with c2:
        _sector_chart(stats["by_sector"])

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    # ── Charts row 2 ──────────────────────────────────────────────────────
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        _weekly_chart(stats["weekly"])
    with c4:
        _monthly_chart(stats["monthly"])

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    # ── Responsible table ─────────────────────────────────────────────────
    _responsible_table(stats["by_responsible"])

    # ── Overdue list ──────────────────────────────────────────────────────
    if stats["overdue"] > 0:
        st.markdown('<div class="section-title">Tarefas Atrasadas</div>', unsafe_allow_html=True)
        overdue_cards = get_all_cards_filtered(board_id=sel, overdue_only=True)
        for card in overdue_cards[:20]:
            try:
                days = (date.today() - date.fromisoformat(card["due_date"])).days
            except Exception:
                days = 0
            resp = card.get("responsible_name") or "Sem responsável"
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid #F5B7B1;border-left:3px solid #C0392B;
                        border-radius:var(--radius-lg);padding:11px 16px;margin-bottom:7px;
                        display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span style="font-weight:600;color:var(--text);font-size:13px">{card['title']}</span>
                    <span style="font-size:12px;color:var(--text-3);margin-left:8px">— {resp}</span>
                </div>
                <span class="overdue-tag">{ICONS['warning']} {days} dia{'s' if days != 1 else ''} atrasada</span>
            </div>
            """, unsafe_allow_html=True)


def _chart_wrap(title, body_html):
    st.markdown(f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-xl);
                padding:18px 20px;box-shadow:var(--shadow-xs)">
        <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;
                    color:var(--text-3);margin-bottom:14px">{title}</div>
        {body_html}
    </div>
    """, unsafe_allow_html=True)


def _priority_chart(by_priority):
    if not by_priority:
        _chart_wrap("Tarefas por Prioridade", '<div style="color:var(--text-3);font-size:13px">Sem dados</div>')
        return
    total = sum(r["cnt"] for r in by_priority) or 1
    rows = ""
    for row in by_priority:
        p   = (row.get("priority") or "?")
        cnt = row["cnt"]
        pct = round(cnt / total * 100)
        color = PRIORITY_COLORS.get(p, "#8A9AB0")
        rows += f"""
        <div class="bar-row">
            <div class="bar-label"><span style="font-weight:600">{p.capitalize()}</span><span>{cnt} ({pct}%)</span></div>
            <div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>
        </div>"""
    _chart_wrap("Tarefas por Prioridade", rows)


def _sector_chart(by_sector):
    if not by_sector:
        _chart_wrap("Tarefas por Setor", '<div style="color:var(--text-3);font-size:13px">Sem dados de setor</div>')
        return
    colors = ["#C0392B","#27AE60","#2980B9","#E67E22","#8E44AD","#16A085","#D35400","#2C3E50"]
    total = sum(r["cnt"] for r in by_sector) or 1
    rows = ""
    for i, row in enumerate(by_sector):
        sector = (row.get("sector") or "Não definido")
        cnt    = row["cnt"]
        pct    = round(cnt / total * 100)
        color  = colors[i % len(colors)]
        rows += f"""
        <div class="bar-row">
            <div class="bar-label"><span style="font-weight:600">{sector}</span><span>{cnt} ({pct}%)</span></div>
            <div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>
        </div>"""
    _chart_wrap("Tarefas por Setor", rows)


def _weekly_chart(weekly):
    today = date.today()
    day_map = {(today - timedelta(days=i)).isoformat(): 0 for i in range(6, -1, -1)}
    for row in weekly:
        if row["day"] in day_map:
            day_map[row["day"]] = row["cnt"]

    max_v = max(day_map.values()) if day_map else 1
    bars = ""
    for ds, cnt in day_map.items():
        h = max(int((cnt / max(max_v, 1)) * 90), 4)
        label = ds[5:]  # MM-DD
        bars += f"""
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px">
            <span style="font-size:10px;font-weight:700;color:var(--primary);min-height:14px">{cnt if cnt else ''}</span>
            <div style="width:100%;background:var(--primary);border-radius:4px 4px 0 0;height:{h}px;opacity:0.85"></div>
            <span style="font-size:10px;color:var(--text-3)">{label}</span>
        </div>"""
    body = f'<div style="display:flex;align-items:flex-end;gap:5px;height:120px;padding-bottom:20px">{bars}</div>'
    _chart_wrap("Conclusões — Últimos 7 Dias", body)


def _monthly_chart(monthly):
    if not monthly:
        _chart_wrap("Conclusões Mensais", '<div style="color:var(--text-3);font-size:13px">Sem dados mensais</div>')
        return
    max_v = max(r["cnt"] for r in monthly) or 1
    bars = ""
    for row in monthly:
        h = max(int((row["cnt"] / max_v) * 90), 4)
        bars += f"""
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px">
            <span style="font-size:10px;font-weight:700;color:#27AE60;min-height:14px">{row['cnt'] if row['cnt'] else ''}</span>
            <div style="width:100%;background:#27AE60;border-radius:4px 4px 0 0;height:{h}px;opacity:0.85"></div>
            <span style="font-size:10px;color:var(--text-3)">{row['month'][5:]}</span>
        </div>"""
    body = f'<div style="display:flex;align-items:flex-end;gap:4px;height:120px;padding-bottom:20px">{bars}</div>'
    _chart_wrap("Conclusões Mensais (12 meses)", body)


def _responsible_table(by_responsible):
    st.markdown('<div class="section-title">Produtividade por Colaborador</div>', unsafe_allow_html=True)
    if not by_responsible:
        st.markdown('<div style="color:var(--text-3);font-size:13px">Sem dados</div>', unsafe_allow_html=True)
        return
    colors = ["#C0392B","#27AE60","#2980B9","#E67E22","#8E44AD","#16A085"]
    max_v  = max(r["cnt"] for r in by_responsible) or 1

    rows_html = ""
    for i, row in enumerate(by_responsible):
        name  = row.get("name") or "?"
        cnt   = row["cnt"]
        pct   = int(cnt / max_v * 100)
        color = colors[i % len(colors)]
        initials = "".join(p[0].upper() for p in name.split()[:2])
        rows_html += f"""
        <tr style="border-top:1px solid var(--border)">
            <td style="padding:10px 14px">
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:28px;height:28px;background:{color};border-radius:50%;
                                display:flex;align-items:center;justify-content:center;
                                font-size:10px;font-weight:700;color:#fff;flex-shrink:0">{initials}</div>
                    <span style="font-weight:600;font-size:13px;color:var(--text)">{name}</span>
                </div>
            </td>
            <td style="padding:10px 14px;text-align:center;font-weight:700;color:{color};font-size:14px">{cnt}</td>
            <td style="padding:10px 16px;width:40%">
                <div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>
            </td>
        </tr>"""

    st.markdown(f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-xl);
                overflow:hidden;box-shadow:var(--shadow-xs)">
        <table style="width:100%;border-collapse:collapse">
            <thead>
                <tr style="background:var(--surface-2)">
                    <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;
                               text-transform:uppercase;letter-spacing:0.5px;color:var(--text-3)">Colaborador</th>
                    <th style="padding:10px 14px;text-align:center;font-size:11px;font-weight:700;
                               text-transform:uppercase;letter-spacing:0.5px;color:var(--text-3)">Tarefas</th>
                    <th style="padding:10px 14px;font-size:11px;font-weight:700;
                               text-transform:uppercase;letter-spacing:0.5px;color:var(--text-3)">Distribuição</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)
