from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Email

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField('First Name', validators=[InputRequired(), Length(max=30)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(max=30)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class FeedbackForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[InputRequired()])
    submit = SubmitField('Submit')