from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import random
import spacy
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import io
from io import BytesIO
from xhtml2pdf import pisa
from flask import send_file
import re
from PIL import Image


load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


GEMINI_MODEL = None
MODEL_NAMES = [
    'gemini-2.0-flash-exp',     
    'gemini-2.0-flash',           
    'gemini-1.5-flash-latest',   
    'models/gemini-2.0-flash-exp',
    'models/gemini-1.5-flash',
]

for model_name in MODEL_NAMES:
    try:
        GEMINI_MODEL = genai.GenerativeModel(model_name)
        print(f"✅ Successfully loaded: {model_name}")
        break
    except Exception as e:
        print(f"❌ Failed to load {model_name}: {e}")
        continue

if not GEMINI_MODEL:
    print("⚠ Warning: No Gemini model could be loaded!")


app = Flask(__name__)
WHEREBY_API_KEY = os.getenv("WHEREBY_API_KEY")
                                                                     
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Updated database URI
db_user = os.getenv("DB_USERNAME", "root")
db_password = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "bput15")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "your_super_secret_key_bput")

db = SQLAlchemy(app)


generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}
safety_settings = [
  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]


# ==================== DATABASE MODELS ====================

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    logo = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    job_postings = db.relationship('JobPosting', backref='company', lazy=True, cascade='all, delete-orphan')
    mca_registered_name = db.Column(db.String(250), nullable=True)
    cin_number = db.Column(db.String(21), unique=True, nullable=True)
    gstin_number = db.Column(db.String(15), unique=True, nullable=True)
    mobile_number = db.Column(db.String(15), nullable=True)
    linkedin_profile = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='approved', nullable=False)

    
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(10), nullable=True)
    college = db.Column(db.String(200), nullable=False)
    registration_number = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    cgpa = db.Column(db.Float, default=0.0)
    profile_photo = db.Column(db.String(100))
    skills = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    projects = db.relationship('StudentProject', backref='student', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('JobApplication', backref='student', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='student', lazy=True, cascade='all, delete-orphan')
    summary = db.Column(db.Text, nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)
    portfolio_url = db.Column(db.String(500), nullable=True)
    address = db.Column(db.String(255), nullable=True)


class StudentProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    project_title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    github_link = db.Column(db.String(500))
    site_link = db.Column(db.String(500))
    youtube_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text, nullable=False)
    cgpa_required = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    contact_email = db.Column(db.String(120))
    contact_mobile = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('JobApplication', backref='job_posting', lazy=True, cascade='all, delete-orphan')


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    status = db.Column(db.String(20), default='Applied') 
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='application', lazy=True, cascade='all, delete-orphan')
    video_room_url = db.Column(db.String(500), nullable=True)


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('job_application.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_role = db.Column(db.String(20), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_role = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UniversityUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CollegeUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- NEW MODEL CLASS ---
class StudentProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    cgpa = db.Column(db.Float, default=0.0)
    skills_count = db.Column(db.Integer, default=0)
    projects_count = db.Column(db.Integer, default=0)
    certificates_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)

    student = db.relationship('Student', backref=db.backref('progress_logs', lazy=True))
# --- END NEW MODEL CLASS ---


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


BPUT_COLLEGES = [
    "Raajdhani Engineering College, Bhubaneswar",
    "College of Engineering and Technology, Bhubaneswar (CETB)",
    "Indira Gandhi Institute of Technology, Sarang (IGIT)",
    "Silicon Institute of Technology, Bhubaneswar",
    "Trident Academy of Technology, Bhubaneswar",
    "Gandhi Engineering College, Bhubaneswar (GEC)",
    "CV Raman Global University, Bhubaneswar",
    "Orissa Engineering College, Bhubaneswar (OEC)",
]

SKILL_RESOURCES = {
    'python': 'https://www.youtube.com/watch?v=rfscVS0vtbw',
    'flask': 'https://www.youtube.com/watch?v=oQ5UfJqW5Jo',
    'pandas': 'https://www.youtube.com/watch?v=EhYC02PD_gc',
    'numpy': 'https://www.youtube.com/watch?v=YqUcT-BFUM0',
    'machine learning': 'https://www.youtube.com/watch?v=SQkaBIP2JoA',
    'javascript': 'https://www.youtube.com/watch?v=FtaQSdrl7YA',
    'react': 'https://www.youtube.com/watch?v=lAFbKzO-fss',
    'html': 'https://www.youtube.com/watch?v=kUMe1FH4CHE',
    'css': 'https://www.youtube.com/watch?v=OEV8gHsKqL4',
    'sql': 'https://www.youtube.com/watch?v=NTgejLheGeU',
    'c++': 'https://www.youtube.com/watch?v=vLnPwxZdW4Y',
    'java': 'https://www.youtube.com/watch?v=A74TOX803D0'
}

INDIAN_IT_CITIES = [
    "Bangalore", "Hyderabad", "Pune", "Chennai", "Gurgaon", 
    "Noida", "Mumbai", "Kolkata", "Ahmedabad", "Bhubaneswar", "Kochi"
]


