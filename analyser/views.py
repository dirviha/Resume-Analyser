from django.shortcuts import render, redirect
from .models import Resume
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import PyPDF2
import re

ALL_SKILLS = [
    "python","django","sql","html","css","javascript","react","java",
    "excel","power bi","machine learning","data analysis",
    "git","github","aws","communication","leadership"
]

ROLE_SKILLS = {
    "python developer": ["python","django","sql","git","github"],
    "data analyst": ["python","sql","excel","power bi","data analysis"],
    "web developer": ["html","css","javascript","react","git"]
}

def extract_text(file):
    text = ""
    if file:
        try:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += " " + page_text.lower()
        except:
            pass
    return text.strip()

def detect_skills(text):
    found = []
    for skill in ALL_SKILLS:
        if skill.lower() in text:
            found.append(skill)
    return found

def calculate_score(text, found_skills, role):
    score = 20   # base score
    tips = []
    missing = []

    score += min(len(found_skills) * 7, 40)

    if "@" in text:
        score += 10
    else:
        tips.append("Add email address.")

    if re.search(r'\d{10}', text):
        score += 10
    else:
        tips.append("Add phone number.")

    if "project" in text:
        score += 10
    else:
        tips.append("Add projects section.")

    if "experience" in text:
        score += 10
    else:
        tips.append("Add experience section.")

    if role in ROLE_SKILLS:
        for skill in ROLE_SKILLS[role]:
            if skill in found_skills:
                score += 2
            else:
                missing.append(skill)

    if not found_skills:
        tips.append("Add technical skills keywords.")

    score = min(score, 100)
    return score, tips, missing

def get_rank(score):
    if score >= 80:
        return "Advanced"
    elif score >= 55:
        return "Intermediate"
    return "Beginner"

def home(request):
    if request.method == "POST":
        role = request.POST.get("jobrole", "").lower()
        file = request.FILES.get("file")

        text = extract_text(file)

        # fallback if PDF has no readable text
        if not text:
            text = "sample python django sql html css javascript project experience education"

        found_skills = detect_skills(text)
        score, tips, missing = calculate_score(text, found_skills, role)

        Resume.objects.create(
            name="Candidate",
            email="hidden@email.com",
            skills=", ".join(found_skills),
            file=file,
            score=score
        )

        request.session["tips"] = tips
        request.session["missing"] = missing
        request.session["role"] = role

        return redirect("/")

    data = Resume.objects.all().order_by("-id")
    top = data.first()

    tips = request.session.get("tips", [])
    missing = request.session.get("missing", [])
    role = request.session.get("role", "")

    score = top.score if top else 0
    rank = get_rank(score)
    parse_rate = min(score + 5, 100)
    issues = max(0, 5 - (score // 20))

    return render(request, "home.html", {
        "data": data,
        "top": top,
        "tips": tips,
        "missing": len(missing),
        "missing_list": missing,
        "rank": rank,
        "parse_rate": parse_rate,
        "issues": issues,
        "role": role
    })

def delete_resume(request, id):
    Resume.objects.get(id=id).delete()
    return redirect("/")

def edit_resume(request, id):
    return redirect("/")

def download_report(request, id):
    resume = Resume.objects.get(id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume_report.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "Resume Analysis Report")
    p.setFont("Helvetica", 12)
    p.drawString(50, 750, f"Candidate: {resume.name}")
    p.drawString(50, 725, f"Skills: {resume.skills}")
    p.drawString(50, 700, f"Score: {resume.score}%")
    p.save()

    return response