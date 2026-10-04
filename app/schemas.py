from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(max_length=2000)


class ChatReply(BaseModel):
    reply: str


MAX_PASSWORD_BYTES = 72

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str)  -> str:
        if len(v.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(f"пароль длинее {MAX_PASSWORD_BYTES} байт (UTF-8)")
        return v


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
    city: str | None = None
    desired_position: str  | None = None


class VacancyBase(BaseModel):
    title: str
    company: str
    location: str
    salary: str | None = None
    url: str | None = None


class VacancyCreate(VacancyBase):
    description: str


class VacancyShort(VacancyBase):
    id: int
    source: str | None = None
    model_config = {"from_attributes": True}


class VacancyOut(VacancyShort):
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


class VacancyStats(BaseModel):
    total: int
    by_city: dict[str, int]
    last_updated: datetime | None


class SelfCheckIn(BaseModel):
    text:str

class SelfCheckOut(BaseModel):
    score:float
    matched_skills: list[str]
    missing_skills: list[str]
