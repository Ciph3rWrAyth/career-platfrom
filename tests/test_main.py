from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

from unittest.mock import patch, MagicMock

import json

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_and_login():
    client.post(
        "/register", json={"email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/login", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    response = client.post(
        "/login", json={"email": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_create_vacancy_requires_auth():
    response = client.post(
        "/vacancies",
        json={
            "title": "Тест",
            "company": "Тест GO ",
            "location": "Алматы",
            "description": "Описание",
        },
    )
    assert response.status_code in (401, 403)


def test_list_vacancies_open():
    response = client.get("/vacancies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def register_and_get_token(email, password="password123"):
    client.post("/register", json={"email": email, "password": password})
    resp = client.post("/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def test_me_requires_auth():
    resp = client.get("/me")
    assert resp.status_code in (401, 403)


def test_me_returns_current_user():
    token = register_and_get_token("me@example.com")
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


def test_update_skills():
    token = register_and_get_token("skills@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.put("/me/skills", json={"skills": "Python, SQL"}, headers=headers)
    assert resp.status_code == 200
    resp = client.get("/me", headers=headers)
    assert resp.json()["skills"] == "Python, SQL"


def _fake_openai(content):
    fake_message = MagicMock()
    fake_message.content = content
    fake_choice = MagicMock()
    fake_choice.message = fake_message
    fake_response = MagicMock()
    fake_response.choices = [fake_choice]
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response
    return fake_client


def test_chat_returns_reply():
    token = register_and_get_token("chat@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    fake_client = _fake_openai("Ответ от замоканного GPT")
    with patch("app.services.chat.OpenAI", return_value=fake_client):
        resp = client.post("/me/chat", json={"message": "привет"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["reply"] == "Ответ от замоканного GPT"


def test_analysis_returns_structure():
    token = register_and_get_token("analysis@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client.put("/me/skills", json={"skills": "Python, FastAPI, SQL"}, headers=headers)
    fake_json = json.dumps(
        {
            "summary": "Хороший бэкенд-фундамент, не хватает DevOps",
            "gaps": [{"skill": "Docker", "why": "нужен для деплоя"}],
            "plan": [{"step": 1, "topic": "Основы Docker", "resource": "туториал"}],
        }
    )
    fake_client = _fake_openai(fake_json)
    with (
        patch("app.services.gpt_analysis.OpenAI", return_value=fake_client),
        patch("app.services.gpt_analysis.settings.openai_api_key", "test-key"),
    ):
        resp = client.get("/me/analysis", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert data["gaps"][0]["skill"] == "Docker"
    assert data["plan"][0]["step"] == 1
