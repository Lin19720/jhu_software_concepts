from sqlalchemy import select, func, or_, and_
from models import get_session, Applicant

def run_orm_queries():
    session = get_session()

    print("==================== ORM ANALYSIS RESULTS ====================\n")

    # Question 1: Fall 2026 applicant count
    stmt1 = select(func.count(Applicant.p_id)).where(
        or_(
            Applicant.term_and_year.like('%Fall 2026%'),
            Applicant.raw_program_text.like('%Fall 2026%')
        )
    )
    q1_count = session.scalar(stmt1)
    print(f"Question 1:\nFall 2026 applicant count: {q1_count}\n")

    # Question 4: Average GPA of American applicants
    stmt4 = select(func.avg(Applicant.gpa)).where(
        and_(
            Applicant.student_type == 'American',
            Applicant.gpa.isnot(None)
        )
    )
    q4_gpa = session.scalar(stmt4)
    print(f"Question 4:\nAverage GPA: {q4_gpa:.2f}\n" if q4_gpa is not None else "Question 4:\nAverage GPA: N/A\n")

    # Question 5: Fall 2025 acceptance percentage
    total_fall2025_stmt = select(func.count(Applicant.p_id)).where(
        or_(
            Applicant.term_and_year.like('%Fall 2025%'),
            Applicant.raw_program_text.like('%Fall 2025%')
        )
    )
    accepted_fall2025_stmt = select(func.count(Applicant.p_id)).where(
        and_(
            or_(
                Applicant.term_and_year.like('%Fall 2025%'),
                Applicant.raw_program_text.like('%Fall 2025%')
            ),
            Applicant.applicant_status.like('%Accepted%')
        )
    )
    tot5 = session.scalar(total_fall2025_stmt)
    acc5 = session.scalar(accepted_fall2025_stmt)
    pct5 = (acc5 * 100.0 / tot5) if tot5 and tot5 > 0 else 0.0
    print(f"Question 5:\nFall 2025 acceptance percentage: {pct5:.2f}%\n")

    # Question 8: JHU CS Master's count (Original fields) - 完全对齐 SQL 逻辑
    stmt8 = select(func.count(Applicant.p_id)).where(
        and_(
            or_(
                Applicant.university.like('%Johns Hopkins%'),
                Applicant.university.like('%JHU%'),
                Applicant.raw_program_text.like('%Johns Hopkins%'),
                Applicant.raw_program_text.like('%JHU%')
            ),
            or_(
                Applicant.program_name.like('%Computer Science%'),
                Applicant.raw_program_text.like('%Computer Science%'),
                Applicant.raw_program_text.like('%CS%')
            ),
            or_(
                Applicant.degree_type.like('%Master%'),
                Applicant.degree_type.like('%MS%'),
                Applicant.raw_program_text.like('%Master%'),
                Applicant.raw_program_text.like('%MS%')
            )
        )
    )
    q8_count = session.scalar(stmt8)
    print(f"Question 8:\nOriginal-field count: {q8_count}\n")

    # Question 9: LLM-field count & Difference - 完全对齐 SQL 逻辑
    stmt9 = select(func.count(Applicant.p_id)).where(
        and_(
            or_(
                Applicant.llm_generated_university.like('%Johns Hopkins%'),
                Applicant.university.like('%Johns Hopkins%'),
                Applicant.university.like('%JHU%'),
                Applicant.raw_program_text.like('%Johns Hopkins%'),
                Applicant.raw_program_text.like('%JHU%')
            ),
            or_(
                Applicant.llm_generated_program.like('%Computer Science%'),
                Applicant.program_name.like('%Computer Science%'),
                Applicant.raw_program_text.like('%Computer Science%'),
                Applicant.raw_program_text.like('%CS%')
            ),
            or_(
                Applicant.degree_type.like('%Master%'),
                Applicant.degree_type.like('%MS%'),
                Applicant.raw_program_text.like('%Master%'),
                Applicant.raw_program_text.like('%MS%')
            )
        )
    )
    llm_count = session.scalar(stmt9)
    diff = llm_count - q8_count
    print("Question 9:")
    print(f"Original-field count: {q8_count}")
    print(f"LLM-field count: {llm_count}")
    print(f"Difference: {diff:+d}\n")

    # Question 10 (Selected Original Question): Masters vs PhD Comparison
    phd_stmt = select(
        func.count(Applicant.p_id),
        func.avg(Applicant.gpa)
    ).where(
        or_(Applicant.raw_program_text.like('%PhD%'), Applicant.degree_type.like('%PhD%'))
    )
    
    masters_stmt = select(
        func.count(Applicant.p_id),
        func.avg(Applicant.gpa)
    ).where(
        ~or_(Applicant.raw_program_text.like('%PhD%'), Applicant.degree_type.like('%PhD%'))
    )

    phd_count, phd_gpa = session.execute(phd_stmt).fetchone()
    m_count, m_gpa = session.execute(masters_stmt).fetchone()

    print("Question 10:\nDegree Type Applicant Count & Average GPA:")
    print(f"  - Masters: {m_count} applicants (Avg GPA: {m_gpa:.2f})")
    print(f"  - PhD: {phd_count} applicants (Avg GPA: {phd_gpa:.2f})\n")

    session.close()

if __name__ == "__main__":
    run_orm_queries()

