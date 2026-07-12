import os
import jwt
from datetime import datetime, timedelta, timezone

from database import engine, Base, get_db
import models
from models import User
import bcrypt

from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

app = FastAPI(
    title="Career Platform API",
    description="Интеллектуальная платформа карьерного роста — бэкенд дипломной работы",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY не задан. Проверь .env файл")
security = HTTPBearer()
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
    email: EmailStr
    password: str


@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")

    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": f"Пользователь { user.email } принят на регистрацию!",
        "id": new_user.id,
    }


@app.post("/login")
def login(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.checkpw(
        user.password.encode(), db_user.hashed_password.encode()
    ):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_token(user.email)
    return {
        "message": f"С возвращением, { user.email }!",
        "access_token": token,
        "token_type": "bearer",
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен просрочен, войдите заново")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}
