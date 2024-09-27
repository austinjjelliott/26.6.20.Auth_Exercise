from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import UserForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_exercise'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect ('/register')

@app.route('/register', methods = ["GET", "POST"])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        # Grab info from form 
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        # Create new user
        new_user = User.register(username, password, email, first_name, last_name)
        # Add user to db.session
        db.session.add(new_user)
        # Check if its valid. If so, add user to DB. If not, show error msg
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username Taken - Please Try Another')
            return render_template('register.html', form = form)
        
        session['user_id'] = new_user.username
        flash('Welcome! Successfully created your account', 'success')
        return redirect('/secret')

    return(render_template('register.html', form = form ))


@app.route('/login', methods = ["GET", "POST"])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back {user.username}', 'success')
            session['user_id'] = user.username
            return redirect('/secret')
        else:
            form.username.errors = ['Invalid Username/Password']
    return (render_template('/login.html', form = form))

@app.route('/secret')
def show_secret():
    return 'You Made It'

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash('You Are Now Logged Out', 'danger')
    return redirect('/')
