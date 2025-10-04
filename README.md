MicroCourses LMS – Architecture Notes
1. Overview

A mini Learning Management System where:

Creators upload courses & lessons

Admins review and approve courses

Learners enroll, track progress, complete lessons, and receive certificates

2. Technology Stack
Layer	Technology
Backend	Python, Flask
Database	SQLite (SQLAlchemy ORM)
Frontend	HTML, Jinja2 templates, TailwindCSS
Authentication	Session-based login, hashed passwords (Passlib)
Deployment	Local / VS Code (can extend to Heroku, Render, etc.)
3. Components

Models (Database)

User → Learner, Creator, Admin

Course → title, description, creator, published flag

Lesson → course_id, title, content, transcript, order

Enrollment → tracks user progress & completed lessons

Certificate → serial hash issued when course completed

CreatorApplication → stores creator apply requests

Routes / APIs

Auth → /login, /logout

Learner → /, /courses/<id>, /learn/<lessonId>, /enroll/<courseId>, /complete/<lessonId>, /progress

Creator → /creator/apply, /creator/dashboard

Admin → /admin/review/courses

Templates

Base layout: base.html

Learner: index.html, course_detail.html, learn.html, progress.html

Creator: creator_apply.html, creator_dashboard.html

Admin: admin_review.html

4. Data Flow

Creator applies → Admin approves → Course published

Learner enrolls → Completes lessons → Progress tracked

Progress = 100% → Certificate issued with unique serial hash

5. Key Features

Role-based access control

Lesson order uniqueness

Auto-generated transcripts per lesson

Idempotent course enrollment

Certificate issuance & tracking

Session-based authentication
