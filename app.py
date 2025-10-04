from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Course, Lesson, Enrollment, Certificate, CreatorApplication
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import hashlib

# ---------------------
# Initialize Flask App
# ---------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///microcourses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev-secret'

db.init_app(app)

# ---------------------
# Routes
# ---------------------

# Home / Courses
@app.route('/')
def index():
    courses = Course.query.filter_by(published=True).all()
    return render_template('index.html', courses=courses)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and pbkdf2_sha256.verify(password, user.password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('index'))
        return "Invalid credentials"
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Course Details
@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    return render_template('course_detail.html', course=course, lessons=lessons)

# Enroll in Course
@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if not enrollment:
        enrollment = Enrollment(user_id=user_id, course_id=course_id, progress=0, completed_lessons='')
        db.session.add(enrollment)
        db.session.commit()
    return redirect(url_for('course_detail', course_id=course_id))

# Learn Lesson
@app.route('/learn/<int:lesson_id>')
def learn(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    return render_template('learn.html', lesson=lesson)

# Complete Lesson & Update Progress
@app.route('/complete/<int:lesson_id>')
def complete_lesson(lesson_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    lesson = Lesson.query.get(lesson_id)
    enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=lesson.course_id).first()
    completed = enrollment.completed_lessons.split(',') if enrollment.completed_lessons else []

    if str(lesson.id) not in completed:
        completed.append(str(lesson.id))
        enrollment.completed_lessons = ','.join(completed)
        enrollment.progress = int(len(completed)/Lesson.query.filter_by(course_id=lesson.course_id).count()*100)
        db.session.commit()

        if enrollment.progress == 100:
            serial = hashlib.sha256(f'{user_id}-{lesson.course_id}-{datetime.utcnow()}'.encode()).hexdigest()[:10]
            cert = Certificate(user_id=user_id, course_id=lesson.course_id, serial=serial)
            db.session.add(cert)
            db.session.commit()

    return redirect(url_for('learn', lesson_id=lesson_id))

# Progress & Certificates
@app.route('/progress')
def progress():
    user_id = session.get('user_id')
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    return render_template('progress.html', enrollments=enrollments)

# Jinja helper for certificates
@app.context_processor
def utility_processor():
    def certificate_for_course(user_id, course_id):
        return Certificate.query.filter_by(user_id=user_id, course_id=course_id).first()
    return dict(certificate_for_course=certificate_for_course)

# ---------------------
# Creator & Admin
# ---------------------
@app.route('/creator/apply', methods=['GET', 'POST'])
def creator_apply():
    if request.method == 'POST':
        bio = request.form['bio']
        user_id = session.get('user_id')
        app_obj = CreatorApplication(user_id=user_id, bio=bio)
        db.session.add(app_obj)
        db.session.commit()
        return "Application submitted"
    return render_template('creator_apply.html')

@app.route('/creator/dashboard')
def creator_dashboard():
    user_id = session.get('user_id')
    courses = Course.query.filter_by(creator_id=user_id).all()
    return render_template('creator_dashboard.html', courses=courses)

@app.route('/admin/review/courses')
def admin_review():
    apps = CreatorApplication.query.filter_by(status='pending').all()
    return render_template('admin_review.html', apps=apps)

# ---------------------
# Run App
# ---------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)
