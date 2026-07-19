

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import User, Vacancy
from schemas import VacancyCreate, VacancyOut
from auth import get_current_user

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


def get_vacancy_or_404(vacancy_id: int, db: Session = Depends(get_db)) -> Vacancy:
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return vacancy


@router.post("", response_model=VacancyOut)
def create_vacancy(
    vacancy: VacancyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_vacancy = Vacancy(
        title=vacancy.title,
        company=vacancy.company,
        location=vacancy.location,
        salary=vacancy.salary,
        description=vacancy.description,
        url=vacancy.url,
    )
    db.add(new_vacancy)
    db.commit()
    db.refresh(new_vacancy)
    return new_vacancy


@router.get("", response_model=list[VacancyOut])
def list_vacancies(
    search: str | None = None,
    location: str | None = None,
    source: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(Vacancy)
    if search:
        query = query.filter(
            or_(
                Vacancy.title.ilike(f"%{search}%"),
                Vacancy.description.ilike(f"%{search}%"),
            )
        )
    if location:
        query = query.filter(Vacancy.location.ilike(f"%{location}%"))
    if source:
        query = query.filter(Vacancy.source == source)

    return query.offset(skip).limit(limit).all()


@router.get("/{vacancy_id}", response_model=VacancyOut)
def get_vacancy(vacancy: Vacancy = Depends(get_vacancy_or_404)):
    return vacancy


@router.put("/{vacancy_id}", response_model=VacancyOut)
def update_vacancy(
    vacancy_data: VacancyCreate,
    vacancy: Vacancy = Depends(get_vacancy_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vacancy.title = vacancy_data.title
    vacancy.company = vacancy_data.company
    vacancy.location = vacancy_data.location
    vacancy.salary = vacancy_data.salary
    vacancy.description = vacancy_data.description
    vacancy.url = vacancy_data.url
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.delete("/{vacancy_id}")
def delete_vacancy(
    vacancy: Vacancy = Depends(get_vacancy_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.delete(vacancy)
    db.commit()
    return {"message": "Вакансия удалена"}
