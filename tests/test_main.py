from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

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
    client.post("/register", json={"email": "test@example.com", "password": "password123"})
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
    assert resp.status_code in (401,403)


def test_me_returns_current_user():
    token = register_and_get_token("me@example.com")
    resp = client.get("/me", headers = {"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


def test_update_skills():
    token = register_and_get_token("skills@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.put("/me/skills", json={"skills": "Python, SQL"}, headers=headers)
    assert resp.status_code == 200
    resp = client.get("/me", headers=headers)
    assert resp.json()["skills"] == "Python, SQL"
    
