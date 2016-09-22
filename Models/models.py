from google.appengine.ext import db

class User(db.Model):
    """
        user info
    """
    userName = db.StringProperty(required=True)
    email = db.StringProperty()
    passHash = db.StringProperty()
    cookieSalt = db.StringProperty()
