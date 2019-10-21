from flask import render_template
from app import db
from app.errors import bp
from app.models import User, Club, Attendees, Activity


@bp.app_errorhandler(404)
def not_found_error(error):
#    user = User.query.filter_by(usernum=1000).first_or_404()
#    user = User.query.filter_by(usernum=1000000001)
 #   print(user.club)
 #   club = Club.query.filter_by(clubnum=1000).first_or_404()
#    clubname = club.clubname
#    logo = club.logo
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
#    user = User.query.filter_by(usernum=1000).first_or_404()
#    user = User.query.filter_by(usernum=1000000001)
 #   print(user.club)
 #   club = Club.query.filter_by(clubnum=1000).first_or_404()
  #  clubname = club.clubname
 #  logo = club.logo
    return render_template('errors/500.html'), 500
