import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from forms import LoginForm, ProfileForm, RegisterForm
from models import Student, User, db


HOME_NAME = "Quirsten Heidee G. Dela Rea"
HOME_SECTION = "BSECE-1B"
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


app = Flask(__name__, instance_relative_config=True)
database_path = os.path.join(app.instance_path, "app.db").replace("\\", "/")
app.config["SECRET_KEY"] = "my-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def build_display_name(email):
    local_part = email.split("@", 1)[0]
    return local_part.replace(".", " ").replace("_", " ").title()


def allowed_file(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def migrate_user_table():
    columns = {
        row["name"]
        for row in db.session.execute(text("PRAGMA table_info(users)")).mappings().all()
    }

    if "role" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'viewer'"
            )
        )
    if "display_name" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(120)"))
    if "image_filename" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN image_filename VARCHAR(255)"))
    db.session.commit()


def backfill_existing_users():
    updated = False
    for user in User.query.all():
        if not user.role:
            user.role = "viewer"
            updated = True
        if not user.display_name:
            user.display_name = build_display_name(user.email)
            updated = True
    if updated:
        db.session.commit()


def seed_demo_data():
    demo_users = [
        {
            "email": "admin@tup.edu.ph",
            "password": "admin123",
            "role": "admin",
            "display_name": "Admin User",
        },
        {
            "email": "viewer@tup.edu.ph",
            "password": "viewer123",
            "role": "viewer",
            "display_name": "Viewer User",
        },
    ]

    for item in demo_users:
        user = User.query.filter_by(email=item["email"]).first()
        if user is None:
            user = User(
                email=item["email"],
                password=generate_password_hash(item["password"]),
                role=item["role"],
                display_name=item["display_name"],
            )
            db.session.add(user)

    if Student.query.count() == 0:
        db.session.add_all(
            [
                Student(full_name="Ana Cruz", email="ana.cruz@example.com"),
                Student(full_name="Maria Santos", email="maria.santos@example.com"),
                Student(full_name="Zed Torres", email="zed.torres@example.com"),
            ]
        )

    db.session.commit()


@app.errorhandler(413)
def file_too_large(_error):
    flash("Profile image is too large. Please upload a smaller file.")
    return redirect(url_for("dashboard"))


@app.route("/")
def home():
    return render_template("home.html", name=HOME_NAME, section=HOME_SECTION)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("That email is already registered.")
            return render_template("register.html", form=form)

        user = User(
            email=email,
            password=generate_password_hash(form.password.data),
            role=form.role.data,
            display_name=form.display_name.data.strip(),
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    form = ProfileForm(display_name=current_user.display_name)
    return render_template("dashboard.html", user=current_user, form=form)


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    form = ProfileForm()
    user = db.session.get(User, current_user.id)

    if user is None:
        flash("Profile not found.")
        return redirect(url_for("dashboard"))

    if not form.validate_on_submit():
        for errors in form.errors.values():
            for error in errors:
                flash(error)
        return redirect(url_for("dashboard"))

    user.display_name = form.display_name.data.strip()

    uploaded_file = form.profile_image.data
    if uploaded_file and uploaded_file.filename:
        if not allowed_file(uploaded_file.filename):
            flash("Only JPG, JPEG, and PNG files are allowed.")
            return redirect(url_for("dashboard"))

        if uploaded_file.mimetype not in ALLOWED_MIME_TYPES:
            flash("Only JPEG and PNG image MIME types are allowed.")
            return redirect(url_for("dashboard"))

        safe_name = secure_filename(uploaded_file.filename)
        extension = Path(safe_name).suffix.lower()
        filename = f"user_{user.id}_{uuid4().hex}{extension}"
        save_path = Path(app.config["UPLOAD_FOLDER"]) / filename
        uploaded_file.save(save_path)
        user.image_filename = filename

    db.session.commit()
    flash("Profile updated successfully.")
    return redirect(url_for("dashboard"))


@app.route("/students")
@login_required
def students():
    student_list = Student.query.order_by(Student.full_name.asc()).all()
    return render_template("students.html", students=student_list)


@app.route("/add-student", methods=["POST"])
@login_required
def add_student():
    if current_user.role != "admin":
        flash("Only admin users can add student records.")
        return redirect(url_for("students"))

    full_name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not full_name or not email:
        flash("Both student name and email are required.")
        return redirect(url_for("students"))

    existing_student = Student.query.filter_by(email=email).first()
    if existing_student:
        flash("That student email already exists.")
        return redirect(url_for("students"))

    student = Student(full_name=full_name, email=email)
    db.session.add(student)
    db.session.commit()
    flash("Student added successfully.")
    return redirect(url_for("students"))


@app.route("/delete-student/<int:id>")
@login_required
def delete_student(id):
    if current_user.role != "admin":
        flash("Only admin users can delete student records.")
        return redirect(url_for("students"))

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully.")
    return redirect(url_for("students"))


def setup_database():
    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        db.create_all()
        migrate_user_table()
        backfill_existing_users()
        seed_demo_data()


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
