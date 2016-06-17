from google.appengine.ext import db

class User(db.Model):
    """
        user info
    """
    userName = db.StringProperty(required = True)
    email = db.StringProperty()
    passHash = db.StringProperty()

class UsersBlogPost(db.Model):
    """
         blog posts
    """
   # user = db.KeyProperty(required = True, kind = 'User')
    title = db.StringProperty(required = True)
    bpost = db.TextProperty(required = True)
    dateTime = db.DateTimeProperty(auto_now_add = True)

# def blogKey(name = 'default'):
#    return db.Key.from_path('blogs', name)

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