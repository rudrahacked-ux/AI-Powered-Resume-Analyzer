"""
resume_extractor.py
-------------------
PDF & DOCX Resume Skill Extractor
Keyword + LLM based
ATS Job Role Matching
"""
import joblib
import numpy as np
import os
import re
import json
import sqlite3
import argparse
from datetime import datetime

from pypdf import PdfReader
import docx

from llm_skill_extractor import extract_skills_llm

DB_FILE = "student_resume_placement.db"
SKILLS_FILE = "skills.json"


# ---------- SKILL UTIL ----------
def load_skills(skills_file):
    with open(skills_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = []
    for category in data.values():
        for skill in category:
            skills.append(skill.lower().strip())

    return sorted(set(skills))


def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\+\#\.\- ]", " ", text)
    return text


# ---------- TEXT EXTRACTION ----------
def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return " ".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(path):
    document = docx.Document(path)
    return " ".join(p.text for p in document.paragraphs)


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Only PDF and DOCX supported")


# ---------- KEYWORD MATCH ----------
def match_skills(text, skills):
    cleaned = clean_text(text)
    return sorted({s for s in skills if s in cleaned})


# ---------- DATABASE ----------
def connect_db():
    return sqlite3.connect(DB_FILE)


def ensure_tables(conn):
    cur = conn.cursor()

    # ---------- STUDENTS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        branch TEXT,
        cgpa REAL
    )
    """)

    # ---------- RESUME ANALYSIS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resume_analysis (
        analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        score INTEGER,
        analysis_date TEXT,
        keyword_skills TEXT,
        llm_skills TEXT,
        final_skills TEXT
    )
    """)

    # ---------- PLACEMENT PREDICTION ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS placement_prediction (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        best_role TEXT,
        ats_score INTEGER,
        placement_probability REAL,
        readiness_level TEXT,
        suggestions TEXT,
        weak_areas TEXT,
        created_at TEXT
    )
    """)

    # ---------- JOB ROLES ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_roles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT UNIQUE,
        required_skills TEXT
    )
    """)

    # ---------- AUTO INSERT DEFAULT JOB ROLES IF EMPTY ----------
    cur.execute("SELECT COUNT(*) FROM job_roles")
    count = cur.fetchone()[0]

    if count == 0:
        roles = {
            "Software Engineer": [
                "c", "c++", "java", "python",
                "data structures", "algorithms",
                "git", "github", "sql"
            ],
            "Data Analyst": [
                "python", "sql", "pandas", "numpy",
                "data analysis", "statistics",
                "excel", "visualization"
            ],
            "Machine Learning Engineer": [
                "python", "machine learning", "numpy",
                "pandas", "scikit-learn", "nlp",
                "deep learning"
            ]
        }

        for role, skills in roles.items():
            cur.execute("""
                INSERT INTO job_roles (role_name, required_skills)
                VALUES (?, ?)
            """, (role, json.dumps(skills)))

    conn.commit()



def get_or_create_student(conn, name, email, branch, cgpa):
    cur = conn.cursor()
    cur.execute("SELECT student_id FROM students WHERE email=?", (email,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute("""
        INSERT INTO students (name, email, branch, cgpa)
        VALUES (?, ?, ?, ?)
    """, (name, email, branch, cgpa))

    conn.commit()
    return cur.lastrowid


def insert_resume_analysis(conn, student_id, keyword_skills, llm_skills, final_skills, score):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resume_analysis
        (student_id, score, analysis_date, keyword_skills, llm_skills, final_skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        score,
        datetime.now().isoformat(),
        json.dumps(keyword_skills),
        json.dumps(llm_skills),
        json.dumps(final_skills)
    ))
    conn.commit()

def insert_placement_prediction(conn, student_id, best_role,
                                ats_score, placement_probability,
                                readiness_level, suggestions,
                                weak_areas):

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO placement_prediction
        (student_id, best_role, ats_score,
         placement_probability, readiness_level,
         suggestions, weak_areas, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        best_role,
        ats_score,
        placement_probability,
        readiness_level,
        json.dumps(suggestions),
        json.dumps(weak_areas),
        datetime.now().isoformat()
    ))

    conn.commit()




# ---------- JOB ROLE MATCHING ----------
def fetch_job_roles(conn):
    cur = conn.cursor()
    cur.execute("SELECT role_name, required_skills FROM job_roles")
    rows = cur.fetchall()

    roles = []
    for role_name, skills_json in rows:
        skills = json.loads(skills_json)
        skills = [s.lower().strip() for s in skills]

        roles.append({
            "role": role_name,
            "skills": skills
        })

    return roles


def calculate_ats_score(resume_skills, job_skills):
    matched = set(resume_skills) & set(job_skills)
    score = int((len(matched) / len(job_skills)) * 100) if job_skills else 0
    return score, sorted(matched)


def find_best_job_match(resume_skills, job_roles):
    best_role = None
    best_score = 0
    best_matched = []

    for role in job_roles:
        score, matched = calculate_ats_score(resume_skills, role["skills"])
        if score > best_score:
            best_score = score
            best_role = role["role"]
            best_matched = matched

    return best_role, best_score, best_matched


# ---------- SCORING ----------
def compute_score(skill_count):
    return min(100, skill_count * 10)

# ---------- ML MODEL ----------
def load_ml_model():
    model = joblib.load("placement_model.pkl")
    scaler = joblib.load("scaler.pkl")
    return model, scaler

def predict_placement(model, scaler, cgpa, skills_count, projects, internships, ats_score, resume_score):
    
    features = np.array([[cgpa, skills_count, projects, internships, ats_score, resume_score]])
    
    features_scaled = scaler.transform(features)
    
    probability = model.predict_proba(features_scaled)[0][1] * 100
    
    return round(probability, 2)



# ---------- CORE ----------
def analyze_resume(file_path, name, email, branch, cgpa, projects, internships):

    print("ANALYZE STARTED")

    # ---------- Load Skills & Extract Text ----------
    skills_master = load_skills(SKILLS_FILE)
    text = extract_text(file_path)

    # ---------- Skill Extraction ----------
    keyword_skills = match_skills(text, skills_master)
    llm_skills = extract_skills_llm(text)

    final_skills = sorted(set(keyword_skills + llm_skills))
    resume_score = compute_score(len(final_skills))

    # ---------- Database ----------
    conn = connect_db()
    ensure_tables(conn)

    student_id = get_or_create_student(conn, name, email, branch, cgpa)

    # ---------- Job Role Matching ----------
    job_roles = fetch_job_roles(conn)

    best_role, ats_score, matched_skills = find_best_job_match(
        final_skills,
        job_roles
    )

    print("BEST MATCHING ROLE:", best_role)
    print("ATS SCORE:", ats_score)

    # ---------- SKILL GAP ANALYSIS ----------
    required_skills = []
    missing_skills = []

    for role in job_roles:
        if role["role"] == best_role:
            required_skills = role["skills"]
            break

    if required_skills:
        missing_skills = list(set(required_skills) - set(final_skills))

    # ---------- ML Placement Prediction ----------
    model, scaler = load_ml_model()

    placement_probability = predict_placement(
        model,
        scaler,
        cgpa,
        len(final_skills),
        projects,
        internships,
        ats_score,
        resume_score
    )

    # ---------- Readiness Logic ----------
    if placement_probability >= 75:
        readiness_level = "High"
    elif placement_probability >= 50:
        readiness_level = "Medium"
    else:
        readiness_level = "Low"

    # ---------- Suggestions ----------
    suggestions = []
    weak_areas = []

    if ats_score < 60:
        suggestions.append("Improve role-specific skills.")
        weak_areas.append("Low ATS match")

    if cgpa < 7:
        suggestions.append("Improve academic performance.")
        weak_areas.append("Low CGPA")

    if internships == 0:
        suggestions.append("Gain internship experience.")
        weak_areas.append("No internships")

    if projects < 2:
        suggestions.append("Build more practical projects.")
        weak_areas.append("Low project count")

    # ---------- Store Placement Prediction ----------
    insert_placement_prediction(
        conn,
        student_id,
        best_role,
        ats_score,
        placement_probability,
        readiness_level,
        suggestions,
        weak_areas
    )

    # ---------- Store Resume Analysis ----------
    insert_resume_analysis(
        conn,
        student_id,
        keyword_skills,
        llm_skills,
        final_skills,
        resume_score
    )

    conn.close()

    print("ANALYZE FINISHED")

    return {
        "student_id": student_id,
        "keyword_skills": keyword_skills,
        "llm_skills": llm_skills,
        "final_skills": final_skills,
        "score": resume_score,
        "best_role": best_role,
        "ats_score": ats_score,
        "placement_probability": placement_probability,
        "readiness_level": readiness_level,
        "suggestions": suggestions,
        "missing_skills": missing_skills
    }


# ---------- CLI ----------
def main():
    print("MAIN STARTED")

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--cgpa", type=float, required=True)
    parser.add_argument("--projects", type=int, required=True)
    parser.add_argument("--internships", type=int, required=True)


    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("ERROR: Resume file not found")
        return

    result = analyze_resume(
        args.file,
        args.name,
        args.email,
        args.branch,
        args.cgpa,
        args.projects,
        args.internships
    )

    print("\n---- RESULT ----")
    print("Student ID:", result["student_id"])
    print("Keyword Skills:", result["keyword_skills"])
    print("LLM Skills:", result["llm_skills"])
    print("Final Skills:", result["final_skills"])
    print("Resume Score:", result["score"])
    print("Best Matching Role:", result["best_role"])
    print("ATS Score:", result["ats_score"])
    print("Placement Probability:", result["placement_probability"])
    print("Readiness Level:", result["readiness_level"])
    print("Suggestions:", result["suggestions"])
    print("----------------")


if __name__ == "__main__":
    main()
