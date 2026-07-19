import os

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from database import engine, Base
from vacancies_import import refresh_vacancies
from logging_config import logger
from routers import vacancies, users

app = FastAPI(
    title="Career Platform API",
    description="Интеллектуальная платформа карьерного роста — бэкенд дипломной работы",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()
interval_hours = int(os.getenv("SCHEDULER_INTERVAL_HOURS", 24))
scheduler.add_job(refresh_vacancies, "interval", hours=interval_hours)
scheduler.start()
logger.info(f"Приложение запущено, планировщик активен (интервал {interval_hours}ч)")

app.include_router(vacancies.router)
app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": "Привет! Бэкенд дипломки живой 🚀"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
