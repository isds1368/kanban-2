import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kanban.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'colaborador',
        sector TEXT,
        position TEXT,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        last_login TEXT
    );

    CREATE TABLE IF NOT EXISTS boards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        color TEXT DEFAULT '#0052cc',
        owner_id INTEGER,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        archived INTEGER DEFAULT 0,
        FOREIGN KEY (owner_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS board_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        board_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        can_edit INTEGER DEFAULT 1,
        FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS columns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        board_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        position INTEGER DEFAULT 0,
        color TEXT DEFAULT '#e2e8f0',
        wip_limit INTEGER DEFAULT 0,
        FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        column_id INTEGER NOT NULL,
        board_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        responsible_id INTEGER,
        requester_id INTEGER,
        sector TEXT,
        priority TEXT DEFAULT 'média',
        status TEXT DEFAULT 'aberto',
        completion_percent INTEGER DEFAULT 0,
        due_date TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime')),
        position INTEGER DEFAULT 0,
        archived INTEGER DEFAULT 0,
        FOREIGN KEY (column_id) REFERENCES columns(id),
        FOREIGN KEY (board_id) REFERENCES boards(id),
        FOREIGN KEY (responsible_id) REFERENCES users(id),
        FOREIGN KEY (requester_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        board_id INTEGER,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#0052cc'
    );

    CREATE TABLE IF NOT EXISTS card_labels (
        card_id INTEGER NOT NULL,
        label_id INTEGER NOT NULL,
        PRIMARY KEY (card_id, label_id),
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
        FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        position INTEGER DEFAULT 0,
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS checklist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        position INTEGER DEFAULT 0,
        FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS card_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        user_id INTEGER,
        action TEXT NOT NULL,
        detail TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        user_id INTEGER,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_size INTEGER,
        mime_type TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'info',
        read INTEGER DEFAULT 0,
        card_id INTEGER,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (card_id) REFERENCES cards(id)
    );

    CREATE TABLE IF NOT EXISTS personal_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        priority TEXT DEFAULT 'média',
        completed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS personal_checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (task_id) REFERENCES personal_tasks(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS personal_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        detail TEXT,
        ip_address TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS card_time_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        column_id INTEGER NOT NULL,
        column_name TEXT,
        entered_at TEXT DEFAULT (datetime('now','localtime')),
        exited_at TEXT,
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def seed_default_data():
    """Insert default admin user and sample data if DB is empty."""
    import hashlib
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("""INSERT INTO users (name, login, password_hash, role, sector, position)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  ("Administrador", "admin", pw, "administrador", "TI", "Administrador do Sistema"))
        conn.commit()

        # Default board
        c.execute("INSERT INTO boards (name, description, color, owner_id) VALUES (?,?,?,?)",
                  ("Projeto Principal", "Quadro principal da empresa", "#0052cc", 1))
        board_id = c.lastrowid

        # Default columns
        cols = ["Backlog", "A Fazer", "Em Andamento", "Aguardando Aprovação", "Concluído"]
        for i, col in enumerate(cols):
            c.execute("INSERT INTO columns (board_id, name, position) VALUES (?,?,?)", (board_id, col, i))

        # Default labels
        labels = [
            ("Urgente", "#ff5630"), ("Financeiro", "#ff8b00"), ("Operação", "#36b37e"),
            ("Manutenção", "#00b8d9"), ("Projetos", "#6554c0"), ("Compras", "#ff7452"), ("TI", "#0052cc")
        ]
        for lname, lcolor in labels:
            c.execute("INSERT INTO labels (board_id, name, color) VALUES (?,?,?)", (board_id, lname, lcolor))

        conn.commit()

    conn.close()
