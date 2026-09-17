import sqlite3

def run_queries():
    conn = sqlite3.connect("gradcafe.db")
    cur = conn.cursor()

    print("==================== DATA ANALYSIS RESULTS ====================\n")

    # Question 1: Fall 2026 申请人数
    q1_sql = "SELECT COUNT(*) FROM applicants WHERE term_and_year LIKE '%Fall 2026%' OR raw_program_text LIKE '%Fall 2026%';"
    cur.execute(q1_sql)
    q1_count = cur.fetchone()[0]
    print(f"Question 1:\nFall 2026 applicant count: {q1_count}\n")

    # Question 2: 国际生比例
    q2_sql = "SELECT (COUNT(CASE WHEN raw_program_text LIKE '%International%' OR student_type LIKE '%International%' THEN 1 END) * 100.0 / COUNT(*)) FROM applicants;"
    cur.execute(q2_sql)
    q2_pct = cur.fetchone()[0]
    print(f"Question 2:\nPercent international: {q2_pct:.2f}%\n" if q2_pct is not None else "Question 2:\nPercent international: N/A\n")

    # Question 3: 整体平均成绩
    q3_sql = "SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw) FROM applicants;"
    cur.execute(q3_sql)
    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()
    print("Question 3:")
    print(f"Average GPA: {avg_gpa:.2f}" if avg_gpa is not None else "Average GPA: N/A")
    print(f"Average GRE Quantitative: {avg_gre:.2f}" if avg_gre is not None else "Average GRE Quantitative: N/A")
    print(f"Average GRE Verbal: {avg_gre_v:.2f}" if avg_gre_v is not None else "Average GRE Verbal: N/A")
    print(f"Average GRE Analytical Writing: {avg_gre_aw:.2f}\n" if avg_gre_aw is not None else "Average GRE Analytical Writing: N/A\n")

    # Question 4: 美国本土学生 GPA
    q4_sql = "SELECT AVG(gpa) FROM applicants WHERE student_type = 'American' AND gpa IS NOT NULL;"
    cur.execute(q4_sql)
    q4_gpa = cur.fetchone()[0]
    print(f"Question 4:\nAverage GPA: {q4_gpa:.2f}\n" if q4_gpa is not None else "Question 4:\nAverage GPA: N/A\n")

    # Question 5: Fall 2025 录取率
    q5_sql = "SELECT (COUNT(CASE WHEN applicant_status LIKE '%Accepted%' THEN 1 END) * 100.0 / COUNT(*)) FROM applicants WHERE term_and_year LIKE '%Fall 2025%' OR raw_program_text LIKE '%Fall 2025%';"
    cur.execute(q5_sql)
    q5_pct = cur.fetchone()[0]
    print(f"Question 5:\nFall 2025 acceptance percentage: {q5_pct:.2f}%\n" if q5_pct is not None else "Question 5:\nFall 2025 acceptance percentage: N/A\n")

    # Question 6: Fall 2025 被录取学生 GPA
    q6_sql = "SELECT AVG(gpa) FROM applicants WHERE (term_and_year LIKE '%Fall 2025%' OR raw_program_text LIKE '%Fall 2025%') AND applicant_status LIKE '%Accepted%' AND gpa IS NOT NULL;"
    cur.execute(q6_sql)
    q6_gpa = cur.fetchone()[0]
    print(f"Question 6:\nAverage GPA: {q6_gpa:.2f}\n" if q6_gpa is not None else "Question 6:\nAverage GPA: N/A\n")

    # Question 7: JHU CS Master 申请人数
    q7_sql = """
    SELECT COUNT(*) 
    FROM applicants 
    WHERE (university LIKE '%Johns Hopkins%' OR university LIKE '%JHU%' OR raw_program_text LIKE '%Johns Hopkins%' OR raw_program_text LIKE '%JHU%') 
      AND (program_name LIKE '%Computer Science%' OR raw_program_text LIKE '%Computer Science%' OR raw_program_text LIKE '%CS%')
      AND (degree_type LIKE '%Master%' OR degree_type LIKE '%MS%' OR raw_program_text LIKE '%Master%' OR raw_program_text LIKE '%MS%');
    """
    cur.execute(q7_sql)
    q7_count = cur.fetchone()[0]
    print(f"Question 7:\nJHU CS Master's applicant count: {q7_count}\n")

    # Question 8
    print(f"Question 8:\nOriginal-field count: {q7_count}\n")

    # Question 9
    q9_sql = """
    SELECT COUNT(*) 
    FROM applicants 
    WHERE (llm_generated_university LIKE '%Johns Hopkins%' OR university LIKE '%Johns Hopkins%' OR university LIKE '%JHU%' OR raw_program_text LIKE '%Johns Hopkins%' OR raw_program_text LIKE '%JHU%') 
      AND (llm_generated_program LIKE '%Computer Science%' OR program_name LIKE '%Computer Science%' OR raw_program_text LIKE '%Computer Science%' OR raw_program_text LIKE '%CS%')
      AND (degree_type LIKE '%Master%' OR degree_type LIKE '%MS%' OR raw_program_text LIKE '%Master%' OR raw_program_text LIKE '%MS%');
    """
    cur.execute(q9_sql)
    llm_count = cur.fetchone()[0]
    diff = llm_count - q7_count

    print("Question 9:")
    print(f"Original-field count: {q7_count}")
    print(f"LLM-field count: {llm_count}")
    print(f"Difference: {diff:+d}\n")

    # Question 10: Masters vs PhD Applicant Comparison
    q10_sql = """
    SELECT 
        CASE 
            WHEN raw_program_text LIKE '%PhD%' OR degree_type LIKE '%PhD%' THEN 'PhD'
            ELSE 'Masters'
        END AS degree_category,
        COUNT(*) AS total_count,
        ROUND(AVG(gpa), 2) AS avg_gpa
    FROM applicants
    GROUP BY degree_category;
    """
    cur.execute(q10_sql)
    deg_stats = cur.fetchall()
    print("Question 10:\nDegree Type Applicant Count & Average GPA:")
    for deg, count, gpa in deg_stats:
        gpa_str = f"{gpa:.2f}" if gpa is not None else "N/A"
        print(f"  - {deg}: {count} applicants (Avg GPA: {gpa_str})")
    print()

    # Question 11: High GRE Quant (>=165) vs Lower GRE Acceptance Rate Comparison
    q11_sql = """
    SELECT 
        CASE 
            WHEN gre >= 165 THEN 'High Quant (>=165)'
            ELSE 'Lower Quant (<165)'
        END AS gre_bracket,
        COUNT(*) AS total_applicants,
        COUNT(CASE WHEN applicant_status LIKE '%Accepted%' THEN 1 END) AS accepted_count,
        ROUND(COUNT(CASE WHEN applicant_status LIKE '%Accepted%' THEN 1 END) * 100.0 / COUNT(*), 2) AS acceptance_rate
    FROM applicants
    WHERE gre IS NOT NULL AND gre BETWEEN 130 AND 170
    GROUP BY gre_bracket;
    """
    cur.execute(q11_sql)
    gre_stats = cur.fetchall()
    print("Question 11:\nAcceptance Rate Comparison by GRE Quant Score (>=165 vs <165):")
    for bracket, total, acc, rate in gre_stats:
        rate_str = f"{rate:.2f}%" if rate is not None else "N/A"
        print(f"  - {bracket}: {rate_str} ({acc}/{total} accepted)")
    print()

    conn.close()

if __name__ == "__main__":
    run_queries()
