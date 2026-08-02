import time 
from app.database import SessionLocal 
from app.models import Vacancy 
from app.services.matching import find_matches 

db = SessionLocal()
vacancies = db.query(Vacancy).all()
db.close()

skills = "Python, FastAPI, SQL"

start = time.perf_counter()
find_matches(skills, vacancies)
cold = time.perf_counter() - start


start = time.perf_counter()
for _ in range(5):
   find_matches(skills, vacancies)
warm = (time.perf_counter() - start)/5

print(f"Холодный вызов(заполняет кэш): {cold: .3f} сек")
print(f"Тёплый вызов(из кэш): {warm: .3f} сек")
print(f"Ускорение: -{cold / warm: .0f}x")