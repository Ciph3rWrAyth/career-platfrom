import sys
import os

# добавляем корень проекта в путь, чтобы из подпапки импортировать пакет app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from app.database import SessionLocal
from app.models import Vacancy
from app.services.matching import find_matches

db = SessionLocal()
vacancies = db.query(Vacancy).all()
db.close()

skills = "Python, FastAPI, SQL"

# 1-й вызов — ХОЛОДНЫЙ: заполняет кэш (столько стоил КАЖДЫЙ запрос раньше)
start = time.perf_counter()
find_matches(skills, vacancies)
cold = time.perf_counter() - start

# следующие 5 — ТЁПЛЫЕ: берут векторы из кэша
start = time.perf_counter()
for _ in range(5):
    find_matches(skills, vacancies)
warm = (time.perf_counter() - start) / 5

print(f"Холодный вызов (заполняет кэш): {cold:.3f} сек")
print(f"Тёплый вызов (из кэша):         {warm:.3f} сек")
print(f"Ускорение: ~{cold / warm:.0f}x")
