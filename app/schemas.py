from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class SkillsUpdate(BaseModel):
    skills: str


class VacancyCreate(BaseModel):
    title: str
    company: str
    location: str
    salary: str | None = None
    description: str
    url: str | None = None
    source: str | None = None


class VacancyOut(VacancyCreate):
    id: int
    model_config = {"from_attributes": True}
