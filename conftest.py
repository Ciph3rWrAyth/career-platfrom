# Пустой conftest.py в корне проекта.
# Он нужен, чтобы pytest добавил корень в sys.path и видел пакет `app`
# при импортах вида `from app.main import app` в тестах.
