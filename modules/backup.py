import shutil
import os
import zipfile
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "kanban.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup():
    ensure_backup_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{ts}.zip")
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(DB_PATH):
            zf.write(DB_PATH, "kanban.db")
        if os.path.exists(UPLOADS_DIR):
            for root, dirs, files in os.walk(UPLOADS_DIR):
                for file in files:
                    fp = os.path.join(root, file)
                    arcname = os.path.relpath(fp, BASE_DIR)
                    zf.write(fp, arcname)
    return backup_path

def list_backups():
    ensure_backup_dir()
    files = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if f.endswith(".zip"):
            fp = os.path.join(BACKUP_DIR, f)
            size = os.path.getsize(fp)
            files.append({"name": f, "path": fp, "size": size,
                          "created": datetime.fromtimestamp(os.path.getctime(fp)).strftime("%d/%m/%Y %H:%M")})
    return files

def restore_backup(backup_path):
    with zipfile.ZipFile(backup_path, "r") as zf:
        zf.extractall(BASE_DIR)
    return True
