import bcrypt
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserRegister, SkillsUpdate
from app.auth import create_token, get_current_user
from pypdf import PdfReader

from app.models import User, Vacancy, ChatMessage
from app.services.matching import match_vacancies, find_matches
from app.schemas import MatchOut


from app.schemas import AnalysisOut, UserLogin, ChatRequest, ChatReply, ChatMessageOut
from app.services.gpt_analysis import analyze_student

from app.services.chat import chat_with_student

from app.core.limiter import limiter


router = APIRouter(tags=["users"])


@router.post("/register", summary="Регистрация нового пользователя")
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


@router.post("/login", summary="Вход и получение JWT-токена")
@limiter.limit("5/minute")
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
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


@router.get("/me", summary="Профиль текущего пользователя")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "skills": current_user.skills,
        "city": current_user.city,
        "desired_position": current_user.desired_position,
        "role": current_user.role,
    }


@router.put("/me/skills", summary="Обновить навыки")
def update_skills(
    data: SkillsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.skills = data.skills
    if data.city is not None:
        current_user.city = data.city
    if data.desired_position is not None:
        current_user.desired_position = data.desired_position
    db.commit()
    return {
        "id": current_user.id,
        "email": current_user.email,
        "skills": current_user.skills,
    }


MAX_RESUME_SIZE = 5 * 1024 * 1024


@router.post("/me/resume", summary="Загрузить резюме (PDF)")
def upload_resume(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Загрузите файл в формат PDF")

    if file.size and file.size > MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=413, detail="Резюме слишком большое (макс. 5 МБ )"
        )
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


@router.get(
    "/me/matches",
    summary="Подбор вакансий (семантический матчинг)",
    response_model=list[MatchOut],
)
def get_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    source: str = "skills",
    top_n: int = Query(10, ge=1, le=50),
):
    if source == "resume":
        text = current_user.resume_text
    else:
        text = current_user.skills
    if not text:
        raise HTTPException(
            status_code=400, detail="нет данных: заполни навыки или загрузи резюме"
        )
    vacancies = db.query(Vacancy).all()
    return match_vacancies(text, vacancies, top_n=top_n)


@router.get(
    "/me/chat/history", summary="История чата", response_model=list[ChatMessageOut]
)
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return messages


@router.get(
    "/me/analysis",
    summary="ИИ-анализ навыков и план обучения",
    response_model=AnalysisOut,
)
@limiter.limit("5/minute")
def analyze_me(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    text = current_user.resume_text or current_user.skills
    if not text:
        raise HTTPException(status_code=400, detail="Заполни навыки или загрузи резюме")
    vacancies = db.query(Vacancy).all()
    matches = find_matches(text, vacancies, top_n=5)
    return analyze_student(text, matches)


@router.post(
    "/me/chat", response_model=ChatReply, summary="Чат с карьерным консультантом"
)
@limiter.limit("5/minute")
def chat(
    request: Request,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reply = chat_with_student(db, current_user, body.message)
    return ChatReply(reply=reply)
