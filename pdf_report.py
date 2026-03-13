from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_pdf_report(result, filename):

    reports_dir = "reports"

    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    file_path = os.path.join(reports_dir, filename)

    c = canvas.Canvas(file_path, pagesize=letter)

    width, height = letter

    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "AI Resume Analysis Report")

    y -= 40

    c.setFont("Helvetica", 12)

    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y -= 30

    c.drawString(50, y, f"Student ID: {result['student_id']}")

    y -= 20
    c.drawString(50, y, f"Best Matching Role: {result['best_role']}")

    y -= 20
    c.drawString(50, y, f"ATS Score: {result['ats_score']}%")

    y -= 20
    c.drawString(50, y, f"Placement Probability: {result['placement_probability']}%")

    y -= 20
    c.drawString(50, y, f"Readiness Level: {result['readiness_level']}")

    y -= 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Extracted Skills")

    y -= 20
    c.setFont("Helvetica", 12)

    for skill in result["final_skills"]:

        if y < 50:
            c.showPage()
            y = height - 50

        c.drawString(60, y, f"- {skill}")
        y -= 18

    y -= 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Suggestions")

    y -= 20
    c.setFont("Helvetica", 12)

    for s in result["suggestions"]:

        if y < 50:
            c.showPage()
            y = height - 50

        c.drawString(60, y, f"- {s}")
        y -= 18

    c.save()

    return file_path