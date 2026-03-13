import sqlite3
import json

DB_FILE = "student_resume_placement.db"

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

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("DELETE FROM job_roles")

for role, skills in roles.items():
    cur.execute("""
        INSERT INTO job_roles (role_name, required_skills)
        VALUES (?, ?)
    """, (role, json.dumps(skills)))

conn.commit()
conn.close()

print("✅ Job roles inserted cleanly")
