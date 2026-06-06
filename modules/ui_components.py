import streamlit as st

PRIORITY_COLORS = {
    "crítica": "#C0392B",
    "alta":    "#E67E22",
    "média":   "#2980B9",
    "baixa":   "#27AE60",
}

ROLE_LABELS = {
    "administrador": "Administrador",
    "gestor":        "Gestor",
    "colaborador":   "Colaborador",
    "leitor":        "Leitor",
}

# ── SVG icon library ──────────────────────────────────────────────────────────
ICONS = {
    "home": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>',
    "board": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M4 5h3v14H4zm6 0h3v8h-3zm6 0h3v11h-3z"/></svg>',
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M3 3v18h18v-2H5V3zm15 12-4-4-3 3-4-4-1.5 1.5 5.5 5.5 3-3 4 4L18 15z"/></svg>',
    "lock": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>',
    "bell": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/></svg>',
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M19.43 12.98c.04-.32.07-.64.07-.98s-.03-.66-.07-.98l2.11-1.65c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.3-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.38-2.65C14.46 2.18 14.25 2 14 2h-4c-.25 0-.46.18-.49.42l-.38 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.23-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64l2.11 1.65c-.04.32-.07.65-.07.98s.03.66.07.98l-2.11 1.65c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.08.73 1.69.98l.38 2.65c.03.24.24.42.49.42h4c.25 0 .46-.18.49-.42l.38-2.65c.61-.25 1.17-.59 1.69-.98l2.49 1c.23.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.65zM12 15.5c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z"/></svg>',
    "logout": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z"/></svg>',
    "edit": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="currentColor" viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>',
    "trash": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
    "arrow_right": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z"/></svg>',
    "tag": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="currentColor" viewBox="0 0 24 24"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>',
    "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>',
    "flag_red":    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="#C0392B" viewBox="0 0 24 24"><path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"/></svg>',
    "flag_orange": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="#E67E22" viewBox="0 0 24 24"><path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"/></svg>',
    "flag_blue":   '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="#2980B9" viewBox="0 0 24 24"><path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"/></svg>',
    "flag_green":  '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="#27AE60" viewBox="0 0 24 24"><path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"/></svg>',
    "warning":  '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="#E74C3C" viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
    "calendar": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 24 24"><path d="M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z"/></svg>',
    "comment": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 24 24"><path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z"/></svg>',
    "attach": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 24 24"><path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/></svg>',
    "chevron_right": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>',
    "chevron_down":  '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/></svg>',
    "menu": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>',
    "close": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>',
    "archive": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="currentColor" viewBox="0 0 24 24"><path d="M20 2H4c-1 0-2 .9-2 2v3.01c0 .72.43 1.34 1 1.72V20c0 1.1 1.1 2 2 2h14c.9 0 2-.9 2-2V8.72c.57-.39 1-1 1-1.71V4c0-1.1-1-2-2-2zm-5 12H9v-2h6v2zm5-8H4V4l16 .01V6z"/></svg>',
    "move": '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="currentColor" viewBox="0 0 24 24"><path d="M10 9h4V6h3l-5-5-5 5h3v3zm-1 1H6V7l-5 5 5 5v-3h3v-4zm14 2l-5-5v3h-3v4h3v3l5-5zm-9 3h-4v3H7l5 5 5-5h-3v-3z"/></svg>',
    "save": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
    "back": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>',
    "filter": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>',
    "person": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>',
    "note": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>',
    "task": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-9 14l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    "star_red": '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="#C0392B" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/></svg>',
    "dot_orange": '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="#E67E22" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/></svg>',
    "dot_blue":   '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="#2980B9" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/></svg>',
    "dot_green":  '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="#27AE60" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/></svg>',
    "logo": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" viewBox="0 0 24 24"><path d="M4 5h3v14H4zm6 0h3v8h-3zm6 0h3v11h-3z"/></svg>',
}

PRIORITY_ICON = {
    "crítica": ICONS["flag_red"],
    "alta":    ICONS["flag_orange"],
    "média":   ICONS["flag_blue"],
    "baixa":   ICONS["flag_green"],
}

