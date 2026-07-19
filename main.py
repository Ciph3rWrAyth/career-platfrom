import os

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler


from contextlib import asynccontextmanager
from vacancies_import import refresh_vacancies
from logging_config import logger
from routers import vacancies, users

scheduler = BackgroundScheduler()
interval_hours = int(os.getenv("SCHEDULER_INTERVAL_HOURS", 24))


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(refresh_vacancies, "interval", hours=interval_hours)
    scheduler.start()
    logger.info(f"Приложение запущено, планировщик активен (интервал {interval_hours}ч)")
    yield
    scheduler.shutdown()
    logger.info("Приложение остановлено, планировщик выключен")
    

app = FastAPI(
    title="Career Platform API",
    description="Интеллектуальная платформа карьерного роста — бэкенд дипломной работы",
    version="0.1.0",
)


app.include_router(vacancies.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Привет! Бэкенд дипломки живой 🚀"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