@app.template_filter('fromjson')
def fromjson_filter(value):
    """A template filter to parse a JSON string."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return [] 


def get_recommendations(student_id):
    student = Student.query.get(student_id)
    if not student:
        return []

    all_jobs = JobPosting.query.all()
    applied_job_ids = {app.job_id for app in student.applications}
    
    if not all_jobs:
        return []

    try:
        student_skills_list = json.loads(student.skills) if student.skills else []
    except (json.JSONDecodeError, TypeError):
        student_skills_list = []
    student_skills_set = {s.lower().strip() for s in student_skills_list}

    student_projects_text = ' '.join([p.description for p in student.projects if p.description])
    student_doc = f"{' '.join(student_skills_list)} {student_projects_text}"

    job_docs = []
    for job in all_jobs:
        skills = ' '.join(json.loads(job.required_skills) if job.required_skills else [])
        job_doc = f"{job.job_role} {job.description} {skills}"
        job_docs.append(job_doc)

    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        corpus = [student_doc] + job_docs
        tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        content_scores = cosine_sim[0]
    except ValueError:
        content_scores = [0] * len(all_jobs)

    recommendations = []
    num_projects = len(student.projects)

    for i, job in enumerate(all_jobs):
        if job.id not in applied_job_ids:
            content_score = content_scores[i] * 70
            cgpa_score = 0
            if student.cgpa and student.cgpa >= job.cgpa_required:
                cgpa_score = 10 
            project_score = min(num_projects * 10, 20)
            total_score = content_score + cgpa_score + project_score
            
            roadmap = []                                          # youtube    links    start
            try:
                job_skills_list = json.loads(job.required_skills) if job.required_skills else []
            except (json.JSONDecodeError, TypeError):
                job_skills_list = []
                
            job_skills_set = {s.lower().strip() for s in job_skills_list}
            missing_skills = list(job_skills_set - student_skills_set)
            
            for skill in missing_skills:
                resource_link = SKILL_RESOURCES.get(skill)
                if resource_link:
                    roadmap.append({
                        'skill': skill.capitalize(), 
                        'link': resource_link
                    })

            if total_score > 25:
                 recommendations.append({
                     'job': job, 
                     'score': round(total_score, 2),
                     'roadmap': roadmap  
                 })
                                                                    # youtube end here 
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:5]


def get_fit_score_for_application(student_id, job_id):
    student = Student.query.get(student_id)
    job = JobPosting.query.get(job_id)

    if not student or not job:
        return 0

    student_skills = ' '.join(json.loads(student.skills) if student.skills else [])
    student_projects_text = ' '.join([p.description for p in student.projects if p.description])
    student_doc = f"{student_skills} {student_projects_text}"

    job_skills = ' '.join(json.loads(job.required_skills) if job.required_skills else [])
    job_doc = f"{job.job_role} {job.description} {job_skills}"

    content_score_percentage = 0
    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        corpus = [student_doc, job_doc] 
        tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        content_score_percentage = cosine_sim[0][0]
    except ValueError:
        content_score_percentage = 0

    total_score = 0
    total_score += content_score_percentage * 100
    
    if student.cgpa and student.cgpa >= job.cgpa_required:
        total_score += 10
    
    num_projects = len(student.projects)
    total_score += min(num_projects * 10, 20)

    return round(total_score, 2)


# --- NEW HELPER FUNCTION ---
def log_student_progress(student_id):
    """Logs a snapshot of the student's current metrics."""
    student = Student.query.get(student_id)
    if not student:
        return

    try:
        skills_list = json.loads(student.skills) if student.skills else []
        skills_count = len(skills_list)
    except (json.JSONDecodeError, TypeError):
        skills_count = 0
    
    projects_count = StudentProject.query.filter_by(student_id=student_id).count()
    certificates_count = Certificate.query.filter_by(student_id=student_id).count()
    applications_count = JobApplication.query.filter_by(student_id=student_id).count()
    
    new_log = StudentProgress(
        student_id=student_id,
        cgpa=student.cgpa or 0.0,
        skills_count=skills_count,
        projects_count=projects_count,
        certificates_count=certificates_count,
        applications_count=applications_count
    )
    
    db.session.add(new_log)
    # Note: This function expects the caller to handle db.session.commit()
# --- END NEW HELPER FUNCTION ---


def calculate_placement_stats(students):
    total_students = len(students)
    if total_students == 0:
        return {'total': 0, 'placed': 0, 'rate': 0.0}

    placed_student_ids = db.session.query(JobApplication.student_id)\
        .filter(JobApplication.student_id.in_([s.id for s in students]))\
        .filter(JobApplication.status == 'Accepted')\
        .distinct().count()

    rate = (placed_student_ids / total_students) * 100
    return {'total': total_students, 'placed': placed_student_ids, 'rate': round(rate, 1)}

def calculate_profile_completion(student):
    """Calculates the student's profile completion percentage."""
   
    total_points = 8
    completed_points = 0

    if student.profile_photo:
        completed_points += 1
    if student.mobile:
        completed_points += 1
    if student.cgpa and student.cgpa > 0:
        completed_points += 1
    if student.summary:
        completed_points += 1
    if student.linkedin_url:
        completed_points += 1
    
    
    try:
        skills_list = json.loads(student.skills) if student.skills else []
        if skills_list:
            completed_points += 1
    except:
        pass
    
    
    if student.projects: 
        completed_points += 1
    if student.certificates: 
        completed_points += 1
    
    if total_points == 0:
        return 100
    
    percentage = (completed_points / total_points) * 100
    return int(percentage)

# ==================== ROUTES ====================

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')


@app.route('/chatbot_api', methods=['POST'])
def chatbot_api():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"reply": "Please type a message!"})

    if not GEMINI_MODEL:
        return jsonify({"reply": "Sorry, the chatbot is currently unavailable. Please try again later."})

    try:
        prompt = f"""You are ElevatR Assistant, a helpful placement chatbot for BPUT students. 
Be friendly, helpful, and concise.

User: {user_message}
Assistant:"""
        
        response = GEMINI_MODEL.generate_content(prompt)
        bot_reply = response.text.strip()
        
        return jsonify({"reply": bot_reply})
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"reply": "Sorry, I'm having trouble connecting. Please try again later."})


@app.route('/resources')
def resources():
    return render_template('resources.html')


