from database import SessionLocal
from models import Vacancy
from matching import find_matches

db = SessionLocal()
vacancies = db.query(Vacancy).all()
db.close()


skills = "Python, FastAPI, SQL"


skill_words = [w.strip().lower() for w in skills.split(",")]


keyword_results = []
for v in vacancies:
    text = (v.description or "").lower()
    count = 0
    for word in skill_words:
        if word in text:
            count += 1
    keyword_results.append((v, count))

keyword_results.sort(key=lambda pair: pair[1], reverse=True)

print("=== ТОП-10 по словам (keyword) ===")
for v, count in keyword_results[:10]:
    print(count, "совпадений -", v.title)


keyword_count_by_id = {}
for v, count in keyword_results:
    keyword_count_by_id[v.id] = count

print()
print(f"{'#':<3}{'Балл':<8}{'Keyword':<10}Вакансия")
print("-" * 60)

semantic_results = find_matches(skills, vacancies, top_n=10)
rank = 1
for v, score in semantic_results:
    kw = keyword_count_by_id[v.id]
    kw_text = f"{kw} из 3"
    print(f"{rank:<3}{round(float(score), 3):<8}{kw_text:<10}{v.title}")
    rank += 1
