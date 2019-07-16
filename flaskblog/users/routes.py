from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskblog import db, bcrypt       # directly importing from the package imports from __init__.py file
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)    # argument 'users' is the name of this blueprint


# using @users instead of @app because we're creating routes specifically for this user's blueprint 
# and then later register these with the app
@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:   # if user is already logged in, redirect him/her to the home page
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # if the form is validated, hash the password and create a new user with the username,
        # email and hashed_password and save the user to database to access later
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # used .decode() to get string instead of bytes
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title = 'Register', form = form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
            # these 2 lines above are only for when user is logged out and access the account page, in which
            # case a 'next' argument is generated in the address bar indicating where we'll go after login
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title = 'Login', form = form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:       # if picture is uploaded by the user, save the picture in the filesystem
            picture_file = save_picture(form.picture.data)  # and set the current user's picture to this saved
            current_user.image_file = picture_file    # profile picture
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()     # no need for .add() because both username and email are already in the database
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account')) # redirecting causes the browser to send a GET request instead of rendering template
                                            # which causes the browser to send the POST request again. This is called the
                                            # "post/redirect/get" pattern

    elif request.method == 'GET':           # to populate the current user's data in the form by default on GET
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type = int)  # get an integer argument from address bar as the page no. which defaults to 1
    user = User.query.filter_by(username = username).first_or_404() # get posts of a specific user (author)
    posts = Post.query\
            .filter_by(author = user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page = page, per_page = 6)  # newest posts first & posts per page is set to 6
    return render_template('user_posts.html', posts = posts, user = user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:   # if the user's logged out only then he needs to reset password
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to reset your password with instructions', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:   # if the user's logged out only then he needs to reset password
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token!', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)