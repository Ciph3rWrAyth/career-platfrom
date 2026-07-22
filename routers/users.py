import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserRegister, SkillsUpdate
from auth import create_token, get_current_user

from fastapi import UploadFile, File
from pypdf import PdfReader

router = APIRouter(tags=["users"])


@router.post("/register")
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
        "message": f"Пользователь {user.email} принят на регистрацию!",
        "id": new_user.id,
    }


@router.post("/login")
def login(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.checkpw(
        user.password.encode(), db_user.hashed_password.encode()
    ):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_token(user.email)
    return {
        "message": f"С возвращением, {user.email}!",
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "skills": current_user.skills,
        "role": current_user.role,
    }


@router.put("/me/skills")
def update_skills(
    data: SkillsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.skills = data.skills
    db.commit()
    return {
        "id": current_user.id,
        "email": current_user.email,
        "skills": current_user.skills,
    }


@router.post("/me/resume")
def upload_resume(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Загрузите файл в формат PDF")
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    current_user.resume_text = text
    db.commit()

    return {
        "message": "Резюме загружено",
        "chars": len(text),
        "preview": text[:200],
    }
