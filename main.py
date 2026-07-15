import os
import jwt
from datetime import datetime, timedelta, timezone

from database import engine, Base, get_db
import models
from models import User, Vacancy
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


class VacancyCreate(BaseModel):
    title: str
    company: str
    location: str
    salary: str | None = None
    description: str
    url: str | None = None


class VacancyOut(VacancyCreate):
    id: int
    model_config = {"from_attributes": True}


def get_vacancy_or_404(vacancy_id: int, db: Session = Depends(get_db)) -> Vacancy:
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return vacancy


@app.post("/vacancies", response_model=VacancyOut)
def create_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db)):
    new_vacancy = Vacancy(
        title=vacancy.title,
        company=vacancy.company,
        location=vacancy.location,
        salary=vacancy.salary,
        description=vacancy.description,
        url=vacancy.url,
    )
    db.add(new_vacancy)
    db.commit()
    db.refresh(new_vacancy)
    return new_vacancy


@app.get("/vacancies", response_model=list[VacancyOut])
def list_vacancies(db: Session = Depends(get_db)):
    return db.query(Vacancy).all()


@app.get("/vacancies/{vacancy_id}", response_model=VacancyOut)
def get_vacancy(vacancy: Vacancy = Depends(get_vacancy_or_404)):
    return vacancy


@app.put("/vacancies/{vacancy_id}", response_model=VacancyOut)
def update_vacancy(
    vacancy_data: VacancyCreate,
    vacancy: Vacancy = Depends(get_vacancy_or_404),
    db: Session = Depends(get_db),
):
    vacancy.title = vacancy_data.title
    vacancy.company = vacancy_data.company
    vacancy.location = vacancy_data.location
    vacancy.salary = vacancy_data.salary
    vacancy.description = vacancy_data.description
    vacancy.url = vacancy_data.url
    db.commit()
    db.refresh(vacancy)
    return vacancy


@app.delete("/vacancies/{vacancy_id}")
def delete_vacancy(
    vacancy: Vacancy = Depends(get_vacancy_or_404),
    db: Session = Depends(get_db),
):
    db.delete(vacancy)
    db.commit()
    return {"message": "Вакансия удалена "}


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
