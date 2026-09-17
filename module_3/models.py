import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Applicant(Base):
    __tablename__ = 'applicants'

    # 将 Python 模型的 p_id 映射到 SQLite/PostgreSQL 数据库中已存在的 id 列
    p_id = Column("id", Integer, primary_key=True, autoincrement=True)

    # 原始与清洗字段
    raw_program_text = Column(Text, nullable=True)
    university = Column(String, nullable=True)
    program_name = Column(String, nullable=True)
    comments = Column(Text, nullable=True)
    date_added = Column(String, nullable=True)
    url = Column(String, nullable=True)
    applicant_status = Column(String, nullable=True)
    decision_date = Column(String, nullable=True)
    term_and_year = Column(String, nullable=True)
    student_type = Column(String, nullable=True)
    degree_type = Column(String, nullable=True)
    
    # 成绩字段
    gpa = Column(Float, nullable=True)
    gre = Column(Float, nullable=True)
    gre_v = Column(Float, nullable=True)
    gre_aw = Column(Float, nullable=True)

    # LLM 提取字段
    llm_generated_university = Column(String, nullable=True)
    llm_generated_program = Column(String, nullable=True)

# 自动兼容 PostgreSQL 或 本地 SQLite 连接
DB_URL = os.getenv("DATABASE_URL", "sqlite:///gradcafe.db")

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()

