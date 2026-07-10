from database import engine, Base, get_db
import models
from models import User
import bcrypt

from pydantic import BaseModel
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session 
app = FastAPI (  
    title="Career Platform API",
    description="Интеллектуальная платформа карьерного роста — бэкенд дипломной работы",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Привет! Бэкенд дипломки живой 🚀"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Привет, {name}! Добро пожаловать на платформу."}

class UserRegister(BaseModel):
    email: str
    password: str 

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    hashed = bcrypt.hashpw(user.password.encode(),bcrypt.gensalt()).decode()
    new_user = User(email=user.email,hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return{"message": f"Пользователь {user.email} принят на регистрацию!", "id": new_user.id}

