from types import SimpleNamespace
from app.services.matching import _vector_cache
from app.services.matching import find_matches, clear_cache


def make_vacancy(id, title, description):
   return SimpleNamespace(id=id, title=title, description=description)


def test_relevant_vacancy_ranks_first():
   clear_cache()
   vacancies = [
      make_vacancy(1, "Повар", "Готовит блюда в ресторане, работа на кухне"),
      make_vacancy(2, "Python-разработчик", "Пишет бэкенд на Python и FastAPI")
   ]
   result = find_matches("Python, FastAPI", vacancies, top_n=2)

   top_vacancy = result[0][0]
   assert top_vacancy.title == "Python-разработчик"

def test_returns_top_n():
   clear_cache()
   vacancies = [
      make_vacancy(1, "Таксист", "Доставляет людей от точки А до точки Б"),
      make_vacancy(2, "Java-разработчик", "Пишет бэкенд на Java и Docker"),
      make_vacancy(3, "Тестировщик", "Тестирует сервисы на проф пригодность")
   ]
   result = find_matches("Java, Docker", vacancies, top_n=2)

   assert len(result) == 2

def test_clear_cache_empties():
   clear_cache()
   vacancies = [
      make_vacancy(1, "Таксист", "Доставляет людей от точки А до точки Б"),
      make_vacancy(2, "C#-разработчик", "Пишет инженерию через С и работает через Visual"),
      make_vacancy(3, "Тестировщик", "Тестирует сервисы на проф пригодность"),
      make_vacancy(4, "Водитель-автобуса", "Водить автобус")
   ] 
   find_matches("C#, Visual", vacancies, top_n=2)

   assert len(_vector_cache) > 0
   clear_cache()
   assert len(_vector_cache) == 0
   