import os
import jwt
from datetime import datetime,timedelta,timezone

from database import engine, Base, get_db
import models
from models import User
import bcrypt

from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session 
app = FastAPI (  
    title="Career Platform API",
    description="Интеллектуальная платформа карьерного роста — бэкенд дипломной работы",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

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
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")

    hashed = bcrypt.hashpw(user.password.encode(),bcrypt.gensalt()).decode()
    new_user = User(email=user.email,hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return{"message": f"Пользователь {user.email} принят на регистрацию!", "id": new_user.id}

@app.post("/login")
def login(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.checkpw(user.password.encode(), db_user.hashed_password.encode()):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    token = create_token(user.email)
    return{"message":f"С возвращением, {user.email}!","access_token": token, "token_type":"bearer"}
