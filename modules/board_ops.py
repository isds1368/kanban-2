from modules.database import get_connection
from datetime import datetime

# ===== BOARDS =====

def get_boards_for_user(user_id, role):
    conn = get_connection()
    if role == "administrador":
        boards = conn.execute("SELECT * FROM boards WHERE archived=0 ORDER BY name").fetchall()
    else:
        boards = conn.execute("""
            SELECT DISTINCT b.* FROM boards b
            LEFT JOIN board_members bm ON b.id = bm.board_id
            WHERE b.archived=0 AND (b.owner_id=? OR bm.user_id=?)
            ORDER BY b.name
        """, (user_id, user_id)).fetchall()
    conn.close()
    return [dict(b) for b in boards]

def create_board(name, description, color, owner_id):
    conn = get_connection()
    conn.execute("INSERT INTO boards (name, description, color, owner_id) VALUES (?,?,?,?)",
                 (name, description, color, owner_id))
    board_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    # default columns
    for i, col in enumerate(["Backlog", "A Fazer", "Em Andamento", "Concluído"]):
        conn.execute("INSERT INTO columns (board_id, name, position) VALUES (?,?,?)", (board_id, col, i))
    conn.commit()
    conn.close()
    return board_id

def get_board(board_id):
    conn = get_connection()
    b = conn.execute("SELECT * FROM boards WHERE id=?", (board_id,)).fetchone()
    conn.close()
    return dict(b) if b else None

def update_board(board_id, name, description, color):
    conn = get_connection()
    conn.execute("UPDATE boards SET name=?, description=?, color=? WHERE id=?",
                 (name, description, color, board_id))
    conn.commit()
    conn.close()

def archive_board(board_id):
    conn = get_connection()
    conn.execute("UPDATE boards SET archived=1 WHERE id=?", (board_id,))
    conn.commit()
    conn.close()

# ===== COLUMNS =====

def get_columns(board_id):
    conn = get_connection()
    cols = conn.execute("SELECT * FROM columns WHERE board_id=? ORDER BY position", (board_id,)).fetchall()
    conn.close()
    return [dict(c) for c in cols]

def create_column(board_id, name, color="#e2e8f0"):
    conn = get_connection()
    max_pos = conn.execute("SELECT COALESCE(MAX(position),0) FROM columns WHERE board_id=?", (board_id,)).fetchone()[0]
    conn.execute("INSERT INTO columns (board_id, name, position, color) VALUES (?,?,?,?)",
                 (board_id, name, max_pos+1, color))
    conn.commit()
    conn.close()

def update_column(col_id, name, color):
    conn = get_connection()
    conn.execute("UPDATE columns SET name=?, color=? WHERE id=?", (name, color, col_id))
    conn.commit()
    conn.close()

def delete_column(col_id):
    conn = get_connection()
    conn.execute("DELETE FROM columns WHERE id=?", (col_id,))
    conn.commit()
    conn.close()

def reorder_columns(board_id, col_ids_ordered):
    conn = get_connection()
    for i, cid in enumerate(col_ids_ordered):
        conn.execute("UPDATE columns SET position=? WHERE id=? AND board_id=?", (i, cid, board_id))
    conn.commit()
    conn.close()

# ===== CARDS =====

def get_cards_by_column(column_id):
    conn = get_connection()
    cards = conn.execute("""
        SELECT c.*, u.name as responsible_name, u2.name as requester_name
        FROM cards c
        LEFT JOIN users u ON c.responsible_id = u.id
        LEFT JOIN users u2 ON c.requester_id = u2.id
        WHERE c.column_id=? AND c.archived=0
        ORDER BY c.position
    """, (column_id,)).fetchall()
    conn.close()
    return [dict(c) for c in cards]

def get_card(card_id):
    conn = get_connection()
    c = conn.execute("""
        SELECT c.*, u.name as responsible_name, u2.name as requester_name
        FROM cards c
        LEFT JOIN users u ON c.responsible_id = u.id
        LEFT JOIN users u2 ON c.requester_id = u2.id
        WHERE c.id=?
    """, (card_id,)).fetchone()
    conn.close()
    return dict(c) if c else None

