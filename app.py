from flask import Flask, render_template, request, send_from_directory
from pdf_report import generate_pdf_report
import os
import time

from resume_extractor import analyze_resume

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER

# create folders if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- DOWNLOAD REPORT ----------
@app.route("/reports/<path:filename>")
def download_report(filename):
    return send_from_directory(app.config["REPORT_FOLDER"], filename)


# ---------- UPLOAD RESUME ----------
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        file = request.files["resume"]
        name = request.form["name"]
        email = request.form["email"]
        branch = request.form["branch"]
        cgpa = float(request.form["cgpa"])
        projects = int(request.form["projects"])
        internships = int(request.form["internships"])

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # simulate processing delay
        time.sleep(1)

        # ---------- RUN AI ANALYSIS ----------
        result = analyze_resume(
            filepath,
            name,
            email,
            branch,
            cgpa,
            projects,
            internships
        )

        # ---------- GENERATE PDF ----------
        filename = "resume_analysis_report.pdf"
        generate_pdf_report(result, filename)

        pdf_path = f"reports/{filename}"

        # ---------- DATA FOR CHARTS ----------
        skills = result["final_skills"][:6]  # top 6 skills for radar chart
        ats_score = result["ats_score"]
        resume_score = result["score"]
        placement_probability = result["placement_probability"]

        return render_template(
            "result.html",
            result=result,
            pdf_path=pdf_path,
            skills=skills,
            ats_score=ats_score,
            resume_score=resume_score,
            placement_probability=placement_probability
        )

    return render_template("upload.html")


# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True)