from . import db
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from datetime import datetime

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    pfp_url = db.Column(db.String(50))
    bio = db.Column(db.String(400))

    following = db.Column(MutableList.as_mutable(PickleType), default=[])
    followers = db.Column(MutableList.as_mutable(PickleType), default=[])

    def __init__(self, name, email, pfp_url):
        self.name = name
        self.email = email
        self.pfp_url = pfp_url

# TODO: add support for video
class post(db.Model):
    _id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    text = db.Column(db.String(400))
    img_src = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))

    def __init__(self, name, text, img_src):
        self.name = name
        if text:
            self.text = text
        else:
            self.text = ''
        
        if img_src:
            self.img_src = img_src
        else:
            self.img_src = ''

        # set timestamp attribute
        self.timestamp = str(datetime.now())