# ==================== STUDENT ROUTES ====================

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        college = request.form['college']
        registration_number = request.form['registration_number']
        password = request.form['password']
      
        if Student.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('student_register'))
        
        if Student.query.filter_by(registration_number=registration_number).first():
            flash('Registration number already exists.', 'error')
            return redirect(url_for('student_register'))
            
        hashed_password = generate_password_hash(password)
        
        new_student = Student(
            full_name=full_name,
            email=email,
            college=college,
            registration_number=registration_number,
            password_hash=hashed_password,  
            skills=json.dumps([]) 
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        session['logged_in'] = True
        session['user_id'] = new_student.id
        session['role'] = 'student'
        session['full_name'] = new_student.full_name

        flash('Registration successful! Welcome to your profile.', 'success')
        return redirect(url_for('student_profile'))
    
    return render_template('student_register.html', colleges=BPUT_COLLEGES)


@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        student = Student.query.filter_by(email=email).first()
        
        if student and check_password_hash(student.password_hash, password):
            session['logged_in'] = True
            session['user_id'] = student.id
            session['role'] = 'student'
            session['full_name'] = student.full_name
            flash('Login successful!', 'success')
            return redirect(url_for('student_profile'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('student_login.html')


@app.route('/student_profile')
def student_profile():
    if session.get('role') != 'student':
        flash('Please log in to view this page.', 'error')
        return redirect(url_for('student_login'))
    
    student = Student.query.get(session['user_id'])
    projects = StudentProject.query.filter_by(student_id=student.id).all()
    
    try:
        student_skills = json.loads(student.skills) if student.skills else []
    except (json.JSONDecodeError, TypeError):
        student_skills = []

    recommendations = get_recommendations(student.id)
    certificates = Certificate.query.filter_by(student_id=student.id).order_by(Certificate.uploaded_at.desc()).all()
    
    completion_percentage = calculate_profile_completion(student)
    return render_template('student_profile.html', 
                           student=student, 
                           projects=projects, 
                           skills=student_skills, 
                           recommendations=recommendations,
                           certificates=certificates,
                           completion_percentage=completion_percentage)


@app.route('/student_edit_profile', methods=['GET', 'POST'])
def student_edit_profile():
    if session.get('role') != 'student':
        flash('Please log in to view this page.', 'error')
        return redirect(url_for('student_login'))
    
    student = Student.query.get(session['user_id'])
    
    # --- FIX 1: Handles the 'NoneType' object has no attribute 'id' error ---
    if not student:
        flash('Your profile could not be found. Please log in again.', 'error')
        session.clear() # Clear the invalid session
        return redirect(url_for('student_login'))
    
    if request.method == 'POST':
        student.full_name = request.form['full_name']
        student.email = request.form['email']
        student.mobile = request.form['mobile']
        
        # --- FIX 2: Handles the '400 Bad Request' (ValueError) for CGPA ---
        try:
            cgpa_input = request.form.get('cgpa')
            if cgpa_input:
                student.cgpa = float(cgpa_input)
            else:
                # If the field is empty, keep the existing CGPA or set to 0.0
                student.cgpa = student.cgpa or 0.0 
        except ValueError:
            # If conversion fails (e.g., "N/A"), flash an error and reload the page
            flash('Invalid input for CGPA. Please enter a number.', 'error')
            student_skills_str = ', '.join(json.loads(student.skills)) if student.skills else ""
            # Re-render the edit page with the data the user already typed in
            return render_template('student_edit_profile.html', student=student, skills=student_skills_str,
                                   summary=request.form.get('summary', ''),
                                   linkedin_url=request.form.get('linkedin_url', ''),
                                   portfolio_url=request.form.get('portfolio_url', ''),
                                   address=request.form.get('address', ''))
        
        skills_input = request.form.get('skills', '')
        skills_list = [s.strip() for s in skills_input.split(',') if s.strip()]
        student.skills = json.dumps(skills_list)
        student.summary = request.form.get('summary', '')
        student.linkedin_url = request.form.get('linkedin_url', '')
        student.portfolio_url = request.form.get('portfolio_url', '')
        student.address = request.form.get('address', '')

        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"student_{student.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                student.profile_photo = filename
        
        # --- ADDED CALL TO LOG PROGRESS ---
        log_student_progress(student.id)
        # --- END ADDED CALL ---
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))
    
    # This part runs for a GET request (when the page first loads)
    student_skills_str = ', '.join(json.loads(student.skills)) if student.skills else ""
    return render_template('student_edit_profile.html', student=student, skills=student_skills_str,
                           summary=student.summary or '',
                           linkedin_url=student.linkedin_url or '',
                           portfolio_url=student.portfolio_url or '',
                           address=student.address or '')


@app.route('/download_resume')
def download_resume():
    if session.get('role') != 'student':
        flash('Please log in to download your resume.', 'error')
        return redirect(url_for('student_login'))

    student_id = session['user_id']
    student = Student.query.get(student_id)
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('student_profile'))

    projects = StudentProject.query.filter_by(student_id=student.id).order_by(StudentProject.created_at.desc()).all()
    certificates = Certificate.query.filter_by(student_id=student.id).order_by(Certificate.uploaded_at.desc()).all()
    try:
        skills_list = json.loads(student.skills) if student.skills else []
    except (json.JSONDecodeError, TypeError):
        skills_list = []

    rendered_html = render_template(
        'resume_template.html',
        student=student,
        projects=projects,
        certificates=certificates,
        skills_list=skills_list,
    )

    pdf_bytes = BytesIO()
    pisa_status = pisa.CreatePDF(
        BytesIO(rendered_html.encode('UTF-8')),
        dest=pdf_bytes
    )

    if pisa_status.err:
        flash('Error generating PDF.', 'error')
        return redirect(url_for('student_profile'))

    pdf_bytes.seek(0)

    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{student.full_name.replace(" ", "_")}_Resume.pdf'
    )


