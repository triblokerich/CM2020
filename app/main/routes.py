from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, AttendeeForm, ActivityForm
from app.models import User, Post, Club, Activity, Attendees
from app.translate import translate
from app.main import bp
from app.auth.email import welcome_user
from app.barcode.barcodescan import barcode_reader
from sqlalchemy import exc
from sqlalchemy import func
import sqlalchemy
from barcode import get_class,get_barcode_class,get_barcode,get
from barcode.writer import ImageWriter
import barcode

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


#   The Home Screen (index) - This shows the user name, current balance and messages from club officials

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    user = User.query.filter_by(username=current_user.username).first_or_404()

    def printC(answer):
        print
        return "\n{:0.2f}.\n".format(answer)

    strbal = printC(current_user.balance/100)
    club = Club.query.filter_by(clubnum=current_user.club).first_or_404()
    post = Post.query.filter_by(club=current_user.club).first_or_404()
    clubname = club.clubname
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, club=club.clubnum,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!','info')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)

    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, club=club, user=user, strbal=strbal, next_url=next_url,
                           prev_url=prev_url)


# Members screen - This is avalailable to all club officials and lists all members of the club.
# Required enhancement - show balance on account if enquiry made by a user with "treasurer" rights

@bp.route('/members/<username>')
@login_required
def members(username):

    def printC(answer):
        print
        return "\n{:0.2f}.\n".format(answer)

    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
#    print(user.username)
#    print(user.balance)
    strbal = printC(user.balance/100)
    club = Club.query.filter_by(clubnum=current_user.club).first_or_404()
    clubname = club.clubname
    users = User.query.filter_by(club=club.clubnum).order_by(User.surname,User.forename)
    return render_template('member.html', title=_('Members'),
        club=club,strbal=strbal, users=users)


# Profile screen - This shows all information to user himself and anyone with admin capabilities
#   To coach or sessionmanager it shows declared medical conditions and next of kin details

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
 #   usernum = user.usernum
    club = Club.query.filter_by(clubnum=user.club).first_or_404()
    clubname = club.clubname
    logo = club.logo
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user,  club=club, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/barcode/<username>')
@login_required
def barcodecreator(username):

    user = User.query.filter_by(username=username).first_or_404()
    usernum = str(user.usernum)
    CODE39 = barcode.get_barcode_class('code39')
    code39 = CODE39(usernum,add_checksum=False)
    fullname = code39.save('code39_barcode')
 #   usernum = "00" + str(user.usernum)
 #   EAN = barcode.get_barcode_class('ean13')
 #   ean = EAN(usernum)
 #   fullname = ean.save('ean13_barcode')
    return render_template('barcode.html', usernum=usernum)

