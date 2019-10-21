from flask import render_template, current_app
from flask_babel import _
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Club Manager 2020] Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def notify_admin(user,adminuser):
#    print(adminuser.email)
#    print(adminuser.username)
    send_email(_('[Club Manager 2020] New Member Notification'),
               sender=current_app.config['ADMINS'][0],
               recipients=[adminuser.email],
               text_body=render_template('email/new_user.txt',
                                         user=user, adminuser=adminuser.username),
               html_body=render_template('email/new_user.html',
                                         user=user, adminuser=adminuser.username))


def welcome_user(user,clubname):
    send_email(_('[Club Manager 2020] Welcome'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/welcome.txt',
                                         user=user,clubname=clubname),
               html_body=render_template('email/welcome.html',
                                         user=user,clubname=clubname))