@app.route('/add_project', methods=['POST'])
def add_project():
    if session.get('role') != 'student':
        return redirect(url_for('landing'))
    
    if request.method == 'POST':
        project = StudentProject(
            student_id=session['user_id'],
            project_title=request.form['project_title'],
            description=request.form['description'],
            github_link=request.form.get('github_link'),
            site_link=request.form.get('site_link'),
            youtube_link=request.form.get('youtube_link')
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')

    return redirect(url_for('student_edit_profile'))


@app.route('/add_certificate', methods=['POST'])
def add_certificate():
    if session.get('role') != 'student':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('landing'))

    student_id = session['user_id']
    title = request.form.get('title')
    file = request.files.get('certificate_image')

    if not title or not file or not file.filename:
        flash('Certificate title and image are required.', 'error')
        return redirect(url_for('student_edit_profile'))

    if not allowed_file(file.filename):
        flash('Invalid file type for certificate.', 'error')
        return redirect(url_for('student_edit_profile'))

    try:
        img = Image.open(file)
    except Exception as e:
        flash(f'Error processing image: {e}', 'error')
        return redirect(url_for('student_edit_profile'))

    prompt = """
    Analyze this certificate image.
    Extract all relevant technical skills and also non-technical skills even smaller smaller skills need to be extract  , programming languages, software, or tools mentioned.
    Do not extract soft skills.. ,and if the cirtificate look like resume then also extract skills from them also , 
    Return the skills as a single, flat JSON list of strings.
    even "outstanding gerdener" is a skill. remember this text .
    
    Example: ["Python", "Machine Learning", "TensorFlow", "Pandas", "Java"]
    
    If no  skills are found, return an empty list: []
    """

    newly_found_skills = []
    
    if not GEMINI_MODEL:
        flash('AI analysis model is not available.', 'error')
    else:
        try:
            response = GEMINI_MODEL.generate_content([prompt, img])
            
            clean_response = re.sub(r'```json\s*|\s*```', '', response.text.strip())
            
            newly_found_skills = json.loads(clean_response)
            
            if not isinstance(newly_found_skills, list):
                newly_found_skills = []
                
        except json.JSONDecodeError:
            print("Gemini response was not valid JSON.")
            flash('AI analyzed the certificate but could not extract skills in a valid format.', 'warning')
        except Exception as e:
            print(f"Gemini API Error: {e}")
            flash('Error during AI analysis of the certificate.', 'error')

    file.seek(0)
    filename = secure_filename(f"cert_{student_id}_{file.filename}")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_certificate = Certificate(
        student_id=student_id,
        title=title,
        filename=filename
    )
    db.session.add(new_certificate)

    student = Student.query.get(student_id)
    if student:
        try:
            current_skills_list = json.loads(student.skills) if student.skills else []
        except (json.JSONDecodeError, TypeError):
            current_skills_list = []
        
        current_skills_set = {s.lower().strip() for s in current_skills_list}
        new_skills_set = {s.lower().strip() for s in newly_found_skills}
        
        updated_skills_set = current_skills_set.union(new_skills_set)
        
        final_skills_list = sorted([s.title() for s in updated_skills_set])
        
        student.skills = json.dumps(final_skills_list)
        db.session.commit()
        
        new_skill_count = len(new_skills_set - current_skills_set)
        if new_skill_count > 0:
            flash(f'Certificate added and {new_skill_count} new skills were found and added to your profile!', 'success')
        else:
            flash('Certificate added successfully! No new skills were detected.', 'success')
            
    else:
        db.session.commit()
        flash('Certificate added, but could not find student profile to update skills.', 'error')

    return redirect(url_for('student_edit_profile'))


@app.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    if session.get('role') != 'student':
        return redirect(url_for('landing'))
    
    project = StudentProject.query.get_or_404(project_id)
    if project.student_id != session['user_id']:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('student_profile'))
    
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted!', 'success')
    return redirect(url_for('student_edit_profile'))


# --- NEW API ROUTE ---
@app.route('/api/student_progress')
def api_student_progress():
    if session.get('role') != 'student':
        return jsonify({"error": "Unauthorized"}), 401
    
    student_id = session['user_id']
    progress_logs = StudentProgress.query.filter_by(student_id=student_id).order_by(StudentProgress.timestamp.asc()).all()
    
    if not progress_logs:
        # If no logs, log one now
        log_student_progress(student_id)
        try:
            db.session.commit()
            progress_logs = StudentProgress.query.filter_by(student_id=student_id).order_by(StudentProgress.timestamp.asc()).all()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {e}"}), 500

    labels = [log.timestamp.strftime('%Y-%m-%d') for log in progress_logs]
    cgpa_data = [log.cgpa for log in progress_logs]
    skills_data = [log.skills_count for log in progress_logs]
    projects_data = [log.projects_count for log in progress_logs]
    certs_data = [log.certificates_count for log in progress_logs]
    apps_data = [log.applications_count for log in progress_logs]

    return jsonify({
        "labels": labels,
        "datasets": [
            {
                "label": "CGPA",
                "data": cgpa_data,
                "borderColor": "#34d399", # emerald
                "backgroundColor": "rgba(52, 211, 153, 0.1)",
                "fill": True,
                "yAxisID": "y",
            },
            {
                "label": "Skills",
                "data": skills_data,
                "borderColor": "#6366f1", # indigo
                "backgroundColor": "rgba(99, 102, 241, 0.1)",
                "fill": True,
                "yAxisID": "y1",
            },
            {
                "label": "Projects",
                "data": projects_data,
                "borderColor": "#f472b6", # pink
                "backgroundColor": "rgba(244, 114, 182, 0.1)",
                "fill": True,
                "yAxisID": "y1",
            },
            {
                "label": "Certificates",
                "data": certs_data,
                "borderColor": "#fbbf24", # amber
                "backgroundColor": "rgba(251, 191, 36, 0.1)",
                "fill": True,
                "yAxisID": "y1",
            },
            {
                "label": "Applications",
                "data": apps_data,
                "borderColor": "#06b6d4", # cyan
                "backgroundColor": "rgba(6, 182, 212, 0.1)",
                "fill": True,
                "yAxisID": "y1",
            }
        ]
    })
