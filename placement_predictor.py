import sqlite3
import json
from datetime import datetime

DB_FILE = "student_resume_placement.db"

# ---------- NORMALIZATION HELPERS ----------

def normalize_cgpa(cgpa):
    if cgpa >= 8.5:
        return 100
    elif cgpa >= 8.0:
        return 85
    elif cgpa >= 7.0:
        return 70
    elif cgpa >= 6.0:
        return 55
    else:
        return 40


def experience_score(internship_count, project_count):
    if internship_count >= 1 and project_count >= 2:
        return 100
    elif internship_count >= 1 and project_count == 1:
        return 80
    elif internship_count == 0 and project_count >= 2:
        return 60
    elif project_count == 1:
        return 40
    else:
        return 20


def readiness_level(prob):
    if prob >= 75:
        return "High"
    elif prob >= 50:
        return "Medium"
    else:
        return "Low"


# ---------- CORE PREDICTION ----------

def predict_placement(
    student_id,
    resume_score,
    ats_score,
    cgpa,
    final_skills,
    internship_count=0,
    project_count=2,
    best_role=None
):
    cgpa_score = normalize_cgpa(cgpa)
    exp_score = experience_score(internship_count, project_count)

    placement_probability = (
        resume_score * 0.40 +
        ats_score * 0.30 +
        cgpa_score * 0.20 +
        exp_score * 0.10
    )

    placement_probability = round(placement_probability, 2)
    readiness = readiness_level(placement_probability)

    # ---------- Strengths & Weak Areas ----------
    strengths = []
    weaknesses = []

    if ats_score >= 60:
        strengths.append("Good role-specific skill match")
    else:
        weaknesses.append("Low ATS compatibility")

    if cgpa >= 7:
        strengths.append("Strong academic performance")
    else:
        weaknesses.append("Low CGPA")

    if len(final_skills) >= 10:
        strengths.append("Good skill coverage")
    else:
        weaknesses.append("Limited skill set")

    suggestions = []
    if "Low ATS compatibility" in weaknesses:
        suggestions.append("Improve role-specific skills")
    if "Low CGPA" in weaknesses:
        suggestions.append("Focus on academic improvement")
    if "Limited skill set" in weaknesses:
        suggestions.append("Add projects and certifications")

    # ---------- STORE IN DB ----------
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO placement_prediction
        (student_id, placement_probability, readiness_level, best_role,
         ats_score, weak_areas, suggestions, generated_on)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        placement_probability,
        readiness,
        best_role,
        ats_score,
        ", ".join(weaknesses),
        ", ".join(suggestions),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return {
        
        "placement_probability": placement_probability,
        "readiness_level": readiness,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }
