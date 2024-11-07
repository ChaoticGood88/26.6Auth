from flask import Flask, redirect, render_template, session, url_for, flash
from models import db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

bcrypt = Bcrypt(app)
db.init_app(app)

# Utility function to ensure correct user
def ensure_correct_user(func):
    @wraps(func)
    def wrapper(username, *args, **kwargs):
        if "username" not in session or session["username"] != username:
            flash("You are not authorized to access this page.", "danger")
            return redirect(url_for("login"))
        return func(username, *args, **kwargs)
    return wrapper

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash("Registration successful!", "success")
        return redirect(url_for('user_profile', username=new_user.username))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('user_profile', username=user.username))
        else:
            flash("Invalid username or password.", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('home'))

# Display user profile and feedback
@app.route('/users/<username>')
@ensure_correct_user
def user_profile(username):
    user = User.query.get_or_404(username)
    feedback = Feedback.query.filter_by(username=username).all()
    return render_template('user_profile.html', user=user, feedback=feedback)

# Delete user and their feedback
@app.route('/users/<username>/delete', methods=['POST'])
@ensure_correct_user
def delete_user(username):
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username', None)
    flash("Your account has been deleted.", "success")
    return redirect(url_for('home'))

# Display form to add feedback
@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
@ensure_correct_user
def add_feedback(username):
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username
        )
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback added successfully.", "success")
        return redirect(url_for('user_profile', username=username))
    return render_template('feedback_form.html', form=form, form_title="Add Feedback")

# Display form to edit feedback
@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or session["username"] != feedback.username:
        flash("You are not authorized to edit this feedback.", "danger")
        return redirect(url_for("login"))

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Feedback updated successfully.", "success")
        return redirect(url_for('user_profile', username=feedback.username))
    return render_template('feedback_form.html', form=form, form_title="Edit Feedback")

# Delete feedback
@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or session["username"] != feedback.username:
        flash("You are not authorized to delete this feedback.", "danger")
        return redirect(url_for("login"))

    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted successfully.", "success")
    return redirect(url_for('user_profile', username=feedback.username))
