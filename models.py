from sqlalchemy import Column, Integer, String, DateTime 
from database import Base
from sqlalchemy import Text

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    skills = Column(String, nullable=True)


class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    location = Column(String)
    salary = Column(String, nullable=True)
    description = Column(Text)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