# --- END NEW API ROUTE ---


@app.route('/api/generate_improvement_plan', methods=['POST'])
def generate_improvement_plan():
    """Server-side endpoint to generate improvement plans using Gemini API"""
    if session.get('role') != 'student':
        return jsonify({"error": "Unauthorized"}), 401
    
    if not GEMINI_MODEL:
        return jsonify({"error": "AI model not available"}), 503
    
    try:
        data = request.get_json()
        job_role = data.get('jobRole', '')
        company = data.get('company', '')
        student_skills = data.get('studentSkills', [])
        job_skills = data.get('jobSkills', [])
        
        # Find missing skills - optimized for performance
        student_skills_lower = {skill.lower() for skill in student_skills}
        missing_skills = [skill for skill in job_skills 
                         if skill.lower() not in student_skills_lower]
        
        student_skills_str = ', '.join(student_skills) if student_skills else 'No skills listed'
        job_skills_str = ', '.join(job_skills) if job_skills else 'No specific skills listed'
        missing_skills_str = ', '.join(missing_skills) if missing_skills else 'None (Good match!)'
        
        prompt = f"""Generate a concise, actionable improvement plan for a student aiming for a '{job_role}' role at '{company}'.

Student's current skills: {student_skills_str}
Required skills for the job: {job_skills_str}
Identified skill gaps: {missing_skills_str}

Provide 3-5 specific, actionable steps focused on bridging the gaps. Include:
- Specific online courses (e.g., "Python for Data Science on Coursera")
- Project ideas (e.g., "Build a REST API using Flask")
- Certifications (e.g., "AWS Cloud Practitioner")
- Learning resources

Format as bullet points. Be brief and encouraging. Start directly with the plan."""
        
        response = GEMINI_MODEL.generate_content(prompt)
        
        # Safely extract text from response
        if not response or not hasattr(response, 'text'):
            return jsonify({"error": "Invalid response from AI model"}), 500
            
        text = response.text
        if not text:
            return jsonify({"error": "AI model returned empty response"}), 500
            
        text = text.strip()
        
        return jsonify({"success": True, "plan": text})
        
    except Exception as e:
        print(f"Error generating improvement plan: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/all_internship_opportunity')
def all_internship_opportunity():
    if session.get('role') != 'student':
        flash('Please log in to view internship opportunities.', 'error')
        return redirect(url_for('student_login'))

    student_id = session['user_id'] 
    selected_location = request.args.get('location')
    page_title = "Browse Job & Internship Opportunities"
    jobs_with_scores = [] 
    if selected_location:
        all_jobs_in_location = JobPosting.query.filter_by(location=selected_location).order_by(JobPosting.created_at.desc()).all()
        page_title = f"Jobs in {selected_location}"
        for job in all_jobs_in_location:
            fit_score = get_fit_score_for_application(student_id, job.id)
            jobs_with_scores.append({'job': job, 'score': fit_score})
        
        jobs_with_scores.sort(key=lambda x: x['score'], reverse=True)
    else:
        recommendations = get_recommendations(student_id)
        jobs_with_scores = recommendations
        page_title = "Jobs Recommended For You"

    student = Student.query.get(student_id)
    applied_job_ids = {app.job_id for app in student.applications}

    return render_template('all_internship_opportunity.html',
                           jobs_with_scores=jobs_with_scores, 
                           applied_job_ids=applied_job_ids,
                           cities=INDIAN_IT_CITIES,
                           selected_location=selected_location,
                           page_title=page_title)


@app.route('/apply_job/<int:job_id>')
def apply_job(job_id):
    if session.get('role') != 'student':
        return redirect(url_for('student_login'))
    
    existing_application = JobApplication.query.filter_by(
        student_id=session['user_id'], 
        job_id=job_id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(request.referrer or url_for('all_internship_opportunity'))

    application = JobApplication(student_id=session['user_id'], job_id=job_id)
    db.session.add(application)
    db.session.commit()
    
    job = JobPosting.query.get(job_id)
    student = Student.query.get(session['user_id'])
    
    
    create_notification(
        user_id=job.company_id,
        user_role='company',
        title='New Applicant!',
        message=f'{student.full_name} has applied for your {job.job_role} position.',
        link=url_for('applicants', job_id=job_id)
    )
    
    
    create_notification(
        user_id=session['user_id'],
        user_role='student',
        title='Application Submitted ✓',
        message=f'Your application for {job.job_role} at {job.company.company_name} has been submitted successfully.',
        link=url_for('my_applications')
    )
    
    flash('Application submitted successfully!', 'success')
    return redirect(request.referrer or url_for('all_internship_opportunity'))


@app.route('/my_applications')
def my_applications():
    if session.get('role') != 'student':
        flash('Please log in to view your applications.', 'error')
        return redirect(url_for('student_login'))

    student_id = session['user_id']
    applications = JobApplication.query.filter_by(student_id=student_id).order_by(JobApplication.applied_at.desc()).all()

    return render_template('my_applications.html', applications=applications)


# ==================== COMPANY ROUTES ====================

@app.route('/company_register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        mca_name = request.form['mca_registered_name'].strip()
        cin = request.form['cin_number'].strip().upper()
        gstin = request.form['gstin_number'].strip().upper()
        email = request.form['email'].strip().lower()
        mobile = request.form['mobile_number'].strip()
        linkedin = request.form['linkedin_profile'].strip()
        password = request.form['password']

        company_name = mca_name

        if Company.query.filter_by(email=email).first():
            flash('This email address is already registered.', 'error')
            return redirect(url_for('company_register'))
        if Company.query.filter_by(cin_number=cin).first():
            flash('This CIN is already registered.', 'error')
            return redirect(url_for('company_register'))
        if Company.query.filter_by(gstin_number=gstin).first():
             flash('This GSTIN is already registered.', 'error')
             return redirect(url_for('company_register'))

        hashed_password = generate_password_hash(password)
        new_company = Company(
            company_name=company_name,
            mca_registered_name=mca_name,
            cin_number=cin,
            gstin_number=gstin,
            email=email,
            mobile_number=mobile,
            linkedin_profile=linkedin,
            password_hash=hashed_password,
            status='pending'
        )
        try:
            db.session.add(new_company)
            db.session.commit()
            flash('Registration submitted! Your company details are pending verification by BPUT.', 'info')
            return redirect(url_for('company_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration. Please try again. Error: {e}', 'error')
            return redirect(url_for('company_register'))

    return render_template('company_register.html')


@app.route('/company_login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        company = Company.query.filter_by(email=email).first()

        if company and check_password_hash(company.password_hash, password):
            if company.status == 'approved':
                session['logged_in'] = True
                session['user_id'] = company.id
                session['role'] = 'company'
                session['company_name'] = company.mca_registered_name or company.company_name
                flash('Login successful!', 'success')
                return redirect(url_for('company_profile'))
            elif company.status == 'pending':
                flash('Your company registration is pending verification. Please contact BPUT at *****99 for assistance.', 'warning')
                return redirect(url_for('company_login'))
            elif company.status == 'rejected':
                flash('Your company registration was not approved. Please contact BPUT for details.', 'error')
                return redirect(url_for('company_login'))
            else:
                flash('Your account has an unknown status. Please contact BPUT.', 'error')
                return redirect(url_for('company_login'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('company_login.html')


@app.route('/company_profile')
def company_profile():
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))
    
    company = Company.query.get(session['user_id'])
    jobs = JobPosting.query.filter_by(company_id=company.id).order_by(JobPosting.created_at.desc()).all()
    
    return render_template('company_profile.html', company=company, jobs=jobs)


@app.route('/company_edit_profile', methods=['GET', 'POST'])
def company_edit_profile():
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))
        
    company = Company.query.get(session['user_id'])
    
    if request.method == 'POST':
        company.description = request.form.get('description', '')
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"company_{company.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                company.logo = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('company_profile'))

    return render_template('company_edit_profile.html', company=company)


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))
        
    if request.method == 'POST':
        skills_input = request.form['required_skills']
        skills_list = [s.strip() for s in skills_input.split(',') if s.strip()]
        
        job = JobPosting(
            company_id=session['user_id'],
            job_role=request.form['job_role'],
            description=request.form.get('description', ''),
            required_skills=json.dumps(skills_list),
            cgpa_required=float(request.form['cgpa_required']),
            location=request.form['location'],
            salary_min=float(request.form.get('salary_min', 0) or 0),
            salary_max=float(request.form.get('salary_max', 0) or 0),
            contact_email=request.form.get('contact_email'),
            contact_mobile=request.form.get('contact_mobile')
        )
        
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company_profile'))

    return render_template('post_job.html', cities=INDIAN_IT_CITIES)


@app.route('/applicants/<int:job_id>')
def applicants(job_id):
    if session.get('role') != 'company':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('company_login'))

    job = JobPosting.query.get_or_404(job_id)
    if job.company_id != session['user_id']:
        flash('You are not authorized to view applicants for this job.', 'error')
        return redirect(url_for('company_dashboard'))

    applications = JobApplication.query.filter_by(job_id=job_id).order_by(JobApplication.applied_at.asc()).all()

    applications_with_scores = []
    for app in applications:
        fit_score = get_fit_score_for_application(app.student_id, job_id)
        applications_with_scores.append({
            'application': app,
            'fit_score': fit_score
        })

    return render_template('applicants.html', job=job, applications_with_scores=applications_with_scores)


