from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class BarangCreate(BaseModel):
    nama_barang: str
    jumlah: int

class BarangResponse(BaseModel):
    id: int
    nama_barang: str
    jumlah: int
    class Config:
        orm_mode = True
