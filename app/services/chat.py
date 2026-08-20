from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import ChatMessage


def _system_prompt(student_text):
    return (
        "Ты — карьерный консультант для студентов. Отвечай на русском, дружелюбно и по делу.\n\n"
        f"Данные студента (навыки/резюме):\n{student_text}\n\n"
        "Помогай с карьерой: пробелы в навыках, план обучения, подготовка к собеседованиям. "
        "Опирайся на данные студента."
    )


def chat_with_student(db: Session, user, message: str) -> str:
    db.add(ChatMessage(user_id=user.id, role="user", content=message))
    db.commit()

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    messages = [
        {
            "role": "system",
            "content": _system_prompt(user.resume_text or user.skills or ""),
        }
    ]
    for m in history:
        messages.append({"role": m.role, "content": m.content})

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(model="gpt-5.4-mini", messages=messages)
    reply = response.choices[0].message.content

    db.add(ChatMessage(user_id=user.id, role="assistant", content=reply))
    db.commit()

    return reply
