from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from database import SessionLocal, engine
from models import Base, User, Barang, Transaksi
from auth import create_access_token
from jose import jwt, JWTError
from datetime import datetime
from fastapi.security import HTTPBearer
from typing import Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Auto create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# Dependency DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper: get current user from token
def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user   # ⬅️ sekarang return object User, ada .id dan .username


@app.get("/")
def root():
    return {"message": "API Inventaris sudah jalan 🚀"}

# ------------------ AUTH ------------------
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": f"User {username} berhasil dibuat"}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# ------------------ BARANG ------------------
@app.post("/barang")
def tambah_barang(nama: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    barang = Barang(nama=nama, stok=0)
    db.add(barang)
    db.commit()
    db.refresh(barang)
    return {"message": f"Barang {nama} berhasil ditambahkan"}

@app.get("/barang")
def list_barang(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Barang).all()

# ------------------ TRANSAKSI ------------------
@app.post("/transaksi")
def tambah_transaksi(barang_id: int, jumlah: int, jenis: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    barang = db.query(Barang).filter(Barang.id == barang_id).first()
    if not barang:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan")

    if jenis == "masuk":
        barang.stok += jumlah
    elif jenis == "keluar":
        if barang.stok < jumlah:
            raise HTTPException(status_code=400, detail="Stok tidak cukup")
        barang.stok -= jumlah
    else:
        raise HTTPException(status_code=400, detail="Jenis harus 'masuk' atau 'keluar'")

    transaksi = Transaksi(
        barang_id=barang_id,
        jumlah=jumlah,
        jenis=jenis,
        tanggal=datetime.utcnow(),
        user_id=current_user.id
    )
    db.add(transaksi)
    db.commit()
    db.refresh(transaksi)

    return {"message": f"Transaksi {jenis} {jumlah} barang berhasil dicatat"}

@app.get("/transaksi")
def list_transaksi(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Transaksi).all()
# ---------------- LAST ACTIVITY ----------------
@app.get("/last-activity")
def last_activity(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transaksi = db.query(Transaksi).order_by(Transaksi.tanggal.desc()).first()
    if not transaksi:
        return {"message": "Belum ada transaksi"}
    return {
        "barang": transaksi.barang.nama,
        "jumlah": transaksi.jumlah,
        "jenis": transaksi.jenis,
        "tanggal": transaksi.tanggal,
        "oleh": transaksi.user.username
    }

@app.get("/last-activity/{barang_id}")
def last_activity_barang(barang_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transaksi = (
        db.query(Transaksi)
        .filter(Transaksi.barang_id == barang_id)
        .order_by(Transaksi.tanggal.desc())
        .first()
    )
    if not transaksi:
        return {"message": "Belum ada transaksi untuk barang ini"}
    return {
        "barang": transaksi.barang.nama,
        "jumlah": transaksi.jumlah,
        "jenis": transaksi.jenis,
        "tanggal": transaksi.tanggal,
        "oleh": transaksi.user.username
    }