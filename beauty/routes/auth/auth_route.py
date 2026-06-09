from flask import Blueprint, render_template, url_for, flash, redirect, request
from beauty import db, bcrypt
from beauty.forms import RegistrationForm, LoginForm
from beauty.models import User, Cart
from flask_login import login_user, current_user, logout_user

auth = Blueprint('auth', __name__)

# registration route
@auth.route('/register', methods = ['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # create the new user
        user = User(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password = hashed_password
        )

        # add user to the database
        db.session.add(user)
        db.session.commit()

        # initialize a cart for new users
        user_cart = Cart(user_id = user.id)
        db.session.add(user_cart)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template(
        'auth/register.html',
        title = 'Register',
        form = form
    )


# login route
@auth.route('/login', methods = ['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful, Welcome back!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template(
        'auth/login.html',
        title = 'Login',
        form = form
    )


# logout route
@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out, see you next time', 'info')
    return redirect(url_for('auth.login'))