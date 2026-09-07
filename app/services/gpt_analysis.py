import json
from urllib.parse import quote_plus
from openai import OpenAI

from app.core.config import settings
from app.schemas import AnalysisOut, SkillGap, LearningStep
from app.logging_config import logger


def search_link(topic):
    return "https://www.youtube.com/results?search_query=" + quote_plus(topic)


def build_prompt(student_text, matches):
    vac_lines = []
    for v, score in matches:
        vac_lines.append(f"- {v.title} ({v.company}):{(v.description or '')[:200]}")
    vacancies_block = "\n".join(vac_lines)
    return (
        "Ты - карьерный консультант, Навыки/резюме студента:\n"
        f"{student_text}\n\n"
        "Подходящие ему вакансий:\n"
        f"{vacancies_block}\n\n"
        "Задача: определи, каких навыков студенту не хватает под эти вакансии, "
        "и составь пошаговый план обучения.\n"
        "Ответь строго в JSON с полями:\n"
        "- summary: краткий вывод в 2-3 предложениях;\n"
        "- gaps: список из 4-6 пунктов, каждый {skill, why};\n"
        "- plan: список из 4-6 шагов, каждый {step, topic}. "
        "step — номер шага, ЦЕЛОЕ ЧИСЛО (1, 2, 3), без текста. "
        "topic — название темы отдельным полем. Номер и тему НЕ слепляй в одну строку.\n"
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
                    step=1, topic="Основы Docker", resource=search_link("Основе Docker")
                )
            ],
        )
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    result = AnalysisOut(**data)
    for step in result.plan:
        step.resource = search_link(step.topic)
    return result
