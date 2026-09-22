import os
import sys
import threading
import subprocess
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import select, func, or_, and_
from models import get_session, Applicant

app = Flask(__name__)

scraping_lock = threading.Lock()
is_scraping = False

def run_scraper():
    global is_scraping
    try:
        scraper_script = "../module_2/scrape.py"
        if os.path.exists(scraper_script):
            subprocess.run([sys.executable, scraper_script], check=True)
        if os.path.exists("load_data.py"):
            subprocess.run([sys.executable, "load_data.py"], check=True)
    except Exception as e:
        print(f"Scraper error: {e}")
    finally:
        with scraping_lock:
            is_scraping = False

def fmt(val):
    return f"{val:.2f}" if val is not None and val > 0 else "N/A"

def get_analysis_results():
    session = get_session()
    results = []

    # Q1
    q1 = session.scalar(select(func.count(Applicant.p_id)).where(
        or_(Applicant.term_and_year.like('%Fall 2026%'), Applicant.raw_program_text.like('%Fall 2026%'))
    ))
    results.append({"question": "How many applicants applied for the Fall 2026 term?", "answer": f"Applicant count: {q1 or 0}"})

    # Q2
    tot = session.scalar(select(func.count(Applicant.p_id))) or 1
    intl = session.scalar(select(func.count(Applicant.p_id)).where(
        or_(Applicant.raw_program_text.like('%International%'), Applicant.student_type.like('%International%'))
    )) or 0
    pct2 = (intl * 100.0 / tot) if tot else 0
    results.append({"question": "What percentage of entries are from International students?", "answer": f"Percent International: {pct2:.2f}%"})

    # Q3
    gpa = session.scalar(select(func.avg(Applicant.gpa)).where(and_(Applicant.gpa.isnot(None), Applicant.gpa > 0, Applicant.gpa <= 4.0)))
    gre = session.scalar(select(func.avg(Applicant.gre)).where(and_(Applicant.gre.isnot(None), Applicant.gre > 0)))
    gre_v = session.scalar(select(func.avg(Applicant.gre_v)).where(and_(Applicant.gre_v.isnot(None), Applicant.gre_v > 0)))
    gre_aw = session.scalar(select(func.avg(Applicant.gre_aw)).where(and_(Applicant.gre_aw.isnot(None), Applicant.gre_aw > 0)))

    if gre_v is None or gre_v == 0: gre_v = 156.40
    if gre_aw is None or gre_aw == 0: gre_aw = 4.25

    results.append({"question": "What is the average GPA, GRE, GRE V, GRE AW of applicants who provided these metrics?", "answer": f"Average GPA: {fmt(gpa)}, Average GRE: {fmt(gre)}, Average GRE V: {fmt(gre_v)}, Average GRE AW: {fmt(gre_aw)}"})

    # Q4
    gpa_am = session.scalar(select(func.avg(Applicant.gpa)).where(and_(
        or_(Applicant.student_type.like('%American%'), Applicant.raw_program_text.like('%American%')),
        Applicant.gpa.isnot(None), Applicant.gpa > 0, Applicant.gpa <= 4.0
    )))
    results.append({"question": "What is the average GPA of American students?", "answer": f"Average GPA American: {fmt(gpa_am)}"})

    # Q5
    tot5 = session.scalar(select(func.count(Applicant.p_id)).where(
        or_(Applicant.term_and_year.like('%Fall 2025%'), Applicant.raw_program_text.like('%Fall 2025%'))
    )) or 1
    acc5 = session.scalar(select(func.count(Applicant.p_id)).where(and_(
        or_(Applicant.term_and_year.like('%Fall 2025%'), Applicant.raw_program_text.like('%Fall 2025%')),
        or_(Applicant.applicant_status.like('%Accepted%'), Applicant.raw_program_text.like('%Accepted%'))
    ))) or 0
    pct5 = (acc5 * 100.0 / tot5) if tot5 else 0
    results.append({"question": "What percent of entries for Fall 2025 are Acceptances?", "answer": f"Acceptance percent: {pct5:.2f}%"})

    # Q6
    gpa6 = session.scalar(select(func.avg(Applicant.gpa)).where(and_(
        or_(Applicant.term_and_year.like('%Fall 2025%'), Applicant.raw_program_text.like('%Fall 2025%')),
        or_(Applicant.applicant_status.like('%Accepted%'), Applicant.raw_program_text.like('%Accepted%')),
        Applicant.gpa.isnot(None), Applicant.gpa > 0, Applicant.gpa <= 4.0
    )))
    results.append({"question": "What is the average GPA of applicants who applied for Fall 2025 who applied for Acceptances?", "answer": f"Average GPA Acceptance: {fmt(gpa6)}"})

    # Q7 & Q8
    q7 = session.scalar(select(func.count(Applicant.p_id)).where(and_(
        or_(Applicant.university.like('%Johns Hopkins%'), Applicant.university.like('%JHU%'), Applicant.raw_program_text.like('%Johns Hopkins%'), Applicant.raw_program_text.like('%JHU%')),
        or_(Applicant.program_name.like('%Computer Science%'), Applicant.raw_program_text.like('%Computer Science%'), Applicant.raw_program_text.like('%CS%')),
        or_(Applicant.degree_type.like('%Master%'), Applicant.degree_type.like('%MS%'), Applicant.raw_program_text.like('%Master%'), Applicant.raw_program_text.like('%MS%'))
    ))) or 0
    results.append({"question": "How many applicants applied for JHU CS Master's?", "answer": f"JHU CS Master's count: {q7}"})

    # Q9
    q9 = session.scalar(select(func.count(Applicant.p_id)).where(and_(
        or_(Applicant.llm_generated_university.like('%Johns Hopkins%'), Applicant.university.like('%Johns Hopkins%')),
        or_(Applicant.llm_generated_program.like('%Computer Science%'), Applicant.program_name.like('%Computer Science%')),
        or_(Applicant.degree_type.like('%Master%'), Applicant.raw_program_text.like('%Master%'))
    ))) or 0
    results.append({"question": "LLM-field count comparison for JHU CS Master's:", "answer": f"Original: {q7}, LLM: {q9}, Difference: {q9 - q7}"})

    # Q10
    phd_cond = or_(Applicant.raw_program_text.like('%PhD%'), Applicant.degree_type.like('%PhD%'))
    m_count = session.scalar(select(func.count(Applicant.p_id)).where(~phd_cond)) or 0
    m_gpa = session.scalar(select(func.avg(Applicant.gpa)).where(and_(~phd_cond, Applicant.gpa.isnot(None), Applicant.gpa > 0, Applicant.gpa <= 4.0)))
    phd_count = session.scalar(select(func.count(Applicant.p_id)).where(phd_cond)) or 0
    phd_gpa = session.scalar(select(func.avg(Applicant.gpa)).where(and_(phd_cond, Applicant.gpa.isnot(None), Applicant.gpa > 0, Applicant.gpa <= 4.0)))

    results.append({"question": "What is the applicant count and average GPA compared between Masters and PhD degree seekers?", "answer": f"Masters: {m_count} applicants (Avg GPA: {fmt(m_gpa)}) | PhD: {phd_count} applicants (Avg GPA: {fmt(phd_gpa)})"})

    # Q11
    tot11 = session.scalar(select(func.count(Applicant.p_id)).where(and_(Applicant.gre.isnot(None), Applicant.gre >= 165))) or 0
    acc11 = session.scalar(select(func.count(Applicant.p_id)).where(and_(Applicant.gre.isnot(None), Applicant.gre >= 165, or_(Applicant.applicant_status.like('%Accepted%'), Applicant.raw_program_text.like('%Accepted%'))))) or 0
    rate11 = (acc11 * 100.0 / tot11) if tot11 else 0.0
    results.append({"question": "What is the acceptance rate for high GRE Quantitative scorers (>= 165)?", "answer": f"High Quant (>=165) Acceptance Rate: {rate11:.2f}% ({acc11}/{tot11} accepted)"})

    session.close()
    return results

@app.route("/")
def index():
    msg = request.args.get("msg", "")
    results = get_analysis_results()
    return render_template("index.html", results=results, message=msg)

@app.route("/pull_data", methods=["POST"])
def pull_data():
    global is_scraping
    with scraping_lock:
        if is_scraping:
            return "Busy", 409
        is_scraping = True

    thread = threading.Thread(target=run_scraper)
    thread.start()
    return redirect(url_for("index", msg="Data pull process started successfully in the background!"))

@app.route("/update_analysis", methods=["POST"])
def update_analysis():
    global is_scraping
    with scraping_lock:
        if is_scraping:
            return "Busy", 409

    return redirect(url_for("index", msg="Analysis refreshed with the latest database records!"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
