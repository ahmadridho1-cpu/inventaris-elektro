# create_db.py
import os
from database import Base, engine
import models

DB_FILE = "loker_elit.db"

# Hapus file lama biar fresh
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"🗑️ Database lama '{DB_FILE}' dihapus.")

# Buat database baru
print("⚙️ Membuat database baru...")
Base.metadata.create_all(bind=engine)
print(f"✅ Database baru '{DB_FILE}' berhasil dibuat!")
