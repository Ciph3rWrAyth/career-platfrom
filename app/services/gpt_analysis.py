import json
from urllib.parse import quote_plus
from pydantic import ValidationError

from app.core.exceptions import AIBadResponse
from app.services.ai_client import get_client, ask
from app.schemas import AnalysisOut, SkillGap, LearningStep
from app.logging_config import logger

MAX_VACANCIES_IN_PROMPT = 5
MAX_VACANCY_CHARS = 800
MAX_STUDENT_CHARS = 4000
MAX_GAPS = 6
MAX_PLAN_STEPS = 6


def search_link(topic):
    return "https://www.youtube.com/results?search_query=" + quote_plus(topic)


def build_prompt(student_text, matches):
    vac_lines = []
    for v, score in matches[:MAX_VACANCIES_IN_PROMPT]:
        text = (v.description or "")[:MAX_VACANCY_CHARS]
        vac_lines.append(f"[id={v.id}] {v.title} ({v.company}): {text}")
    vacancies_block = "\n\n".join(vac_lines)
    profile = student_text[:MAX_STUDENT_CHARS]
    return (
        "Ты — карьерный консультант. Навыки/резюме студента:\n"
        f"{profile}\n\n"
        "Подходящие ему вакансии:\n"
        f"{vacancies_block}\n\n"
        "Задача: определи, каких навыков студенту не хватает под эти вакансии, "
        "и составь пошаговый план обучения.\n\n"
        "ПРАВИЛА ДОСТОВЕРНОСТИ (соблюдай строго):\n"
        "1. Опирайся ТОЛЬКО на текст выше. Не додумывай требования, "
        "которых нет в приведённых описаниях.\n"
        "2. Если навык не указан в резюме — это НЕ значит, что студент им не владеет. "
        "Пиши «в профиле не подтверждён», а не «у вас нет».\n"
        "3. Если данных мало или требования не подтверждаются текстом — "
        "верни пустые gaps и plan, а причину объясни в summary. "
        "Пустой список лучше выдуманного пункта.\n"
        "4. НЕ добивай списки до максимума. Сколько подтверждено — столько и пунктов.\n\n"
        "Ответь строго в JSON с полями:\n"
        "- summary: краткий вывод в 2-3 предложениях; "
        "если gaps пустой — объясни здесь почему (мало данных / требования покрыты);\n"
        f"- gaps: список от 0 до {MAX_GAPS} пунктов, каждый {{skill, why}}. "
        "why — конкретное требование из текста вакансии со ссылкой на неё, "
        "формат: «вакансия id=N требует X, в профиле не подтверждён»;\n"
        f"- plan: список от 0 до {MAX_PLAN_STEPS} шагов, каждый {{step, topic}}. "
        "step — номер шага, ЦЕЛОЕ ЧИСЛО (1, 2, 3), без текста. "
        "topic — название темы отдельным полем. Номер и тему НЕ слепляй в одну строку.\n"
    )


def analyze_student(student_text, matches):
    prompt = build_prompt(student_text, matches)
    logger.info(f"Собран промт для GPT ({len(prompt)} cимволов)")
    client = get_client()
    response = ask(
        client,
        max_completion_tokens=1500,
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(response.choices[0].message.content)
        result = AnalysisOut(**data)
    except (json.JSONDecodeError, ValidationError, TypeError, IndexError) as error:
        raise AIBadResponse(f"{type(error).__name__}:{error}")

    for step in result.plan:
        step.resource = search_link(step.topic)
    return result
