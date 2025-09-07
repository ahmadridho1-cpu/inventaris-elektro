from database import Base, engine
from models import User, Barang

print("Membuat tabel di database...")
Base.metadata.create_all(bind=engine)
print("Selesai ✅")