def create_card(column_id, board_id, title, description="", responsible_id=None,
                requester_id=None, sector=None, priority="média", due_date=None, user_id=None):
    conn = get_connection()
    max_pos = conn.execute("SELECT COALESCE(MAX(position),0) FROM cards WHERE column_id=?", (column_id,)).fetchone()[0]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO cards (column_id, board_id, title, description, responsible_id, requester_id,
                           sector, priority, due_date, position, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (column_id, board_id, title, description, responsible_id, requester_id,
          sector, priority, due_date, max_pos+1, now, now))
    card_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # start time tracking
    col_name = conn.execute("SELECT name FROM columns WHERE id=?", (column_id,)).fetchone()
    col_name = col_name[0] if col_name else ""
    conn.execute("INSERT INTO card_time_tracking (card_id, column_id, column_name) VALUES (?,?,?)",
                 (card_id, column_id, col_name))

    # history
    conn.execute("INSERT INTO card_history (card_id, user_id, action, detail) VALUES (?,?,?,?)",
                 (card_id, user_id, "criação", f"Tarefa criada na coluna '{col_name}'"))
    conn.commit()
    conn.close()
    return card_id

def update_card(card_id, **kwargs):
    conn = get_connection()
    allowed = ["title","description","responsible_id","requester_id","sector","priority",
               "status","completion_percent","due_date","column_id"]
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        conn.close()
        return
    fields["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [card_id]
    conn.execute(f"UPDATE cards SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def move_card(card_id, new_column_id, user_id=None):
    conn = get_connection()
    card = conn.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
    if not card:
        conn.close()
        return

    old_col = conn.execute("SELECT name FROM columns WHERE id=?", (card["column_id"],)).fetchone()
    new_col = conn.execute("SELECT name FROM columns WHERE id=?", (new_column_id,)).fetchone()
    old_col_name = old_col[0] if old_col else ""
    new_col_name = new_col[0] if new_col else ""

    # close time tracking
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE card_time_tracking SET exited_at=? WHERE card_id=? AND exited_at IS NULL",
                 (now, card_id))

    # open new tracking
    conn.execute("INSERT INTO card_time_tracking (card_id, column_id, column_name) VALUES (?,?,?)",
                 (card_id, new_column_id, new_col_name))

    # move
    max_pos = conn.execute("SELECT COALESCE(MAX(position),0) FROM cards WHERE column_id=?", (new_column_id,)).fetchone()[0]
    conn.execute("UPDATE cards SET column_id=?, position=?, updated_at=? WHERE id=?",
                 (new_column_id, max_pos+1, now, card_id))

    # history
    conn.execute("INSERT INTO card_history (card_id, user_id, action, detail) VALUES (?,?,?,?)",
                 (card_id, user_id, "movimentação", f"Movido de '{old_col_name}' para '{new_col_name}'"))
    conn.commit()
    conn.close()

def archive_card(card_id, user_id=None):
    conn = get_connection()
    conn.execute("UPDATE cards SET archived=1 WHERE id=?", (card_id,))
    conn.execute("INSERT INTO card_history (card_id, user_id, action, detail) VALUES (?,?,?,?)",
                 (card_id, user_id, "arquivamento", "Tarefa arquivada"))
    conn.commit()
    conn.close()

def get_card_history(card_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT h.*, u.name as user_name FROM card_history h
        LEFT JOIN users u ON h.user_id = u.id
        WHERE h.card_id=? ORDER BY h.created_at DESC
    """, (card_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ===== COMMENTS =====

def get_comments(card_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT cm.*, u.name as user_name FROM comments cm
        JOIN users u ON cm.user_id = u.id
        WHERE cm.card_id=? ORDER BY cm.created_at ASC
    """, (card_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_comment(card_id, user_id, message):
    conn = get_connection()
    conn.execute("INSERT INTO comments (card_id, user_id, message) VALUES (?,?,?)",
                 (card_id, user_id, message))
    conn.execute("INSERT INTO card_history (card_id, user_id, action, detail) VALUES (?,?,?,?)",
                 (card_id, user_id, "comentário", message[:100]))
    conn.commit()
    conn.close()

# ===== CHECKLISTS =====

def get_checklists(card_id):
    conn = get_connection()
    cls = conn.execute("SELECT * FROM checklists WHERE card_id=? ORDER BY position", (card_id,)).fetchall()
    result = []
    for cl in cls:
        items = conn.execute("SELECT * FROM checklist_items WHERE checklist_id=? ORDER BY position", (cl["id"],)).fetchall()
        d = dict(cl)
        d["items"] = [dict(i) for i in items]
        result.append(d)
    conn.close()
    return result

def add_checklist(card_id, title):
    conn = get_connection()
    max_pos = conn.execute("SELECT COALESCE(MAX(position),0) FROM checklists WHERE card_id=?", (card_id,)).fetchone()[0]
    conn.execute("INSERT INTO checklists (card_id, title, position) VALUES (?,?,?)", (card_id, title, max_pos+1))
    conn.commit()
    conn.close()

def add_checklist_item(checklist_id, text):
    conn = get_connection()
    max_pos = conn.execute("SELECT COALESCE(MAX(position),0) FROM checklist_items WHERE checklist_id=?", (checklist_id,)).fetchone()[0]
    conn.execute("INSERT INTO checklist_items (checklist_id, text, position) VALUES (?,?,?)", (checklist_id, text, max_pos+1))
    conn.commit()
    conn.close()

def toggle_checklist_item(item_id):
    conn = get_connection()
    conn.execute("UPDATE checklist_items SET completed = 1 - completed WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def delete_checklist_item(item_id):
    conn = get_connection()
    conn.execute("DELETE FROM checklist_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

# ===== LABELS =====

def get_labels(board_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM labels WHERE board_id=? ORDER BY name", (board_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_label(board_id, name, color):
    conn = get_connection()
    conn.execute("INSERT INTO labels (board_id, name, color) VALUES (?,?,?)", (board_id, name, color))
    conn.commit()
    conn.close()

def get_card_labels(card_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT l.* FROM labels l
        JOIN card_labels cl ON l.id = cl.label_id
        WHERE cl.card_id=?
    """, (card_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_card_labels(card_id, label_ids):
    conn = get_connection()
    conn.execute("DELETE FROM card_labels WHERE card_id=?", (card_id,))
    for lid in label_ids:
        conn.execute("INSERT OR IGNORE INTO card_labels (card_id, label_id) VALUES (?,?)", (card_id, lid))
    conn.commit()
    conn.close()

# ===== NOTIFICATIONS =====

def get_notifications(user_id, unread_only=False):
    conn = get_connection()
    q = "SELECT * FROM notifications WHERE user_id=?"
    if unread_only:
        q += " AND read=0"
    q += " ORDER BY created_at DESC LIMIT 50"
    rows = conn.execute(q, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_notification_read(notif_id):
    conn = get_connection()
    conn.execute("UPDATE notifications SET read=1 WHERE id=?", (notif_id,))
    conn.commit()
    conn.close()

def mark_all_notifications_read(user_id):
    conn = get_connection()
    conn.execute("UPDATE notifications SET read=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def create_notification(user_id, title, message, notif_type="info", card_id=None):
    conn = get_connection()
    conn.execute("INSERT INTO notifications (user_id, title, message, type, card_id) VALUES (?,?,?,?,?)",
                 (user_id, title, message, notif_type, card_id))
    conn.commit()
    conn.close()

def count_unread_notifications(user_id):
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND read=0", (user_id,)).fetchone()[0]
    conn.close()
    return n

# ===== PERSONAL =====

def get_personal_tasks(user_id):
    conn = get_connection()
    tasks = conn.execute("SELECT * FROM personal_tasks WHERE user_id=? ORDER BY completed, due_date, created_at",
                         (user_id,)).fetchall()
    result = []
    for t in tasks:
        d = dict(t)
        items = conn.execute("SELECT * FROM personal_checklists WHERE task_id=?", (t["id"],)).fetchall()
        d["checklist"] = [dict(i) for i in items]
        result.append(d)
    conn.close()
    return result

def create_personal_task(user_id, title, description, due_date, priority):
    conn = get_connection()
    conn.execute("INSERT INTO personal_tasks (user_id, title, description, due_date, priority) VALUES (?,?,?,?,?)",
                 (user_id, title, description, due_date, priority))
    conn.commit()
    conn.close()

def toggle_personal_task(task_id):
    conn = get_connection()
    conn.execute("UPDATE personal_tasks SET completed = 1 - completed WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def delete_personal_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM personal_tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def add_personal_checklist_item(task_id, text):
    conn = get_connection()
    conn.execute("INSERT INTO personal_checklists (task_id, text) VALUES (?,?)", (task_id, text))
    conn.commit()
    conn.close()

def toggle_personal_checklist_item(item_id):
    conn = get_connection()
    conn.execute("UPDATE personal_checklists SET completed = 1 - completed WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def get_personal_notes(user_id):
    conn = get_connection()
    notes = conn.execute("SELECT * FROM personal_notes WHERE user_id=? ORDER BY updated_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(n) for n in notes]

def save_personal_note(user_id, title, content, note_id=None):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if note_id:
        conn.execute("UPDATE personal_notes SET title=?, content=?, updated_at=? WHERE id=? AND user_id=?",
                     (title, content, now, note_id, user_id))
    else:
        conn.execute("INSERT INTO personal_notes (user_id, title, content, updated_at) VALUES (?,?,?,?)",
                     (user_id, title, content, now))
    conn.commit()
    conn.close()

def delete_personal_note(note_id, user_id):
    conn = get_connection()
    conn.execute("DELETE FROM personal_notes WHERE id=? AND user_id=?", (note_id, user_id))
    conn.commit()
    conn.close()

# ===== DASHBOARD =====

def get_dashboard_stats(board_id=None):
    conn = get_connection()
    where = "AND c.board_id=?" if board_id else ""
    params = (board_id,) if board_id else ()

    total = conn.execute(f"SELECT COUNT(*) FROM cards c WHERE c.archived=0 {where}", params).fetchone()[0]
    open_cards = conn.execute(f"SELECT COUNT(*) FROM cards c WHERE c.archived=0 AND c.status!='concluído' {where}", params).fetchone()[0]
    done = conn.execute(f"SELECT COUNT(*) FROM cards c WHERE c.archived=0 AND c.status='concluído' {where}", params).fetchone()[0]
    overdue = conn.execute(f"""SELECT COUNT(*) FROM cards c WHERE c.archived=0 AND c.status!='concluído'
                               AND c.due_date < date('now') AND c.due_date IS NOT NULL {where}""", params).fetchone()[0]

    by_priority = conn.execute(f"""SELECT priority, COUNT(*) as cnt FROM cards c
                                   WHERE c.archived=0 {where} GROUP BY priority""", params).fetchall()
    by_sector = conn.execute(f"""SELECT sector, COUNT(*) as cnt FROM cards c
                                 WHERE c.archived=0 AND sector IS NOT NULL {where} GROUP BY sector""", params).fetchall()
    by_responsible = conn.execute(f"""SELECT u.name, COUNT(*) as cnt FROM cards c
                                      JOIN users u ON c.responsible_id = u.id
                                      WHERE c.archived=0 {where} GROUP BY u.name ORDER BY cnt DESC LIMIT 10""", params).fetchall()

    # weekly completion
    weekly = conn.execute(f"""SELECT date(updated_at) as day, COUNT(*) as cnt FROM cards c
                               WHERE c.archived=0 AND c.status='concluído'
                               AND updated_at >= date('now','-7 days') {where}
                               GROUP BY day ORDER BY day""", params).fetchall()

    # monthly
    monthly = conn.execute(f"""SELECT strftime('%Y-%m', updated_at) as month, COUNT(*) as cnt FROM cards c
                                WHERE c.archived=0 AND c.status='concluído'
                                AND updated_at >= date('now','-12 months') {where}
                                GROUP BY month ORDER BY month""", params).fetchall()

    conn.close()
    return {
        "total": total, "open": open_cards, "done": done, "overdue": overdue,
        "by_priority": [dict(r) for r in by_priority],
        "by_sector": [dict(r) for r in by_sector],
        "by_responsible": [dict(r) for r in by_responsible],
        "weekly": [dict(r) for r in weekly],
        "monthly": [dict(r) for r in monthly],
    }

def get_all_cards_filtered(board_id=None, responsible_id=None, sector=None,
                            priority=None, search=None, overdue_only=False):
    conn = get_connection()
    q = """SELECT c.*, u.name as responsible_name, col.name as column_name
           FROM cards c
           LEFT JOIN users u ON c.responsible_id = u.id
           LEFT JOIN columns col ON c.column_id = col.id
           WHERE c.archived=0"""
    params = []
    if board_id:
        q += " AND c.board_id=?"; params.append(board_id)
    if responsible_id:
        q += " AND c.responsible_id=?"; params.append(responsible_id)
    if sector:
        q += " AND c.sector=?"; params.append(sector)
    if priority:
        q += " AND c.priority=?"; params.append(priority)
    if search:
        q += " AND (c.title LIKE ? OR c.description LIKE ?)"; params += [f"%{search}%", f"%{search}%"]
    if overdue_only:
        q += " AND c.due_date < date('now') AND c.status!='concluído'"
    q += " ORDER BY c.due_date, c.position"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
