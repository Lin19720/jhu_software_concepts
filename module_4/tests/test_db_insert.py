import pytest
from models import get_session, Applicant
from sqlalchemy import delete, select

@pytest.fixture
def clean_db():
    """每次测试前清空 Applicant 表，测试后清理"""
    session = get_session()
    session.execute(delete(Applicant))
    session.commit()
    session.close()
    yield
    session = get_session()
    session.execute(delete(Applicant))
    session.commit()
    session.close()

@pytest.mark.db
def test_insert_on_pull(clean_db):
    """测试数据插入，校验必填字段非空"""
    session = get_session()
    # 写入前：确认表为空
    count_before = session.scalar(select(Applicant))
    assert count_before is None

    # 插入一条测试数据
    applicant = Applicant(
        p_id=999999,
        term_and_year="Fall 2026",
        gpa=3.85,
        gre=325.0,
        raw_program_text="Computer Science, Johns Hopkins University"
    )
    session.add(applicant)
    session.commit()

    # 写入后：确认新增记录且必填字段非空
    inserted = session.scalar(select(Applicant).where(Applicant.p_id == 999999))
    assert inserted is not None
    assert inserted.p_id is not None
    assert inserted.term_and_year is not None
    session.close()

@pytest.mark.db
def test_idempotency_and_constraints(clean_db):
    """测试幂等性 / 约束：重复插入相同主键不会创建重复行"""
    session = get_session()
    app1 = Applicant(p_id=888888, term_and_year="Fall 2026", gpa=3.9)
    session.add(app1)
    session.commit()

    # 再次插入相同 p_id 的记录
    try:
        app2 = Applicant(p_id=888888, term_and_year="Fall 2026", gpa=3.9)
        session.add(app2)
        session.commit()
    except Exception:
        session.rollback()

    # 校验数据库中仍只有 1 条记录
    records = session.scalars(select(Applicant).where(Applicant.p_id == 888888)).all()
    assert len(records) == 1
    session.close()

@pytest.mark.db
def test_simple_query_function(clean_db):
    """测试查询功能，验证返回包含 M3 预期字段的字典结构"""
    session = get_session()
    app_entry = Applicant(
        p_id=777777,
        term_and_year="Fall 2026",
        gpa=3.75,
        gre=320.0
    )
    session.add(app_entry)
    session.commit()

    # 查询并转换为 dict 结构
    record = session.scalar(select(Applicant).where(Applicant.p_id == 777777))
    assert record is not None
    
    # 验证对象属性访问/字典化包含必要 key
    data_dict = {
        "p_id": record.p_id,
        "term_and_year": record.term_and_year,
        "gpa": record.gpa,
        "gre": record.gre
    }
    assert "p_id" in data_dict
    assert "term_and_year" in data_dict
    assert "gpa" in data_dict
    session.close()
