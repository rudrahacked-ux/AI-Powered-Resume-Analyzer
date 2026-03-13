import sqlite3

DB_FILE = "student_resume_placement.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Add new columns (IF NOT EXISTS workaround)
try:
    cur.execute("ALTER TABLE resume_analysis ADD COLUMN keyword_skills TEXT")
except:
    print("keyword_skills column already exists")

try:
    cur.execute("ALTER TABLE resume_analysis ADD COLUMN llm_skills TEXT")
except:
    print("llm_skills column already exists")

try:
    cur.execute("ALTER TABLE resume_analysis ADD COLUMN final_skills TEXT")
except:
    print("final_skills column already exists")

conn.commit()
conn.close()

print("✅ Database Updated successfully")
