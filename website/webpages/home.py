from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from ..models import users, post, db
from ..functions import allowed_image, save_image
import os

home = Blueprint('home', __name__)

# TODO: enable searching for users
@home.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'], profile_image=session['pfp_url'])
    else:    
        return render_template("index.html")


# for viewing database data
@home.route('/view-users')
def view():
    if 'user' in session:
        return render_template('view.html', values=users.query.all(), profile_image=session['pfp_url'])
    else:
        return render_template('view.html', values=users.query.all())


@home.route('/view-posts')
def view_posts():
    if 'user' in session:
        return render_template('view_posts.html', values=reversed(post.query.all()), profile_image=session['pfp_url'], user=session['user'])
    else:
        return render_template('view_posts.html', values=post.query.all())