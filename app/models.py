from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.usernum')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.usernum'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    usernum = db.Column(db.Integer, index=True, unique=True)
    forename = db.Column(db.String(30), index=True)
    surname = db.Column(db.String(30), index=True)
    club = db.Column(db.Integer,db.ForeignKey('club.clubnum'))
    email = db.Column(db.String(120), index=True, unique=True)
    current = db.Column(db.BOOLEAN)
    member_expire = db.Column(db.DATE) 
    category = db.Column(db.String(10))
    gender = db.Column(db.String(1))
    dob = db.Column(db.DATE)
    address1 = db.Column(db.String(30))
    address2 = db.Column(db.String(30))
    address3 = db.Column(db.String(30))
    postcode = db.Column(db.String(8))
    next_of_kin_name = db.Column(db.String(64))
    next_of_kin_num = db.Column(db.Integer, default=0)
    next_of_kin_name2 = db.Column(db.String(64))
    next_of_kin_num2 = db.Column(db.Integer, default=0)
    ethnicity = db.Column(db.String(20))
    parent_email = db.Column(db.String(120))
    balance = db.Column(db.Integer, default =0)
    paymentuser = db.Column(db.String(64))
    superuser = db.Column(db.BOOLEAN, default= False)
    adminuser = db.Column(db.BOOLEAN, default= False)
    coach = db.Column(db.BOOLEAN, default= False)
    treasurer = db.Column(db.BOOLEAN, default= False)
    sessionmanager = db.Column(db.BOOLEAN, default= False)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    livemember = db.Column(db.BOOLEAN, default= False)
    followed = db.relationship(
       'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
            
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.usernum).count() > 0

    def followed_posts(self):
        # original code
        # followers, (followers.c.followed_id == Post.user_id)).filter(
        #       followers.c.follower_id == self.id)
        #   own = Post.query.filter_by(user_id=self.id)
   #        return followed.union(own).order_by(Post.timestamp.desc())
        followed = Post.query.join(
        #    followers, (followers.c.followed_id == Post.user_id)).filter(
        #        followers.c.follower_id == self.id)
            followers, (followers.c.followed_id == Post.user_id)).filter(
                Post.club == self.club)
        return followed.order_by(Post.timestamp.desc())
   #     return followed.union(own).order_by(Post.timestamp.desc())

   #     followed = Post.query.join(User.usernum == Post.user_id)
  #      own = Post.query.filter_by(user_id=self.id)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.usernum'))
    club = db.Column(db.Integer, db.ForeignKey('club.clubnum'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clubnum = db.Column(db.Integer)
    clubname = db.Column(db.String(140))
    usernum = db.Column(db.Integer, db.ForeignKey('user.usernum'))
    logo = db.Column(db.String(140))
    posts = db.relationship('Post', backref='clubpost', lazy='dynamic')

    def __repr__(self):
        return '<Club {}>'.format(self.clubnum)
        
    def clublogo(self, size):
        return '{}'.format(self.logo, size)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activitynumber = db.Column(db.Integer)
    activityname = db.Column(db.String(80))
    club = db.Column(db.Integer,db.ForeignKey('club.clubnum'))
    childcost = db.Column(db.Integer)
    adultcost = db.Column(db.Integer)
    nonmemberchildcost = db.Column(db.Integer)
    nonmemberadultcost = db.Column(db.Integer)

    def __repr__(self):
        return '<Activity {}>'.format(self.activitynumber)


class Attendees(db.Model):
    activitynumber = db.Column(db.Integer, primary_key=True)
    activitydate = db.Column(db.Integer, primary_key=True)
    club = db.Column(db.Integer, primary_key=True)
    usernum = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    activityname = db.Column(db.String(80))
    cost = db.Column(db.Integer, default= 0)
    received = db.Column(db.Integer, default=0)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Attendees {}>'.format(self.activitynumber)


