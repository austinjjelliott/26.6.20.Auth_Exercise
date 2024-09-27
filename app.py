from flask import Flask, render_template, redirect, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm
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
        return redirect(f'/users/{username}')

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
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Invalid Username/Password']
    return (render_template('/login.html', form = form))

@app.route('/users/<username>')
def show_user(username):
    if 'user_id' not in session:
        flash('Please Login To View')
        return redirect('/')
    user = User.query.get_or_404(session['user_id'])
    feedback = user.feedback
    form = FeedbackForm()
    return render_template('user_homepage.html', user = user, feedback = feedback, form = form)


@app.route('/users/<username>/delete', methods = ["POST"])
def delete_user(username):
    user = User.query.get_or_404(username)
    feedback = user.feedback
    if session['user_id'] != user.username:
        flash('You need to login first!')
        return redirect('/login')
    if user.username == session['user_id']:
        db.session.delete(user)
        db.session.commit()
        session.clear()  # Clear session to log the user out
        flash('Account deleted', 'danger')
        return redirect('/register')
    return render_template('user_homepage.html', user = user, feedback = feedback)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash('You Are Now Logged Out', 'danger')
    return redirect('/')


@app.route('/feedback/<int:id>/delete', methods = ['POST'])
def delete_feedback(id):
    if 'user_id' not in session:
        flash('Please login first!', 'danger')
        return redirect('/')
    user = User.query.get_or_404(session['user_id'])
    feedback = Feedback.query.get_or_404(id)
    if feedback.username == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback Deleted!', 'success')
        return redirect(url_for('show_user', username = user.username))
    
@app.route('/users/<username>/feedback/add', methods = ['GET', 'POST'])
def add_feedback(username):
    user = User.query.get_or_404(username)
    if 'user_id' not in session or session['user_id'] != username:
        flash('You must be logged in to add feedback', 'danger')
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feed = Feedback(title = title, content = content, username = username)
        db.session.add(new_feed)
        db.session.commit()
        flash('Feedback Submitted', 'success')
        return redirect(url_for('show_user', username = username))
    return render_template('add_feedback.html', user = user, form = form)

@app.route('/feedback/<int:id>/update', methods = ['GET', 'POST'])
def update_feedback(id):
    user = User.query.get_or_404(session['user_id'])
    feedback = Feedback.query.get_or_404(id)
    form = FeedbackForm(obj = feedback)
    if 'user_id' not in session:
        flash('Please login first!', 'danger')
        return redirect('/')
    if feedback.username == session['user_id']:
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash('Feedback has been updated!', 'success')
            return redirect(url_for('show_user', username = session['user_id']))
    return render_template('update_feedback.html', user = user, feedback = feedback, form = form)





# **GET */feedback/<feedback-id>/update :*** Display a form to edit feedback —
# Make sure that only the user who has 
# written that feedback can see this form **

# **POST */feedback/<feedback-id>/update :*** Update a specific piece of feedback
# and redirect to /users/<username> — **Make sure that only the user who has 
# written that feedback can update it.**