@app.route('/update_application_status/<int:application_id>', methods=['POST'])
def update_application_status(application_id):
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))

    application = JobApplication.query.get_or_404(application_id)
    job = JobPosting.query.get(application.job_id)

    if not job or job.company_id != session['user_id']:
        return redirect(url_for('company_profile'))

    new_status = request.form.get('status')
    if new_status == 'Accepted':
        application.status = 'Accepted'

        if not application.video_room_url:
            headers = {
                "Authorization": f"Bearer {WHEREBY_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "endDate": "2099-02-18T14:23:00.000Z",
                "fields": ["hostRoomUrl"],
            }
            response = requests.post("https://api.whereby.dev/v1/meetings", headers=headers, json=payload)

            if response.status_code == 201:
                data = response.json()
                application.video_room_url = data.get('roomUrl')
                flash('Applicant accepted and a video call room has been created.', 'success')
            else:
                flash('Applicant accepted, but failed to create a video room.', 'error')
        
        # NEW: Send notification to student
        create_notification(
            user_id=application.student_id,
            user_role='student',
            title='Application Accepted! 🎉',
            message=f'Congratulations! Your application for {job.job_role} at {job.company.company_name} has been accepted.',
            link=url_for('conversation', application_id=application.id)
        )

    elif new_status == 'Rejected':
        application.status = 'Rejected'
        flash('Applicant has been rejected.', 'success')
        
        # NEW: Send notification to student
        create_notification(
            user_id=application.student_id,
            user_role='student',
            title='Application Update',
            message=f'Your application for {job.job_role} at {job.company.company_name} was not selected this time. Keep applying!',
            link=url_for('my_applications')
        )

    else:
        flash('Invalid status update.', 'error')

    db.session.commit()
    return redirect(url_for('applicants', job_id=job.id))


