import sqlite3

DB_FILE = "student_resume_placement.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS job_roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE,
    required_skills TEXT
)
""")

conn.commit()
conn.close()

print("✅ job_roles table created successfully")
