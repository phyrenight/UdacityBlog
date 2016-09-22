from google.appengine.ext import db

class User(db.Model):
    """
        user info
    """
    userName = db.StringProperty(required=True)
    email = db.StringProperty()
    passHash = db.StringProperty()
    cookieSalt = db.StringProperty()

class UsersBlogPost(db.Model):
    """
         blog posts
    """
    user = db.StringProperty()
    title = db.StringProperty(required=True)
    bpost = db.TextProperty(required=True)
    dateTime = db.DateTimeProperty(auto_now_add=True)
    likes = db.ListProperty(str, default=None)


class Comments(db.Model):
    """
       comments on blog posts
    """
    user = db.StringProperty(required = True)
    comment = db.TextProperty(required=True)
    dateTime = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty(required=True)
    commentId = db.StringProperty(required=True) # related to blog post

    @classmethod
    def createComment(cls):
        comment = Comment(user = user,
                      title = title,
                      comment = comment)
        comment.put()

    def deleteComment(cls, commentid):
        pass
