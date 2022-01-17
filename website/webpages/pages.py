from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from ..models import users, post, db
from ..functions import allowed_image, save_image
import os

''' This file holds webpages related to the user's session'''

pages = Blueprint('pages', __name__)

@pages.route('<user>', methods=['POST', 'GET'])
def user(user):
    email = None
    if user == session['user']:
        if request.method == 'POST':
            # get email from form
            email = request.form['email']
            # record email in session
            session['email'] = email
            # record email in database
            found_user = users.query.filter_by(name=session['user']).first()
            found_user.email = email
            db.session.commit()
            flash("Email saved!")
        elif 'email' in session:
            email = session['email']
        else:
            # if email not in session data, pull it from database
            found_user = users.query.filter_by(name=session['user']).first()
            email = found_user.email
        
        print(session['pfp_url'])
        return render_template("profile.html", user=user)
    else:
        return render_template('profile.html', user=user)


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

            # TODO: add length checker
            if request.form.get('text'):
                text = request.form['text']

            # add post to database
            pst = post(session['user'], text, image_src)
            db.session.add(pst)
            db.session.commit()
            flash('Successfully created post!')

            return redirect(url_for("pages.index"))

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
            # if found_user.name == user:
            #     flash('That username is taken')
            #     return(redirect(url_for('pages.login')))
            # add database entries to session data for user
            session['email'] = found_user.email
            session['pfp_url'] = found_user.pfp_url
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
    return redirect(url_for('pages.login'))
