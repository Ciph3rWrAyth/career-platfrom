from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

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
    client.post("/register", json={"email": "test@example.com", "password": "1234"})
    response = client.post(
      "/login", json={"email": "test@example.com","password":"1234"}
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
