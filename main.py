from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# LOGIN
login_manager = LoginManager(app)
login_manager.login_view = "login"

# EMAIL CONFIG (CHANGE THIS)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your@email.com'
app.config['MAIL_PASSWORD'] = 'yourpassword'
mail = Mail(app)

# UPLOADS
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MODELS
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    image = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ROUTES

@app.route("/")
def home():
    projects = Project.query.all()
    return render_template("index.html", projects=projects)

@app.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        msg = Message(
            subject="New Message",
            sender=request.form["email"],
            recipients=["your@email.com"]
        )
        msg.body = request.form["message"]
        mail.send(msg)
        flash("Message sent!")

    return render_template("contact.html")

# LOGIN

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    if request.method == "POST":
        file = request.files["image"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        project = Project(
            title=request.form["title"],
            description=request.form["description"],
            image=filename
        )
        db.session.add(project)
        db.session.commit()

    projects = Project.query.all()
    return render_template("dashboard.html", projects=projects)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
@app.route("/about")
def about():
    return render_template("about.html")
    
    from flask import Flask, render_template, request, redirect
import smtplib

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        send_email(name, email, message)

        return "Message Sent Successfully!"
    return render_template('contact.html')

def send_email(name, email, message):
    sender = "yourgmail@gmail.com"
    password = "your_app_password"

    msg = f"Subject: New Client Message\n\nName: {name}\nEmail: {email}\nMessage: {message}"

    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login(sender, password)
    server.sendmail(sender, sender, msg)
    server.quit()

if __name__ == "__main__":
    app.run(debug=True)