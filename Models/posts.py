from google.appengine.ext import db

class UsersBlogPost(db.Model):
    """
         blog posts
    """
    user = db.StringProperty()
    title = db.StringProperty(required=True)
    bpost = db.TextProperty(required=True)
    dateTime = db.DateTimeProperty(auto_now_add=True)
    likes = db.ListProperty(str, default=None)