@app.route('/view_applicant/<int:student_id>')
def view_applicant(student_id):
    allowed_roles = {'company', 'college', 'university'}
    if session.get('role') not in allowed_roles:
        flash('You are not authorized to view this profile.', 'error')
        return redirect(url_for('landing')) 
    
    student = Student.query.get_or_404(student_id)
    projects = StudentProject.query.filter_by(student_id=student.id).all()
    student_skills = json.loads(student.skills) if student.skills else []
    certificates = Certificate.query.filter_by(student_id=student.id).order_by(Certificate.uploaded_at.desc()).all()

    return render_template('view_applicant.html', student=student, projects=projects, skills=student_skills, certificates=certificates)


# ==================== CONVERSATION/MESSAGING ROUTES ====================

@app.route('/conversation/<int:application_id>', methods=['GET', 'POST'])
def conversation(application_id):
    if not session.get('logged_in'):
        return redirect(url_for('landing'))

    application = JobApplication.query.get_or_404(application_id)

    is_student_applicant = (session.get('role') == 'student' and application.student_id == session.get('user_id'))
    is_company_owner = (session.get('role') == 'company' and application.job_posting.company_id == session.get('user_id'))

    if not (is_student_applicant or is_company_owner):
        flash('You are not authorized to view this conversation.', 'error')
        return redirect(url_for('landing'))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_message = Message(
                application_id=application_id,
                sender_id=session['user_id'],
                sender_role=session['role'],
                content=content
            )
            db.session.add(new_message)
            db.session.commit()
            
            # NEW: Notify the other party
            if session['role'] == 'student':
                create_notification(
                    user_id=application.job_posting.company_id,
                    user_role='company',
                    title='New Message',
                    message=f'{application.student.full_name} sent you a message about {application.job_posting.job_role}.',
                    link=url_for('conversation', application_id=application_id)
                )
            else:
                create_notification(
                    user_id=application.student_id,
                    user_role='student',
                    title='New Message',
                    message=f'{application.job_posting.company.company_name} sent you a message.',
                    link=url_for('conversation', application_id=application_id)
                )
        
        return redirect(url_for('conversation', application_id=application_id))

    messages = Message.query.filter_by(application_id=application_id).order_by(Message.timestamp.asc()).all()

    if session['role'] == 'student':
        other_party_name = application.job_posting.company.company_name
    else: 
        other_party_name = application.student.full_name

    return render_template('conversation.html', 
                           application=application, 
                           messages=messages, 
                           other_party_name=other_party_name)


# ==================== UNIVERSITY ROUTES ====================

@app.route('/university_register', methods=['GET', 'POST'])
def university_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']

        if UniversityUser.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('university_register'))

        hashed_password = generate_password_hash(password)
        new_user = UniversityUser(
            username=username, email=email, role=role, password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('university_login'))
    
    return render_template('university_register.html')


@app.route('/university_login', methods=['GET', 'POST'])
def university_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = UniversityUser.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['role'] = 'university'
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('university_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('university_login.html')


@app.route('/university_dashboard')
def university_dashboard():
    if session.get('role') != 'university':
        flash('Please log in to access the university dashboard.', 'error')
        return redirect(url_for('university_login'))

    college_stats = []
    
    fake_company_participation = [random.randint(5, 15) for _ in BPUT_COLLEGES]
    fake_avg_package = [round(random.uniform(4.5, 8.5), 1) for _ in BPUT_COLLEGES]

    for i, college in enumerate(BPUT_COLLEGES):
        students = Student.query.filter_by(college=college).all()
        stats = calculate_placement_stats(students)

        college_stats.append({
            'name': college,
            'total_students': stats['total'],
            'placed_students': stats['placed'],
            'companies_participated': fake_company_participation[i],
            'avg_package': fake_avg_package[i]
        })

    overall_placed = sum(cs['placed_students'] for cs in college_stats)
    overall_total = sum(cs['total_students'] for cs in college_stats)
    overall_rate = (overall_placed / overall_total * 100) if overall_total > 0 else 0

    return render_template('university_dashboard.html',
                           college_stats=college_stats,
                           overall_rate=round(overall_rate, 1))


@app.route('/university_dashboard/<college_name>')
def college_placement_details(college_name):
    if session.get('role') != 'university':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('university_login'))

    if college_name not in BPUT_COLLEGES:
        flash('Invalid college specified.', 'error')
        return redirect(url_for('university_dashboard'))

    students = Student.query.filter_by(college=college_name).order_by(Student.full_name).all()

    student_placement_data = []
    for student in students:
        accepted_app = JobApplication.query\
            .join(JobPosting, JobApplication.job_id == JobPosting.id)\
            .join(Company, JobPosting.company_id == Company.id)\
            .filter(JobApplication.student_id == student.id)\
            .filter(JobApplication.status == 'Accepted')\
            .add_columns(Company.company_name)\
            .first()

        student_placement_data.append({
            'info': student,
            'is_placed': bool(accepted_app),
            'company_name': accepted_app.company_name if accepted_app else None
        })

    return render_template('college_placement_details.html',
                           college_name=college_name,
                           student_data=student_placement_data)


@app.route('/university/verify_companies')
def verify_companies():
    if session.get('role') != 'university':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('university_login'))

    try:
        pending_companies = Company.query.filter_by(status='pending').order_by(Company.created_at.asc()).all()
    except Exception as e:
        flash(f"Error fetching pending companies: {e}", "error")
        pending_companies = []

    return render_template('verify_company.html', companies=pending_companies)