def icon(name, style=""):
    svg = ICONS.get(name, "")
    if style:
        svg = svg.replace("<svg ", f'<svg style="{style}" ')
    return svg

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── THEME TOKENS (light) ──────────────────────────── */
:root {
    --primary:        #C0392B;
    --primary-hover:  #A93226;
    --primary-light:  #E74C3C;
    --primary-bg:     #FDEDEC;
    --sidebar-bg:     #1a1a1a;
    --sidebar-text:   rgba(255,255,255,0.85);
    --sidebar-muted:  rgba(255,255,255,0.45);
    --sidebar-active: rgba(192,57,43,0.85);
    --sidebar-hover:  rgba(255,255,255,0.08);
    --surface:        #FFFFFF;
    --surface-2:      #F8F9FA;
    --surface-3:      #F0F1F3;
    --border:         #E1E4E8;
    --border-strong:  #CDD0D4;
    --text:           #1A1D23;
    --text-2:         #4A5568;
    --text-3:         #8A9AB0;
    --success:        #27AE60;
    --warning:        #E67E22;
    --danger:         #C0392B;
    --info:           #2980B9;
    --shadow-xs:      0 1px 2px rgba(0,0,0,0.06);
    --shadow-sm:      0 1px 4px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
    --shadow-md:      0 4px 12px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.04);
    --shadow-lg:      0 8px 24px rgba(0,0,0,0.14);
    --radius:         6px;
    --radius-lg:      10px;
    --radius-xl:      14px;
    --col-bg:         #F0F1F3;
}

/* ── DARK MODE OVERRIDES ───────────────────────────── */
@media (prefers-color-scheme: dark) {
    :root {
        --surface:    #1E2128;
        --surface-2:  #252930;
        --surface-3:  #2D3139;
        --border:     #363C47;
        --border-strong: #454C59;
        --text:       #E8EAF0;
        --text-2:     #9AA5B8;
        --text-3:     #5A6478;
        --col-bg:     #252930;
        --sidebar-bg: #111318;
        --primary-bg: #2D1A18;
    }
    .stApp, html, body { background: #16191F !important; }
    [data-testid="stMetric"] { background: var(--surface) !important; }
    .stTextInput input, .stTextArea textarea, [data-baseweb="input"] input { background: var(--surface-2) !important; color: var(--text) !important; }
}

/* ── BASE ──────────────────────────────────────────── */
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; box-sizing: border-box; }
html, body, .stApp { background: var(--surface-2) !important; color: var(--text) !important; }
#MainMenu, footer, header, .stDeployButton, div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }

/* ── SCROLLBAR ─────────────────────────────────────── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

/* ── SIDEBAR ───────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: none !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] * { color: var(--sidebar-text) !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* sidebar collapse button stays visible */
button[data-testid="collapsedControl"],
button[kind="header"] { opacity: 1 !important; }

/* ── SIDEBAR EXPAND BUTTON (collapsed state) ──────── */
[data-testid="collapsedControl"] {
    background: var(--primary) !important;
    color: white !important;
    border-radius: 0 6px 6px 0 !important;
    top: 50% !important;
}

/* ── MAIN BUTTONS ──────────────────────────────────── */
.stButton > button {
    background: var(--primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.1px !important;
    padding: 7px 14px !important;
    height: auto !important;
    line-height: 1.4 !important;
    transition: background 0.15s, box-shadow 0.15s, transform 0.1s !important;
    box-shadow: var(--shadow-xs) !important;
}
.stButton > button:hover {
    background: var(--primary-hover) !important;
    box-shadow: var(--shadow-sm) !important;
    transform: translateY(-1px) !important;
}
/* secondary ghost buttons */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1.5px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--surface-3) !important;
}

/* ── INPUTS ────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-size: 13px !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(192,57,43,0.12) !important;
    outline: none !important;
}
label[data-testid="stWidgetLabel"] p { font-size: 12px !important; font-weight: 600 !important; color: var(--text-2) !important; text-transform: uppercase !important; letter-spacing: 0.4px !important; }

/* ── SELECTBOX ─────────────────────────────────────── */
[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-size: 13px !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(192,57,43,0.12) !important;
}

