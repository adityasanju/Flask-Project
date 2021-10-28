
from flask import render_template, url_for, flash, redirect, request
from flask_project import app, db, bcrypt, mail
from flask_project.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm
from flask_project.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message




@app.route("/")

@app.route("/loginhome")
def loginhome():
    return render_template('loginhome.html')

@app.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    return render_template('home.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password )
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form1 = LoginForm()
    if form1.validate_on_submit():
        user = User.query.filter_by(username=form1.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form1.password.data):
            login_user(user, remember=form1.remember.data)
            flash('Logged In Successfully')
            return redirect(url_for('profile'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form1)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile",methods=['GET','POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html',title = 'Profile',form=form)

def send_reset_email(user):

    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = "Here is your password - "

    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        flash('An email has been sent with instructions to reset your password.', 'info')
        send_reset_email(user)
        return redirect(url_for('login'))
    return render_template('forgot_password.html', title='Reset Password',form=form)







