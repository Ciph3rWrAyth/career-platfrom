from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class ChatRequest(BaseModel):
    message: str


class ChatReply(BaseModel):
    reply: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(UserLogin):
    password: str = Field(min_length=8)


class SkillGap(BaseModel):
    skill: str
    why: str


class LearningStep(BaseModel):
    step: int
    topic: str
    resource: str | None = None


class AnalysisOut(BaseModel):
    summary: str
    gaps: list[SkillGap]
    plan: list[LearningStep]


class SkillsUpdate(BaseModel):
    skills: str


class VacancyBase(BaseModel):
    title: str
    company: str
    location: str
    salary: str | None = None
    url: str | None = None
    source: str | None = None


class VacancyCreate(VacancyBase):
    description: str


class VacancyShort(VacancyBase):
    id: int
    model_config = {"from_attributes": True}


class VacancyOut(VacancyCreate):
    description: str


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}


class MatchOut(BaseModel):
    score: float
    vacancy: VacancyShort
    matched_skills: list[str]
    missing_skills: list[str]
