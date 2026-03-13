import sqlite3

DB_FILE = "student_resume_placement.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS placement_prediction (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    placement_probability REAL,
    readiness_level TEXT,
    best_role TEXT,
    ats_score REAL,
    weak_areas TEXT,
    suggestions TEXT,
    generated_on TEXT
)
""")

conn.commit()
conn.close()

print("✅ placement_prediction table ready")
