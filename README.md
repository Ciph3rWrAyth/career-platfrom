# Career Platform — интеллектуальная платформа карьерного роста

Дипломный проект. Студент загружает навыки/резюме → семантический ML-матчинг подбирает наиболее подходящие вакансии (Казахстан) **по смыслу, а не по ключевым словам**. В планах — GPT-анализ пробелов в навыках и персональный план обучения.

## Стек
- **FastAPI** + **PostgreSQL** + SQLAlchemy + **Alembic** (миграции)
- **sentence-transformers** — семантический матчинг (с кэшем эмбеддингов)
- **JWT** + bcrypt — аутентификация и роли
- **pytest**, **ruff**

## Быстрый старт
1. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Скопируй `.env.example` → `.env` и заполни (БД, `SECRET_KEY`).
3. Накати миграции:
   ```bash
   alembic upgrade head
   ```
4. Запусти сервер:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Документация API: http://127.0.0.1:8000/docs

## Тесты
```bash
python -m pytest
```

## Структура
- `app/` — приложение
  - `app/routers/` — API-эндпоинты (пользователи, вакансии)
  - `app/services/` — логика: `matching.py` (ИИ-матчинг), `vacancies_import.py` (парсер hh)
  - `app/core/config.py` — конфигурация (pydantic-settings)
- `tests/` — тесты
- `alembic/` — миграции БД
- `experiment/` — эксперименты (keyword vs семантика, бенчмарк)
