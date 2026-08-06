from app.core.config import settings
from app.schemas import AnalysisOut, SkillGap, LearningStep
from app.logging_config import logger


def build_prompt(student_text, matches):
    vac_lines = []
    for v, score in matches:
        vac_lines.append(f"- {v.title} ({v.company}):{(v.description or '')[:200]}")
        vacancies_block = "/n".join(vac_lines)
    return (
        "Ты - карьерный консультант, Навыки/резюме студента:/n"
        f"{student_text}/n/n"
        "Подходящие ему вакансий:/n"
        f"{vacancies_block}/n/n"
        "Найди, каких навыкоа студенту не хватает под эти вакансий и составь план обучения."
        "Ответь сторого в JSON: summary, gaps (skill, why), plan(step, topic, resource)."
    )


def analyze_student(student_text, matches):
    prompt = build_prompt(student_text, matches)
    logger.info(f"Собран промт для GPT ({len(prompt)} cимволов)")
    if not settings.openai_api_key:
        return AnalysisOut(
            summary="[ДЕМО] Здесь будет анализ от GPT. Промпт собран, ждём ключ API",
            gaps=[
                SkillGap(
                    skill="Docker", why="есть в целевых вакансиях, но нет в резюме"
                )
            ],
            plan=[
                LearningStep(
                    step=1, topic="Основы Docker", resource="официальный туториал"
                )
            ],
        )
    raise NotImplementedError("Реальный вызов GPT добавим, когда будет ключ")