/* ── METRICS ───────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px 18px !important;
    box-shadow: var(--shadow-sm) !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; color: var(--primary) !important; }
[data-testid="stMetricLabel"] { font-size: 11px !important; font-weight: 600 !important; color: var(--text-3) !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }

/* ── TABS ──────────────────────────────────────────── */
[data-baseweb="tab-list"] { background: var(--surface-3) !important; border-radius: var(--radius) !important; padding: 3px !important; gap: 2px !important; border: 1px solid var(--border) !important; }
[data-baseweb="tab"] { border-radius: 4px !important; font-weight: 500 !important; font-size: 13px !important; color: var(--text-2) !important; padding: 6px 14px !important; }
[aria-selected="true"][data-baseweb="tab"] { background: var(--surface) !important; color: var(--primary) !important; font-weight: 700 !important; box-shadow: var(--shadow-xs) !important; }

/* ── EXPANDER ──────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-xs) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary { font-weight: 600 !important; font-size: 13px !important; color: var(--text) !important; }

/* ── CHECKBOX ──────────────────────────────────────── */
[data-testid="stCheckbox"] label span { font-size: 13px !important; color: var(--text-2) !important; }

/* ── DIVIDER ───────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 10px 0 !important; }

/* ── PROGRESS ──────────────────────────────────────── */
.stProgress > div > div { background: var(--primary) !important; border-radius: 100px !important; }
.stProgress > div { background: var(--border) !important; border-radius: 100px !important; }

