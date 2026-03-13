import sqlite3

conn = sqlite3.connect("student_resume_placement.db")
cur = conn.cursor()

print("---- TABLES IN DATABASE ----")
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
for t in tables:
    print(t)

print("\n---- resume_analysis TABLE INFO ----")
cur.execute("PRAGMA table_info(resume_analysis);")
rows = cur.fetchall()

if not rows:
    print("❌ resume_analysis table NOT FOUND")
else:
    for row in rows:
        print(row)

conn.close()
