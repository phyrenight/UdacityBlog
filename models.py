from google.appengine.ext import db

class User(db.Model):
    """
        user info
    """
    userName = db.StringProperty(required = True)
    email = db.StringProperty()
    passHash = db.StringProperty()

class BlogPost(db.Model):
    """
         blog posts
    """
   # user = ndb.KeyProperty(required = True, kind = 'User')
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    dateTime = db.DateTimeProperty(auto_now_add = True)
   # postId = db.IntegerProperty()
"""
class Comment(ndb.Model):
    
       comments on blog posts
    
        user = ndb.KeyProperty(required = True, kind = 'User')
        comment = ndb.TextProperty(required = True)
        dateTime = ndb.DateTimeProperty(auto_now_add = True)
        title = ndb.StringProperty()
        id = ndb.keyProperty(required = True, kind='BlogPost')

    @classmethod
    def createComment(cls)
    comment = Comment(user = user,
                      title = title,
                      comment = comment)
"""