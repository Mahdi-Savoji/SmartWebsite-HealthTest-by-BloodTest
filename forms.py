# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp, Length, Email

class UserForm(FlaskForm):
    fullname = StringField(label="Full Name", validators=[
        DataRequired(),
        Length(max=100, message="Full name must be under 100 characters.")
    ])
    username = StringField(label="Username", validators=[
        DataRequired(),
        Regexp(
            regex="^[a-zA-Z0-9_]{3,10}$",
            message="Username must be between 3 and 10 characters and can only contain letters, numbers, and underscores."
        )
    ])
    email = StringField(label="Email", validators=[
        DataRequired(),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField(label="Password", validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])

    submit = SubmitField(label='Login')
