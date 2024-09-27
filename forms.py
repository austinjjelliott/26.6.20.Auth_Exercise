from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField('First Name', validators=[InputRequired(), Length(max = 30)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(max = 30)])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])

    
# **GET */login :*** Show a form that when submitted will login a user. 
# This form should accept a username and a password. Make sure you are using 
# WTForms and that your password input hides the characters that the user is 
# typing!

# **POST */login :*** Process the login form, ensuring the user is authenticated 
# and going to ***/secret*** if so.