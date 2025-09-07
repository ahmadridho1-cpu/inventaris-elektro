from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    # relasi ke Transaksi
    transaksi = relationship("Transaksi", back_populates="user")

class Barang(Base):
    __tablename__ = "barang"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, unique=True, index=True)
    stok = Column(Integer, default=0)

    # relasi ke Transaksi
    transaksi = relationship("Transaksi", back_populates="barang")

class Transaksi(Base):
    __tablename__ = "transaksi"

    id = Column(Integer, primary_key=True, index=True)
    barang_id = Column(Integer, ForeignKey("barang.id"))
    jumlah = Column(Integer)
    jenis = Column(String)   # masuk / keluar
    tanggal = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))

    # relasi balik
    barang = relationship("Barang", back_populates="transaksi")
    user = relationship("User", back_populates="transaksi")
