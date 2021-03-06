from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from ..models import users, post, db

home = Blueprint('home', __name__)

# TODO: enable searching for users
@home.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        search = db.session.query(users).filter(users.name.like(request.form.get('search') + '%'))
        for i in search:
            print(i.name)
        
    if 'user' in session:
        client = db.session.query(users).filter_by(name=session['user']).first()
        posts = []
        for user in client.following:
            try:
                for i in post.query.filter_by(name=user).all():
                    posts.append(i)
            except:
                print("Couldn't recieve posts from database for {}!".format(user))

        return render_template('index.html', user=session['user'], profile_image=session['pfp_url'], values=posts)
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