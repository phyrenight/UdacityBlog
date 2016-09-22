from google.appengine.ext import db

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