from app import app, db
from models import User, Course, Lesson
from passlib.hash import pbkdf2_sha256

with app.app_context():
    db.create_all()

    # Create Users
    if not User.query.filter_by(email='admin@example.com').first():
        db.session.add(User(email='admin@example.com',
                            password=pbkdf2_sha256.hash('pass123'),
                            role='admin'))
    if not User.query.filter_by(email='creator@example.com').first():
        db.session.add(User(email='creator@example.com',
                            password=pbkdf2_sha256.hash('pass123'),
                            role='creator'))
    if not User.query.filter_by(email='learner@example.com').first():
        db.session.add(User(email='learner@example.com',
                            password=pbkdf2_sha256.hash('pass123'),
                            role='learner'))
    db.session.commit()

    # Sample Course & Lessons
    if not Course.query.filter_by(title='Sample Course').first():
        course = Course(title='Sample Course',
                        description='Demo course for testing.',
                        creator_id=2,  # Assuming creator user ID
                        published=True)
        db.session.add(course)
        db.session.commit()

        db.session.add(Lesson(course_id=course.id,
                              title='Introduction',
                              content='Welcome to the Sample Course!',
                              transcript='Transcript 1',
                              order=1))
        db.session.add(Lesson(course_id=course.id,
                              title='Conclusion',
                              content='Congrats on completing the course!',
                              transcript='Transcript 2',
                              order=2))
        db.session.commit()

    print("Database seeded successfully.")