@bp.route('/edit_profile2/<requesting_user>/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile2(requesting_user, username):
    change_user = User.query.filter_by(username=requesting_user).first_or_404()
    current_user = User.query.filter_by(username=username).first_or_404()
    club = Club.query.filter_by(clubnum=current_user.club).first_or_404()
    form = EditProfileForm(current_user.username)

    form.category.choices = [('1','Adult'),('2','Child')]
    form.gender.choices = [('M','M'),('F','F')]

    if form.validate_on_submit():
# ** Admin users only can change these fields
        if change_user.adminuser == 1:
            current_user.adminuser = form.adminuser.data
            current_user.coach = form.coach.data
            current_user.treasurer = form.treasurer.data
            current_user.sessionmanager = form.sessionmanager.data
            current_user.livemember = form.livemember.data
            print(current_user.current)
            if current_user.current == 0:
                print(form.memberstatus.data)
                if form.memberstatus.data == 1:
        #           email user - now live
                    print("send email")
                    club = Club.query.filter_by(clubnum=current_user.club).first_or_404()
                    clubname = club.clubname
                    forename = current_user.forename
                    welcome_user(user=current_user,clubname=clubname)
                    flash('A welcome email has been sent', 'info')
            current_user.current = form.memberstatus.data
            current_user.member_expire = form.member_expire.data
        current_user.username = form.username.data
        current_user.forename = form.forename.data
        current_user.surname = form.surname.data
        current_user.gender = form.gender.data
        current_user.dob = form.dob.data
        current_user.address1 = form.address1.data
        current_user.address2 = form.address2.data
        current_user.address3 = form.address3.data
        current_user.postcode = form.postcode.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        current_user.next_of_kin_name = form.next_of_kin_name.data
        current_user.next_of_kin_num = form.next_of_kin_num.data
        current_user.next_of_kin_name2 = form.next_of_kin_name2.data
        current_user.next_of_kin_num2 = form.next_of_kin_num2.data
        if form.category.data == 1:
            current_user.category = 'Adult'
        else:
            current_user.category = 'Child'
        current_user.about_me = form.about_me.data
        db.session.commit()
        if current_user.livemember == 0:
            flash('Your changes have been saved; the administrator will notify you when your user has been registered.','info')
        else:
            flash('Your changes have been saved.','info')
        return redirect(url_for('main.edit_profile2', requesting_user=change_user.username,username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.forename.data = current_user.forename
        form.surname.data = current_user.surname
 #       form.gender.data = current_user.gender
        form.dob.data = current_user.dob
        form.address1.data = current_user.address1
        form.address2.data = current_user.address2
        form.address3.data = current_user.address3
        form.postcode.data = current_user.postcode
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
        form.next_of_kin_name.data = current_user.next_of_kin_name
        form.next_of_kin_num.data = current_user.next_of_kin_num
        form.next_of_kin_name2.data = current_user.next_of_kin_name2
        form.next_of_kin_num2.data = current_user.next_of_kin_num2
        form.category.data = current_user.category
#        form.superuser.data = current_user.superuser  - never to be available on this screen
        if change_user.adminuser == 1:
            form.adminuser.data = current_user.adminuser
            form.coach.data = current_user.coach
            form.treasurer.data = current_user.treasurer
            form.sessionmanager.data = current_user.sessionmanager
            form.livemember.data = current_user.livemember
            form.memberstatus.data = current_user.current
            form.member_expire.data = current_user.member_expire
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form,club=club)


@bp.route('/activities/<username>', methods=['GET', 'POST'])
@login_required
def activities(username):
    form = ActivityForm()
    user = User.query.filter_by(username=current_user.username).first_or_404()
    club = Club.query.filter_by(clubnum=current_user.club).first_or_404()
    activities = Attendees.query.filter_by(club=current_user.club).order_by(Attendees.activitydate.desc()).group_by(Attendees.activitydate,Attendees.activitynumber)
    print(activities)
    form.activity.choices = [(str(row.activitynumber), row.activityname) for row in Activity.query.filter_by(club=club.clubnum)]
    if form.validate_on_submit():
        date = form.activitydate.data
        act = Activity.query.filter_by(activitynumber=form.activity.data).first_or_404()
        activityname = act.activityname
        activity = form.activity.data
        language = guess_language(form.activity.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        return redirect(url_for('main.attendee_register', activity = activity, activityname=activityname, date = date))
    return render_template('activity.html', title=_('Activities'), form=form,
                           club=club, user=user,activities=activities )



@bp.route('/attendees/<activity>/<date>', methods=['GET', 'POST'])
@login_required
def attendee_register(activity,date):
    club = Club.query.filter_by(clubnum=current_user.club).first_or_404()
    activitytable = Activity.query.filter_by(activitynumber = activity).first_or_404()
    childcost = activitytable.childcost
    adultcost = activitytable.adultcost
    nonmemberchildcost = activitytable.nonmemberchildcost
    nonmemberadultcost = activitytable.nonmemberadultcost
    current_club = current_user.club
    activity = activity
    activityname = activitytable.activityname
    date = date
    form = AttendeeForm(current_user.username)
 #   page = request.args.get('page', 1, type=int)
#    next_url = url_for('main.index', page=registered.next_num) \
#        if registered.has_next else None
#    prev_url = url_for('main.index', page=registered.prev_num) \
 #       if registered.has_prev else None


    if form.validate_on_submit():
       # Ensure the specified user is a valid user for this club - userref could be user number or name so we must handle both
        usercheck = User.query.filter_by(usernum=form.userref.data,club=current_club).first()
        if usercheck is None:
            usercheck = User.query.filter_by(username=form.userref.data,club=current_club).first()
            if usercheck is None:
                flash('***** Attendee unknown to this club *****', 'error')
                return redirect(
                    url_for('main.attendee_register', activity=activity, date = date))

    #  Add the Attendee record but the commit part below might lead to an error (for this time assumed to be duplicate key)
        usernum = usercheck.usernum
        username = usercheck.username
        category = usercheck.category
        user = User.query.filter_by(usernum=usernum).first()
        username = user.username
        if usercheck.category == 'Child':
            usercheck.balance = usercheck.balance - childcost
            cost = childcost
        else:
            usercheck.balance = usercheck.balance - adultcost
            cost = adultcost
        attendeeadd = Attendees(usernum=usernum, activitynumber=activity,
                            activitydate=date, activityname = activityname,
                            username=username,club=current_club, cost=cost)

        db.session.add(attendeeadd)

        #  The following code could be cleaner; it assumes an error is duplicate record. Worth cleaning up at some point.
        try:
            db.session.commit()
        except exc.IntegrityError as e:
            flash('********** Attendee already registered ***********','warning')
            db.session.rollback()
            return redirect(url_for('main.attendee_register', activity=activity,date=date))

        username = user.username
        flash('Registered' , 'success')
        return redirect(url_for('main.attendee_register', activity=activity, date=date))
    elif request.method == 'GET':
        form.club = current_club
    attendeelist = Attendees.query.filter_by(club=current_user.club,activitydate=date,activitynumber=activity).order_by(Attendees.update_time.desc() )
    return render_template('activityattendees.html', title=_('Activity Attendees'),
                           form=form,club=club,date=date,activity=activity,activityname=activityname,
                           attendees=attendeelist)




@bp.route('/myaccount/<username>')
@login_required
def myaccount(username):
    user = User.query.filter_by(username=username).first_or_404()
    print(user.username)
    print(user.balance)
    def printC(answer):
        print
        return "\n{:0.2f}.\n".format(answer)
    strbal = printC(user.balance/100)
#    myclub = Club.query.filter_by(clubnum=current_user.club).first_or_404()
    club = user.club
    users = User.query.filter_by(club=user.club).order_by(User.surname,User.forename)
    myactivities = Attendees.query.filter_by(username=username).order_by(Attendees.activitydate.desc())
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user != current_user:
        if current_user.adminuser == 0:
            if current_user.treasurer == 0:
                flash('Permission denied!','error')
                return redirect(url_for('main.members',username=user.username))
    print(strbal)
    return render_template('myaccount.html', username=username,myactivities=myactivities,strbal=strbal)


# What follows is all defunct code as we don't have a follow facility in the system

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        flash('User not found.','error')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!','warning')
        return redirect(url_for('main.user,username=current_user.username ', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('follow request accepted','info')
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

