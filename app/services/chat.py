from sqlalchemy.orm import Session

from app.core.exceptions import AIBadResponse
from app.models import ChatMessage
from app.services.ai_client import get_client, ask

MAX_HISTORY_MESSAGES = 20
MAX_CONTEXT_CHARS = 4000
MAX_REPLY_TOKENS = 700


def _system_prompt(student_text):
    return (
        "Ты — карьерный консультант для студентов. Отвечай на русском, дружелюбно и по делу.\n\n"
        f"Данные студента (навыки/резюме):\n{student_text}\n\n"
        "Помогай с карьерой: пробелы в навыках, план обучения, подготовка к собеседованиям. "
        "Опирайся на данные студента."
    )


def chat_with_student(db: Session, user, message: str) -> str:
    client = get_client()

    context = (user.resume_text or user.skills or "")[:MAX_CONTEXT_CHARS]

    recent = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(MAX_HISTORY_MESSAGES)
        .all()
    )
    history = list(reversed(recent))

    messages = [{"role": "system", "content": _system_prompt(context)}]
    for m in history:
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": message})

    response = ask(
        client,
        model="gpt-5.4-mini",
        messages=messages,
        max_completion_tokens=MAX_REPLY_TOKENS,
    )
    try:
        reply = response.choices[0].message.content
    except (IndexError, AttributeError) as error:
        raise AIBadResponse(f"{type(error).__name__}: {error}")
    if not reply:
        raise AIBadResponse("пустой ответ модели")

    try:
        db.add(ChatMessage(user_id=user.id, role="user", content=message))
        db.add(ChatMessage(user_id=user.id, role="assistant", content=reply))
        db.commit()
    except Exception:
        db.rollback()
        raise

    return reply