import os
import time


import json
import requests
from bs4 import BeautifulSoup
from database import SessionLocal
from models import Vacancy


def save_vacancies(items: list[dict], db) -> tuple[int, int]:
    added = 0
    updated = 0
    for item in items:
        existing = db.query(Vacancy).filter(Vacancy.url == item["url"]).first()
        if existing:
            for key, value in item.items():
                setattr(existing, key, value)
            updated += 1
        else:
            db.add(Vacancy(**item))
            added += 1
    db.commit()
    return added, updated


def load_from_file(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    for item in items:
        item["source"] = "kz_dataset"
    return items


def format_salary(salary: dict | None) -> str | None:
    if not salary:
        return None
    parts = []
    if salary.get("from"):
        parts.append(f"от {salary['from']}")
    if salary.get("to"):
        parts.append(f"до {salary['to']}")
    if not parts:
        return None
    return " ".join(parts) + f"{salary.get('currency',' ')}"


def load_from_hh(
    text: str = "Python", area: int = 40, per_page: int = 20
) -> list[dict]:
    headers = {"User-Agent": "Career Growth Platform (sudukow7@gmail.com)"}
    token = os.getenv("HH_ACCESS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.get(
            "https://api.hh.ru/vacancies",
            params={"text": text, "area": area, "per_page": per_page},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка запроса к hh: {e}")
        return []
    items = response.json().get("items", [])

    result = []
    for item in items:
        try:
            detail = requests.get(
                f"https://api.hh.ru/vacancies/{item['id']}",
                headers=headers,
                timeout=10,
            ).json()
        except requests.RequestException as e:
            print(f"Пропускаю вакансий {item['id']}: {e}")
            continue

        description = BeautifulSoup(
            detail.get("description", ""), "html.parser"
        ).get_text(separator=" ", strip=True)

        result.append(
            {
                "title": item["name"],
                "company": item["employer"]["name"],
                "location": item["area"]["name"],
                "salary": format_salary(item.get("salary")),
                "description": description,
                "url": item["alternate_url"],
                "source": "hh",
            }
        )
        time.sleep(0.2)

    return result


def refresh_vacancies():
    db = SessionLocal()
    added, updated = save_vacancies(load_from_hh(per_page=20), db)
    print(
        f"[Планировщик] новых вакансий из hh добавлено: {added}, обновлено: {updated}"
    )
    db.close()


if __name__ == "__main__":
    db = SessionLocal()

    added_file, updated_file = save_vacancies(
        load_from_file("vacancies_sample.json"), db
    )
    print(f"Из файла добавлено: {added_file}, обновлено {updated_file}")

    added_hh, updated_hh = save_vacancies(load_from_hh(), db)
    print(f"Из hh добавлено: {added_hh}, обновленно {updated_hh}")

    db.close()
    print("Готово!")
