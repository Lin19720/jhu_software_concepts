import os
import json
import sqlite3

def load_data():
    db_path = "gradcafe.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 确保 applicants 表已建立
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applicants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_program_text TEXT,
        university TEXT,
        program_name TEXT,
        comments TEXT,
        date_added TEXT,
        url TEXT,
        applicant_status TEXT,
        decision_date TEXT,
        term_and_year TEXT,
        student_type TEXT,
        degree_type TEXT,
        gpa REAL,
        gre REAL,
        gre_v REAL,
        gre_aw REAL,
        llm_generated_university TEXT,
        llm_generated_program TEXT
    );
    """)

    # 优先使用 module_2 的全量/增量 JSON 数据
    json_path = "../module_2/applicant_data.json" if os.path.exists("../module_2/applicant_data.json") else "applicant_data.json"
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found!")
        conn.close()
        return

    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    # 采用 INSERT OR IGNORE / 过滤重复插入逻辑
    inserted_count = 0
    for r in records:
        # 通过 url 或 raw_program_text 简单查重
        cursor.execute("SELECT id FROM applicants WHERE url = ? AND raw_program_text = ?", (r.get("url"), r.get("raw_program_text")))
        if cursor.fetchone() is None:
            cursor.execute("""
            INSERT INTO applicants (
                raw_program_text, university, program_name, comments, date_added, url,
                applicant_status, decision_date, term_and_year, student_type, degree_type,
                gpa, gre, gre_v, gre_aw, llm_generated_university, llm_generated_program
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r.get("raw_program_text"), r.get("university"), r.get("program_name"), r.get("comments"),
                r.get("date_added"), r.get("url"), r.get("applicant_status"), r.get("decision_date"),
                r.get("term_and_year"), r.get("student_type"), r.get("degree_type"),
                r.get("gpa"), r.get("gre"), r.get("gre_v"), r.get("gre_aw"),
                r.get("llm_generated_university"), r.get("llm_generated_program")
            ))
            inserted_count += 1

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM applicants;")
    total = cursor.fetchone()[0]
    conn.close()

    print(f"[成功] 新增插入 {inserted_count} 条记录，当前 applicants 表共有 {total} 条记录！")

if __name__ == "__main__":
    load_data()
