import logging

logger = logging.getLogger("career_platform")
logger.setLevel(logging.INFO)


if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
