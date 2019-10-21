from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Club
from app.auth.email import send_password_reset_email, notify_admin
from sqlalchemy import func


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
      #  user = User.query.filter_by(username=form.username.data).first()
     #   club = Club.query.filter_by(clubnum=form.clubnum.data).first()
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            user = User.query.filter_by(usernum=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password','info')
                return redirect(url_for('auth.login'))
        username = user.username
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index' )
        return redirect(next_page)
    return render_template('auth/login.html',title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index' ))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    clubs = []
    user = current_user
    form = RegistrationForm()
    clubrows = Club.query.all()
#    for club in clubrows:
#        clubs.append(club.clubnum)
#        clubs.append(club.clubname)
    form.club.choices = [(str(row.clubnum), row.clubname) for row in Club.query.all()]
 #   print(form.club.data)validators=[DataRequired(),
    if form.validate_on_submit():
        clubrow = Club.query.filter_by(clubname = form.club.data).first()
        usernumber = int(form.club.data)
        usernumber = (usernumber +1) * 1000000
        nextuser = (db.session.query(func.max(User.usernum)).filter(User.usernum<usernumber).scalar() or 0)
        nextuser = nextuser +1
        user = User(username=form.username.data, email=form.email.data, usernum=nextuser,club=form.club.data)
    #    user = User(username=form.username.data, email=form.email.data, usernum=nextuser)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        print(form.club.data)
        admin_user = User.query.filter_by(club = form.club.data, adminuser = 1)
        for admins in admin_user:
            print(admin_user)
            print(admins.usernum)
            notify_admin(user=user,adminuser = admins)

        flash('Congratulations, you are now a registered user! Logon to complete your profile','info')
        return redirect(url_for('auth.login'))
    elif request.method == 'GET':
        print()
 #       clubrows = Club.query.all()
 #       for club in clubrows:
 #           clubs.append(club.clubnum)
 #           clubs.append(club.clubname)
     #   form.club.choices = [(row.clubnum, row.clubname) for row in Club.query.all()]
    return render_template('auth/register.html', title=_('Register'),  form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password','info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.','info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