/* ── KANBAN COMPONENTS ─────────────────────────────── */
.kb-column {
    background: var(--col-bg);
    border-radius: var(--radius-xl);
    padding: 10px 8px 12px;
    border: 1px solid var(--border);
    min-width: 0;
}
.kb-col-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 4px 4px 10px; margin-bottom: 4px;
    border-bottom: 2px solid var(--border);
}
.kb-col-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.7px; color: var(--text-2);
    display: flex; align-items: center; gap: 5px;
}
.kb-count {
    background: var(--border); color: var(--text-3);
    border-radius: 100px; padding: 1px 7px;
    font-size: 11px; font-weight: 700;
}
.kb-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 11px 12px 10px 14px;
    margin-bottom: 7px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-xs);
    cursor: pointer;
    transition: box-shadow 0.15s, transform 0.12s, border-color 0.15s;
    position: relative;
    overflow: hidden;
}
.kb-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
    border-color: var(--primary);
}
.kb-card-stripe {
    position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
}
.kb-card-title { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.4; margin-bottom: 6px; }
.kb-card-desc { font-size: 11.5px; color: var(--text-3); line-height: 1.5; margin-bottom: 6px; }
.kb-card-footer { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.kb-tag {
    display: inline-flex; align-items: center; gap: 3px;
    padding: 2px 7px; border-radius: 100px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.1px;
    border: 1px solid transparent;
}
.kb-prio-tag {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 600;
}
.kb-user-chip {
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--surface-3); border: 1px solid var(--border);
    border-radius: 100px; padding: 2px 8px 2px 4px;
    font-size: 11px; color: var(--text-2);
}
.kb-avatar {
    width: 22px; height: 22px; border-radius: 50%;
    background: var(--primary); color: white;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 9px; font-weight: 700; flex-shrink: 0;
}
.kb-date-badge {
    display: inline-flex; align-items: center; gap: 3px;
    padding: 2px 7px; border-radius: 4px;
    font-size: 11px; font-weight: 500;
}
.kb-date-ok    { background: #EBF5EB; color: #27AE60; }
.kb-date-warn  { background: #FEF9E7; color: #E67E22; }
.kb-date-over  { background: #FDEDEC; color: #C0392B; }
.kb-progress { background: var(--border); border-radius:100px; height:4px; margin-top:6px; overflow:hidden; }
.kb-progress-fill { height:4px; border-radius:100px; background: var(--primary); transition: width 0.4s; }

/* ── PAGE LAYOUT ───────────────────────────────────── */
.pg-title { font-size: 22px; font-weight: 800; color: var(--text); letter-spacing: -0.3px; line-height: 1.2; }
.pg-sub { font-size: 13px; color: var(--text-3); margin-top: 3px; }
.pg-header { margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }

/* ── SIDEBAR CUSTOM ELEMENTS ───────────────────────── */
.sb-logo { display:flex; align-items:center; gap:10px; padding:20px 16px 16px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom:8px; }
.sb-logo-text { font-size:17px; font-weight:800; color:#fff; letter-spacing:-0.3px; }
.sb-user { display:flex; align-items:center; gap:10px; padding:10px 14px; margin: 4px 10px 12px; background:rgba(255,255,255,0.07); border-radius:var(--radius-lg); }
.sb-avatar { width:34px; height:34px; background:var(--primary); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; color:#fff; flex-shrink:0; }
.sb-name { font-size:13px; font-weight:600; color:#fff; }
.sb-role { font-size:11px; color: var(--sidebar-muted); }
.sb-section { font-size:10px; font-weight:700; color:var(--sidebar-muted); text-transform:uppercase; letter-spacing:1px; padding: 8px 14px 4px; }
.sb-nav-item { display:flex; align-items:center; gap:9px; padding:9px 14px; margin:2px 8px; border-radius:var(--radius); font-size:13px; font-weight:500; color:var(--sidebar-text); cursor:pointer; transition:background 0.12s; text-decoration:none; }
.sb-nav-item:hover { background: var(--sidebar-hover); }
.sb-nav-item.active { background: var(--sidebar-active); color:#fff; font-weight:600; }
.sb-badge { background:var(--primary); color:#fff; border-radius:100px; padding:1px 6px; font-size:10px; font-weight:700; margin-left:auto; }
.sb-footer { padding:12px 10px; margin-top:auto; border-top: 1px solid rgba(255,255,255,0.08); }
.sb-stat-row { display:flex; gap:6px; margin-top:8px; }
.sb-stat { flex:1; background:rgba(255,255,255,0.07); border-radius:var(--radius); padding:7px 8px; text-align:center; }
.sb-stat-n { font-size:15px; font-weight:800; color:#fff; }
.sb-stat-l { font-size:9px; color:var(--sidebar-muted); text-transform:uppercase; letter-spacing:0.5px; }

/* ── NOTIFICATION ──────────────────────────────────── */
.notif-item { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-lg); padding:12px 14px; margin-bottom:8px; display:flex; gap:10px; align-items:flex-start; transition:box-shadow 0.12s; }
.notif-item:hover { box-shadow: var(--shadow-sm); }
.notif-item.unread { border-left: 3px solid var(--primary); background: var(--primary-bg); }

/* ── HISTORY ───────────────────────────────────────── */
.hist-row { display:flex; gap:10px; padding:8px 0; border-bottom:1px solid var(--border); align-items:flex-start; }
.hist-icon { width:28px; height:28px; border-radius:50%; background:var(--surface-3); display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.hist-text { font-size:12.5px; color:var(--text-2); line-height:1.5; }
.hist-meta { font-size:11px; color:var(--text-3); margin-top:2px; }

/* ── BOARD CARD ────────────────────────────────────── */
.board-card { background:var(--surface); border-radius:var(--radius-xl); border:1px solid var(--border); overflow:hidden; box-shadow:var(--shadow-sm); transition:box-shadow 0.15s, transform 0.12s; cursor:pointer; }
.board-card:hover { box-shadow:var(--shadow-lg); transform:translateY(-2px); }
.board-card-header { height:7px; }
.board-card-body { padding:16px 18px; }
.board-card-name { font-size:15px; font-weight:700; color:var(--text); margin-bottom:3px; }
.board-card-desc { font-size:12px; color:var(--text-3); min-height:16px; margin-bottom:12px; }
.board-card-stats { display:flex; gap:12px; font-size:12px; color:var(--text-3); }

/* ── PERSONAL ──────────────────────────────────────── */
.ptask { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-lg); padding:11px 13px; margin-bottom:7px; display:flex; gap:10px; align-items:flex-start; box-shadow:var(--shadow-xs); }
.ptask-done { opacity:0.55; }
.ptask-title { font-size:13px; font-weight:600; color:var(--text); }
.ptask-title-done { text-decoration:line-through; color:var(--text-3); }
.pnote { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-lg); padding:13px 15px; margin-bottom:8px; cursor:pointer; transition:box-shadow 0.12s, border-color 0.12s; }
.pnote:hover { box-shadow:var(--shadow-sm); border-color:var(--primary); }
.pnote-title { font-size:13px; font-weight:600; color:var(--text); margin-bottom:3px; }
.pnote-date { font-size:11px; color:var(--text-3); }

/* ── STAT CARD ─────────────────────────────────────── */
.dash-stat { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-xl); padding:18px 20px; text-align:center; box-shadow:var(--shadow-xs); }
.dash-stat-n { font-size:2rem; font-weight:800; line-height:1; margin-bottom:4px; }
.dash-stat-l { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-3); }
.bar-row { margin-bottom:10px; }
.bar-label { display:flex; justify-content:space-between; font-size:12px; color:var(--text-2); margin-bottom:4px; font-weight:500; }
.bar-bg { background:var(--surface-3); border-radius:100px; height:9px; }
.bar-fill { height:9px; border-radius:100px; transition:width 0.5s; }

/* ── COMMENT ───────────────────────────────────────── */
.cmt-wrap { display:flex; gap:10px; margin-bottom:14px; }
.cmt-body { flex:1; background:var(--surface-2); border:1px solid var(--border); border-radius:0 var(--radius-lg) var(--radius-lg); padding:8px 12px; }
.cmt-header { display:flex; align-items:center; gap:8px; margin-bottom:4px; }
.cmt-name { font-size:12.5px; font-weight:700; color:var(--text); }
.cmt-time { font-size:11px; color:var(--text-3); }
.cmt-text { font-size:13px; color:var(--text-2); line-height:1.5; }

/* ── USER TABLE ────────────────────────────────────── */
.user-row { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-lg); padding:12px 16px; margin-bottom:8px; display:flex; align-items:center; gap:12px; }
.user-badge { display:inline-flex; align-items:center; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:600; }

/* ── MISC ──────────────────────────────────────────── */
.empty-state { text-align:center; padding:48px 24px; color:var(--text-3); }
.empty-state svg { margin-bottom:12px; opacity:0.35; }
.empty-state-title { font-size:15px; font-weight:600; color:var(--text-2); margin-bottom:6px; }
.empty-state-sub { font-size:13px; }
.section-title { font-size:13px; font-weight:700; color:var(--text-2); text-transform:uppercase; letter-spacing:0.5px; margin:18px 0 10px; }
.overdue-tag { background:#FDEDEC; color:#C0392B; border:1px solid #F5B7B1; padding:2px 7px; border-radius:4px; font-size:11px; font-weight:600; display:inline-flex; align-items:center; gap:3px; }
</style>
""", unsafe_allow_html=True)


def avatar(name, size=26, bg=None):
    bg = bg or "var(--primary)"
    initials = "".join(p[0].upper() for p in (name or "?").split()[:2])
    return f'<span style="width:{size}px;height:{size}px;border-radius:50%;background:{bg};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:{int(size*0.38)}px;font-weight:700;flex-shrink:0">{initials}</span>'

def priority_pill(priority):
    colors = {"crítica": ("#C0392B","#FDEDEC"), "alta": ("#E67E22","#FEF5EC"),
               "média": ("#2980B9","#EBF5FB"), "baixa": ("#27AE60","#EAF7EF")}
    c, bg = colors.get(priority, ("#8A9AB0","#F0F1F3"))
    ico = PRIORITY_ICON.get(priority, ICONS["flag_blue"])
    return f'<span class="kb-prio-tag" style="color:{c};background:{bg}">{ico} {priority.capitalize()}</span>'

def label_chip(name, color):
    # proper hex contrast text
    return f'<span class="kb-tag" style="background:{color}22;color:{color};border-color:{color}44">{ICONS["tag"]} {name}</span>'

def page_header(title, subtitle=""):
    icon_map = {"Meus Quadros": "home", "Dashboard": "chart", "Área Pessoal": "lock",
                "Notificações": "bell", "Administração": "settings", "Kanban": "board"}
    ico_key = next((v for k, v in icon_map.items() if k in title), "board")
    st.markdown(f"""
    <div class="pg-header">
        <div class="pg-title">{title}</div>
        {f'<div class="pg-sub">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)