@app.route('/university/approve_deny_company/<int:company_id>', methods=['POST'])
def approve_deny_company(company_id):
    if session.get('role') != 'university' or request.method != 'POST':
        flash('Unauthorized action.', 'error')
        return redirect(url_for('university_login' if 'user_id' not in session else 'university_dashboard'))

    company = Company.query.get_or_404(company_id)
    action = request.form.get('action')

    if company.status != 'pending':
         flash(f'Company "{company.company_name}" is no longer pending verification.', 'info')
         return redirect(url_for('verify_companies'))

    if action == 'approve':
        company.status = 'approved'
        flash(f'Company "{company.mca_registered_name or company.company_name}" approved successfully.', 'success')
        
        # NEW: Notify company of approval
        create_notification(
            user_id=company.id,
            user_role='company',
            title='Company Verified! ✓',
            message=f'Congratulations! Your company "{company.mca_registered_name}" has been verified by BPUT. You can now post jobs.',
            link=url_for('company_profile')
        )
        
    elif action == 'reject':
        company.status = 'rejected'
        flash(f'Company "{company.mca_registered_name or company.company_name}" rejected.', 'warning')
        
        # NEW: Notify company of rejection
        create_notification(
            user_id=company.id,
            user_role='company',
            title='Verification Status',
            message=f'Your company registration for "{company.mca_registered_name}" could not be verified. Please contact BPUT for details.',
            link=None
        )
    else:
        flash('Invalid action specified.', 'error')

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Database error: {e}", "error")

    return redirect(url_for('verify_companies'))


# ==================== COLLEGE ROUTES ====================

@app.route('/college_register', methods=['GET', 'POST'])
def college_register():
    if request.method == 'POST':
        college_name = request.form['college_name']
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']

        if CollegeUser.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('college_register'))

        hashed_password = generate_password_hash(password)
        new_user = CollegeUser(
            college_name=college_name, username=username, email=email, role=role, password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('college_login'))
        
    return render_template('college_register.html', colleges=BPUT_COLLEGES)


@app.route('/college_login', methods=['GET', 'POST'])
def college_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = CollegeUser.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['role'] = 'college'
            session['username'] = user.username
            session['college_name'] = user.college_name
            flash('Login successful!', 'success')
            return redirect(url_for('college_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('college_login.html')


@app.route('/college_dashboard')
def college_dashboard():
    if session.get('role') != 'college':
        flash('Please log in to access the college dashboard.', 'error')
        return redirect(url_for('college_login'))
    
    college_name = session['college_name']
    students = Student.query.filter_by(college=college_name).order_by(Student.full_name).all()
    student_data = []
    
    for student in students:
        applications = JobApplication.query.filter_by(student_id=student.id).all()
        placement_status = "N/A" 
        placed_company = None
        has_applied = False
        has_rejected = False

        if applications:
             has_applied = True 
             accepted_app = next((app for app in applications if app.status == 'Accepted'), None)
             if accepted_app:
                 placement_status = 'Accepted'
                 job_posting = JobPosting.query.get(accepted_app.job_id)
                 if job_posting and job_posting.company: 
                     placed_company = job_posting.company.company_name
             else:
                 if any(app.status == 'Rejected' for app in applications):
                      placement_status = 'Rejected'
                 else:
                      placement_status = 'Applied' 

        student_data.append({
            'info': student,
            'application_count': len(applications),
            'placement_status': placement_status,
            'placed_company': placed_company
        })

    return render_template('college_dashboard.html',
                           student_data=student_data,
                           college_name=college_name)


# ==================== NOTIFICATION API ENDPOINTS ====================

def create_notification(user_id, user_role, title, message, link=None):
    
    try:
        notification = Notification(
            user_id=user_id,
            user_role=user_role,
            title=title,
            message=message,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error creating notification: {e}")
        db.session.rollback()
        return False

@app.route('/api/get_notifications')
def get_notifications():
    """Fetch unread notifications for the current user."""
    if not session.get('logged_in'):
        return jsonify({'notifications': [], 'count': 0})
    
    user_id = session['user_id']
    user_role = session['role']
    
    notifications = Notification.query.filter_by(
        user_id=user_id,
        user_role=user_role,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    notification_list = []
    for notif in notifications:
        notification_list.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'link': notif.link,
            'created_at': notif.created_at.strftime('%b %d, %I:%M %p')
        })
    
    return jsonify({
        'notifications': notification_list,
        'count': len(notification_list)
    })


@app.route('/api/mark_notification_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a single notification as read."""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != session['user_id'] or notification.user_role != session['role']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/mark_all_notifications_read', methods=['POST'])
def mark_all_notifications_read():
    """Mark all notifications as read for the current user."""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    Notification.query.filter_by(
        user_id=session['user_id'],
        user_role=session['role'],
        is_read=False
    ).update({'is_read': True})
    
    db.session.commit()
    
    return jsonify({'success': True})

# --- ROUTES THAT WERE MISSING FROM update/app.py ---
@app.route('/tech_feed')
def tech_feed():
    return render_template('tech_feed.html')

@app.route('/api/fetch_tech-news')
def fetch_tech_news():
    news_items = []
    
    try:
        response = requests.get('https://dev.to/api/articles?tag=technology&per_page=20', timeout=5)
        if response.status_code == 200:
            articles = response.json()
            for article in articles:
                news_items.append({
                    'id': f"devto-{article['id']}",
                    'title': article['title'],
                    'summary': article.get('description', 'Click to read more about this tech topic.'),
                    'url': article['url'],
                    'publishDate': article['published_at'],
                    'category': 'tech',
                    'source': 'Dev.to'
                })
        
        # Try to fetch React articles too
        try:
            react_response = requests.get('https://dev.to/api/articles?tag=react&per_page=10', timeout=5)
            if react_response.status_code == 200:
                react_articles = react_response.json()
                for article in react_articles:
                    news_items.append({
                        'id': f"react-{article['id']}",
                        'title': article['title'],
                        'summary': article.get('description', 'Explore this React development topic.'),
                        'url': article['url'],
                        'publishDate': article['published_at'],
                        'category': 'tech',
                        'source': 'Dev.to'
                    })
        except:
            pass
            
    except Exception as e:
        print(f"Error fetching news: {e}")
    
    return jsonify({'success': True, 'articles': news_items})
# --- END MISSING ROUTES ---


# ==================== GENERAL ROUTES ====================

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('landing'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    with app.app_context():
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
    
    app.run(host='0.0.0.0', port=5000, debug=True)