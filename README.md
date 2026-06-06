# ⚡ KanbanPro v2.0 — Sistema de Gestão Corporativa

Sistema Kanban corporativo completo: Python + Streamlit + SQLite.

---

## 🚀 Instalação Rápida

```bash
# 1. Extraia o ZIP e entre na pasta
cd kanban/

# 2. (Recomendado) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instale a dependência
pip install streamlit

# 4. Execute
streamlit run app.py
```

Acesse em: **http://localhost:8501**

---

## 🌐 Acesso pela Rede Interna

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Outros usuários: `http://IP_DO_SERVIDOR:8501`

---

## 🔐 Credenciais Padrão

| Campo | Valor     |
|-------|-----------|
| Login | `admin`   |
| Senha | `admin123`|

> ⚠️ Altere a senha em Administração → Sistema → Alterar minha senha.

---

## 📁 Estrutura

```
kanban/
├── app.py                      # Entrada principal + sidebar
├── requirements.txt
├── kanban.db                   # Banco SQLite (gerado automaticamente)
├── uploads/                    # Arquivos anexados
├── backups/                    # Backups ZIP
├── .streamlit/config.toml      # Configuração do servidor
└── modules/
    ├── database.py             # Schema SQLite (14 tabelas)
    ├── auth.py                 # Autenticação + CRUD usuários
    ├── board_ops.py            # Todas as operações de dados
    ├── backup.py               # Backup/restore ZIP
    ├── ui_components.py        # CSS responsivo + dark mode + SVG icons
    ├── page_login.py           # Tela de login
    ├── page_boards.py          # Listagem de quadros
    ├── page_kanban.py          # Board Kanban principal
    ├── page_dashboard.py       # Dashboard executivo
    ├── page_personal.py        # Área pessoal privada
    ├── page_notifications.py   # Central de notificações
    └── page_admin.py           # Painel administrativo
```

---

## ✅ Funcionalidades v2.0

**Interface**
- Tema base vermelho corporativo
- Suporte automático a modo claro e escuro (prefers-color-scheme)
- Todos os ícones em SVG (sem emojis)
- Sidebar fixa com toggle nativo do Streamlit
- Layout responsivo e fluido

**Kanban**
- Colunas ilimitadas e configuráveis
- Cards com prioridade (flags coloridas), etiquetas, prazo, % conclusão
- Checklist por card com barra de progresso
- Comentários com avatar e timestamp
- Histórico imutável de movimentações
- Rastreamento de tempo por coluna
- Filtros: responsável, setor, prioridade, busca textual, só atrasadas
- Mover cards via selectbox em cada coluna

**Dashboard**
- KPIs: total, aberto, concluído, atrasado, taxa de conclusão
- Barras por prioridade e por setor
- Evolução semanal (7 dias) e mensal (12 meses)
- Ranking de produtividade por colaborador
- Lista de tarefas atrasadas com dias de atraso

**Área Pessoal (privada)**
- Tarefas com checklist, prazo, prioridade
- Notas/anotações com editor inline

**Administração**
- CRUD de usuários (4 perfis)
- Backup manual com download ZIP
- Logs com filtro por ação (bug corrigido)
- Métricas do sistema e alteração de senha

---

## 🔧 Migração para PostgreSQL

Substituir `sqlite3` por `psycopg2` em `modules/database.py` e ajustar string de conexão.
