from pydantic import BaseModel
from fastapi import FastAPI
app = FastAPI(
    title="Career Platform API",
    description="Интеллектуальная платформа карьерного роста — бэкенд дипломной работы",
    version="0.1.0",
)
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
def register(user: UserRegister):
    return{"message": f"Пользователь {user.email} принят на регистрацию!"}

