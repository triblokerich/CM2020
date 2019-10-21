from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, FormField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Length
# from wtforms_components import TimeField, read_only
from flask_babel import _, lazy_gettext as _l
from app.models import User, Club, Attendees, Activity


class EditProfileForm(FlaskForm):
    username = StringField(_l('User Name'), validators=[DataRequired()])
    forename = StringField(_l('Forename'), validators=[DataRequired(),Length(min=1, max=30)])
    surname = StringField(_l('Surname'), validators=[DataRequired(),Length(min=1, max=30)] )
    gender = SelectField(_l('Gender'),
                             validators=[DataRequired(),Length(min=0, max=1)])
    dob = DateField(_l('date of Birth (dd/mmm/yy)'),format='%Y-%m-%d', validators=[DataRequired()] )
    email = StringField(_l('Email'), validators=[DataRequired(), Length(min=1, max=30)] )
    address1 = StringField(_l('Address',validators=[DataRequired()], render_kw={'readonly': True}) )
    address2 = StringField(_l('Line 2'),  )
    address3 = StringField(_l('Line 3'),  )
    postcode = StringField(_l('Postcode'), validators=[DataRequired(),Length(min=1, max=8)] )
    about_me = TextAreaField(_l('Medical Conditions'),
                             validators=[Length(min=0, max=140)]) 
    next_of_kin_name = StringField(_l('Emergency Contact Name'), validators=[DataRequired(),Length(min=1, max=64)] )
    next_of_kin_num = IntegerField(_l('Emergency Contact Number'), validators=[DataRequired()] )
    next_of_kin_name2 = StringField(_l('Emergency Contact Name 2') )
    next_of_kin_num2 = IntegerField(_l('Emergency Contact Number 2') )
    category = SelectField(_l('Member Type (Adult/Child)' ))
 #   category = SelectField(_l('Member Type (Adult/Child)',choices=[('1','Adult'),('2','Child')]) )
 #   category = StringField(_l('Member Type (Adult/Child)') ))
    adminuser = BooleanField(_l('Administrator') )
    coach = BooleanField(_l('coach', render_kw={'readonly': True}))
    treasurer = BooleanField(_l('Treasurer') )
    sessionmanager = BooleanField(_l('Session Manager') )
    memberstatus = BooleanField(_l('Active Member') )
    member_expire = DateField(_l('Member Expires (dd/mmm/yy)'), format='%Y-%m-%d')
    livemember = BooleanField(_l('Registered User') )


    submit = SubmitField(_l('Submit'))


    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class ActivityForm(FlaskForm):
    activity = SelectField(_l('Activity'), validators=[DataRequired()])
    activitydate = DateField(_l('Activity Date (dd/mmm/yy)'),format='%Y-%m-%d', validators=[DataRequired()] )
    submit = SubmitField(_l('Submit'))


class AttendeeForm(FlaskForm):
 #   activitynum = SelectField(_l("Activity Name"), validators=[DataRequired()])
#    activitydate = DateField(_l('Activity Date (dd/mmm/yy)'),format='%Y-%m-%d', validators=[DataRequired()] )
    userref = StringField(_l('User Name/Number'), validators=[DataRequired()])
 #   thisclub = IntegerField(_l('Club'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(AttendeeForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is None:
                raise ValidationError(_('User Name / Number not Known.'))

