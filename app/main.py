from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler


from contextlib import asynccontextmanager
from app.services.vacancies_import import refresh_vacancies
from app.logging_config import logger
from app.routers import vacancies, users

from app.core.config import settings

from app.core.errors import register_error_handlers

from fastapi.middleware.cors import CORSMiddleware


from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

scheduler = BackgroundScheduler()
interval_hours = settings.scheduler_interval_hours


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.scheduler_enabled:
        scheduler.add_job(refresh_vacancies, "interval", hours=interval_hours)
        scheduler.start()
        logger.info(
        f"Приложение запущено, планировщик активен (интервал {interval_hours}ч)"
    )
    else:
        logger.info("Приложение запущено, планировщик выключен (SCHEDULER_ENABLED=false)")
    yield
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Приложение остановлено, планировщик выключен")
    else:
        logger.info ("Приложние остановлено")    
    
    
    


tags_metadata = [
    {"name": "users", "description": "Регистрация, вход, профиль, ИИ-подбор и анализ"},
    {"name": "vacancies", "description": "Каталог вакансий: CRUD, поиск, фильтры"},
]


app = FastAPI(
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    title="Career Platform API",
    description="Интеллектуальная платформа карьерного роста — бэкенд дипломной работы",
    version="0.1.0",
)

register_error_handlers(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vacancies.router)
app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": "Привет! Бэкенд дипломки живой 🚀"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
