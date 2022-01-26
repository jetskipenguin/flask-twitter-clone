from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from sqlalchemy.exc import SQLAlchemyError
from ..models import users, post, db
from ..functions import allowed_image, save_image
import os

''' This file holds webpages related to the user's session'''

pages = Blueprint('pages', __name__)

@pages.route('<user>', methods=['POST', 'GET'])
def user(user):
    found_user = users.query.filter_by(name=user).first()
    user_posts = post.query.filter_by(name=user).all()
    if found_user:
        if request.method == "POST":
            if user != session['user']:
                client = users.query.filter_by(name=session['user']).first()
                
                # Unfollowing User
                if request.form.get('unfollow') == 'unfollow':
                    session['following'].remove(user)
                    client.following.remove(user)
                    found_user.followers.remove(session['user'])

                # Following User
                if request.form.get('follow') == "follow":
                    if user not in session['following']:
                        session['following'].append(user)
                        client.following.append(user)
                        found_user.followers.append(session['user'])
                
                # Commit to database
                try:
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
                    flash("Error Performing Action, Please Try Again later")

        # Set follower count appropriately
        follower_count = 0
        following_count = 0
        if user == session['user']:
            follower_count = len(session['followers'])
            following_count=len(session['following'])
        else:
            # Pull found_user's follower counts
            for i in found_user.followers:
                follower_count += 1

            for i in found_user.following:
                following_count += 1
            

        return render_template("profile.html", user=user, bio=found_user.bio, posts=user_posts,follower_count=follower_count, following_count=following_count)

    else:
        return render_template('profile.html')

@pages.route('following/<user>')
def following(user):
    if user == session['user']:
        return render_template("following.html", following=session['following'])
    else:
        # pull data from database
        found_user = users.query.filter_by(name=user).first()
        return render_template("following.html", following=found_user.following[:])

@pages.route('followers/<user>')
def followers(user):
    if user == session['user']:
        return render_template("followers.html", followers=session['followers'])
    else:
        # pull data from database
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            return render_template('followers.html', followers=found_user.followers[:])

@pages.route('settings', methods=['GET', 'POST'])
def settings():
    if 'user' in session:
        user_email = None
        if request.method == "POST":
            # check for image uploads
            if request.files.get('image'):
                image = request.files["image"]

                # saves with absolute path
                directory = "{}\\{}".format(current_app.config['ABSOLUTE_IMAGE_UPLOADS'], session['user'])
                filename = allowed_image(image.filename, request.cookies.get("filesize"), directory, True)
                
                # if file is valid
                if filename:
                    save_image(directory, current_app.config['PROFILE_FILENAME'], image)

                    found_user = users.query.filter_by(name=session['user']).first()
                    if found_user:
                        # stores relative filepath in database and session
                        filepath = "{}\\{}\\{}".format(current_app.config['RELATIVE_IMAGE_UPLOADS'], session['user'], current_app.config['PROFILE_FILENAME'])
                        session['pfp_url'] = filepath
                        found_user.pfp_url = filepath
                        db.session.commit()
                        flash("Image sucessfully saved")
                    else:
                        flash("Image upload unsucessful, please try again later")
                else:
                    flash("Image upload unsucessful")

            # check for email change
            if request.form.get('email'):
                # get email from form
                user_email = request.form['email']
                # record email in session
                session['email'] = user_email
                # record email in database
                found_user = users.query.filter_by(name=session['user']).first()
                found_user.email = user_email
                db.session.commit()
                flash("Email saved!")

        # if user is not resetting email
        if user_email == None:
            if 'email' in session:
                user_email = session['email']
            else:
                user_email = ''

        # check for bio change
        if request.form.get('bio'):
            user_bio = request.form['bio']
            if len(user_bio) > current_app.config['BIO_LENGTH']:
                flash('Biography cannot be longer than {} chars!'.format(current_app.config['BIO_LENGTH']))
            else:
                found_user = users.query.filter_by(name=session['user']).first()
                found_user.bio = user_bio
                db.session.commit()
                flash("Bio Saved!")

        return render_template('settings.html', user=session['user'], email=user_email, profile_image=session['pfp_url'])
    else:
        return redirect(url_for('pages.login'))

@pages.route('create-post', methods=['GET', 'POST'])
def create_post():
    if 'user' in session:
        if request.method == "POST":
            text = None
            image_src = None

            if request.files.get('image'):
                image = request.files["image"]

                directory = os.path.join(current_app.config['ABSOLUTE_IMAGE_UPLOADS'], session['user'])
                filename = allowed_image(image.filename, request.cookies.get("filesize"), directory, False)

                # if image file valid
                if filename:
                    save_image(directory, filename, image)

                    # stores relative filepath
                    image_src = "{}\\{}\\{}".format(current_app.config['RELATIVE_IMAGE_UPLOADS'], session['user'], filename)

            text = request.form.get('text')

            # add post to database
            if len(text) > current_app.config['POST_LENGTH']:
                flash("Post text cannot be longer than {} chars!".format(current_app.config['POST_LENGTH']))
            else:
                pst = post(session['user'], text, image_src)
                db.session.add(pst)
                db.session.commit()
                flash('Successfully created post!')

            return redirect(url_for("home.index"))

        return render_template('create-post.html', user=session['user'], profile_image=session['pfp_url'])
    else:
        redirect(url_for('pages.login'))

@pages.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        # begins user session
        session.permanent = True
        # records username in session data
        user = request.form['nm']
        session['user'] = user

        found_user = users.query.filter_by(name=session['user']).first()
        
        if found_user:
            session['email'] = found_user.email
            session['pfp_url'] = found_user.pfp_url

            session['following'] = list(found_user.following)
            session['followers'] = list(found_user.followers)
        else:
            print("Adding new user")
            # add new user to database
            usr = users(user, '', 'static/images/default.jfif')
            db.session.add(usr)
            db.session.commit()
            # add default pfp url to session
            session['pfp_url'] = 'static/images/default.jfif'
            session['email'] = ''

        flash('Login Successful')
        return redirect(url_for("pages.user", user=session['user']))
    else:
        if 'user' in session:
            return redirect(url_for('pages.user'))
            
        return render_template("login.html")

@pages.route('/logout')
def logout():
    if 'user' in session:
        flash("Successfully Logged Out!", "info")
    session.pop("user", None)
    session.pop('email', None)
    session.pop('pfp_url', None)
    session['following'] = []
    session['followers'] = []
    return redirect(url_for('pages.login'))
