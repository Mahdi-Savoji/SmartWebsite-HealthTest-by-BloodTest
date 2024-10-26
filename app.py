from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy 
from forms import UserForm, LoginForm 
from captcha.image import ImageCaptcha
from ML.model import predict_diabetes 
import os
import random
import string
from datetime import datetime

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config["SECRET_KEY"] = os.urandom(12)

# Configure SQLite Database with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# User Model for SQLAlchemy
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    result = db.relationship("userResult", backref='author', lazy=True)

    def __init__(self, fullname, username, email, password):
        self.fullname = fullname
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)  # Hash the password


class userResult(db.Model):
    __tablename__ = "user_result"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    chol = db.Column(db.Float, nullable=False)
    tg = db.Column(db.Float, nullable=False)
    hdl = db.Column(db.Float, nullable=False)
    ldl = db.Column(db.Float, nullable=False)
    cr = db.Column(db.Float, nullable=False)
    bun = db.Column(db.Float, nullable=False)

    result = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, gender, age, bmi, chol, tg, hdl, ldl, cr, bun, result, user_id):
        self.gender = gender
        self.age = age
        self.bmi = bmi
        self.chol = chol
        self.tg = tg
        self.hdl = hdl
        self.ldl = ldl
        self.cr = cr
        self.bun = bun
        self.result = result
        self.user_id = user_id


# Create the database tables
with app.app_context():
    db.create_all()


# Generate random CAPTCHA text
def generate_random_captcha(length=6):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


# Routes
@app.route("/")
def home():
    user = None
    if "user_id" in session:
        user = User.query.get(session["user_id"])
    return render_template("index.html", user=user)

@app.route("/")
def our_team():
    return render_template("our-team.html")


image = ImageCaptcha(width=260, height=80)

@app.route("/captcha")
def captcha():
    captcha_text = generate_random_captcha()
    session['captcha'] = captcha_text
    image_file = os.path.join('static', 'img', 'CAPTCHA.png')
    image.write(captcha_text, image_file)

    return app.send_static_file('img/CAPTCHA.png')

@app.route("/register", methods=["GET", "POST"])
def register():
    form = UserForm()
    print("111111111111111111111111111111111111111")
    if UserForm().validate_on_submit():
        print("0000000000000000000000000000000")
        if form.captcha.data != session.get('captcha'):
            flash("Invalid CAPTCHA. Please try again.", "danger")
            session.pop('captcha', None)
            return redirect(url_for("register"))

        fullname = form.fullname.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash("Username already taken, please choose a different one.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered, please use a different one.", "danger")
            return redirect(url_for("register"))

        new_user = User(fullname=fullname, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Successfully registered! Please log in.", "success")
        return redirect(url_for("login"))

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.captcha.data != session.get('captcha'):
            flash("Invalid CAPTCHA. Please try again.", "danger")
            session.pop('captcha', None)
            return redirect(url_for("login"))  

        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Please log in to view this page", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)


@app.route("/input", methods=["GET", "POST"])
def input():
    if "user_id" not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))
    current_user = User.query.filter_by(username=session["username"]).first()
    if request.method == "POST":
        gender = request.form["gender"]
        age = int(request.form["age"])
        bmi = float(request.form["bmi"])
        chol = float(request.form["chol"])
        tg = float(request.form["tg"])
        hdl = float(request.form["hdl"])
        ldl = float(request.form["ldl"])
        cr = float(request.form["cr"])
        bun = float(request.form["bun"])
    
    Inputs = [[gender,age,bmi,chol,tg,hdl,ldl,cr,bun]]
    
    predict = predict_diabetes(Inputs)
    # save to database
    new =  userResult(gender, age, bmi, chol, tg, hdl,ldl, cr, bun, predict, current_user.id)
    db.session.add(new)
    db.session.commit()

    return render_template("input.html")


@app.route("/result")
def result():
    if "user_id" not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))
    current_user = User.query.filter_by(username=session["username"]).first()
    prediction = (
        db.session.query(userResult.result).filter_by(id=current_user.id).first()[0]
    )

    return render_template("result.html", prediction = prediction)

# history page
@app.route("/history")
#@login_required
def history():
    current_user = User.query.filter_by(username=session["username"]).first()

    predictions = userResult.query.filter_by(user_id=current_user.id).all()

    return render_template("history.html", predictions=predictions)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
