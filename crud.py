from sqlalchemy.orm import Session
from models import User, Barang
from schemas import UserCreate, BarangCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User
def create_user(db: Session, user: UserCreate):
    hashed_pw = pwd_context.hash(user.password)
    db_user = User(username=user.username, password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Barang
def create_barang(db: Session, barang: BarangCreate, user_id: int):
    db_barang = Barang(nama_barang=barang.nama_barang, jumlah=barang.jumlah, owner_id=user_id)
    db.add(db_barang)
    db.commit()
    db.refresh(db_barang)
    return db_barang

def get_all_barang(db: Session):
    return db.query(Barang).all()
