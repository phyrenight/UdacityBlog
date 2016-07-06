import os
import random
import string
import jinja2
import webapp2
import hashlib

from google.appengine.ext import db
from models import UsersBlogPost, User, Comments

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True,)
jinja_env.globals['url_for'] = webapp2.uri_for


def get_salt():
   return  "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(5))


def make_hash(pwd, salt=None):
    if not salt:
        salt = get_salt()
    passHash = hashlib.sha256(salt + pwd).hexdigest()
    return "{}|{}".format(passHash,salt)


def validate_pwd(pwd, passHash):  # change to validate_hash 
    line = passHash.find('|')
    saltWord = passHash[line+1:]
    if passHash == make_hash(pwd, saltWord):
        return True
    else:
        return False


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def check_cookie(self, name):
        cookieVal = self.request.cookies.get(name)
        return cookieVal

    def get_username(self, name):  #  test currently working on
        """
            gets username from cookie 
        """
        if self.check_cookie(name):
            cookie = self.check_cookie(name)
            username = cookie.split('|')[0]
            return username

    def make_cookie(self, name, hash):
        """
            creates a cookie using a hash of the user name.
            Each time a user logins a new hash will be created.
        
        """
        just_hash = hash.split('|')[0]
        print just_hash
        salt = hash.split('|')[1]
        print salt
        self.response.headers.add_header('Set-Cookie',
            '{}={}; Path=/'.format('username', name + '|' + just_hash))
        user = db.GqlQuery('select * from User WHERE userName =:1', name)
        print user
        user.cookie_salt = salt



class MainPage(Handler):
    def render_Html(self, title="", rant="", error="", user=""):
        self.render("blogform.html", title=title, rant=rant, error=error,
                    user=user)

    def get(self):
        if self.get_username('username'):
            user = self.get_username('username')
            self.render_Html(user=user)
        else:
            self.redirect('/login')

    def post(self):
        user = self.get_username('username')
        title = self.request.get("title")
        rant = self.request.get("rant")

    	if not title or not rant:
            error = True
            self.render_Html(title, rant, error, user)

        else:
            postBlog = UsersBlogPost(title=title, bpost=rant) # add user
            postBlog.user = user
            postBlog.put()
            page = "/blog/{}".format(str(postBlog.key().id()))
            self.redirect(page)


class BlogPage(Handler):
    """
       Main blog page
    """
    # add function to get db queries tht both functions can use
    def get(self):
        posts = db.GqlQuery("select * from UsersBlogPost")
        comments = db.GqlQuery("select * from Comments")
        user = self.get_username('username')  # Test currently working on
        self.render('blogpost.html', posts=posts, comments=comments, user=user)


    def post(self):
        """
            test
        """
        posts = db.GqlQuery("select * from UsersBlogPost")
        comments = db.GqlQuery("select * from Comments")
        title = self.request.get("Ctitle")
        comment = self.request.get("comment")
        user = self.get_username('username')
        if title is None or comment is None:
            error = True
            self.render('blogpost.html', Ctitle=title, comment=comment,
                         posts=posts, comments=Comments, user=user)

        else:
            title = self.request.get("Ctitle")
            comment = self.request.get("comment")
            postid = self.request.get("postid")
            print postid
            userComment = Comments(user=user, comment=comment,title=title,
                              commentId=postid)
            userComment.put()
            self.render('blogpost.html',posts=posts, comments=comments,
                        user=user)


class EditPost(Handler):
    """
        edits post in the database.
    """
    def render_Html(self, title="", rant="", error=False, user=""):
        self.render('blogform.html', title=title, rant=rant, error=error,
                     user=user)

    def get(self, postids):
        if self.get_username('username'):
            edit = self.request.get("edit")
            print edit
            if edit != "":
                print "Hello"
                keys = db.Key.from_path('UsersBlogPost', int(postids))
                post = db.get(keys)
                rant = post.bpost
                title = post.title
                user =  self.get_username('username')  # add check for a user logged in
                self.render_Html( title=title, rant=rant, user=user)
            else:
                keys = db.Key.from_path("Comments", int(postids))
                comment = db.get(keys)
                rant = comment.comment
                title = comment.title
                user = self.get_username('username')
                self.render_Html(title=title, rant=rant, user=user)
        else:
            self.redirect('/login')

    def post(self, postids):
        user = self.get_username('username')
        title = self.request.get("title")
        rant = self.request.get("rant")
        if title is None or rant is None:
            error = True
            self.render_Html(title=title, rant=rant, error=error, user=user)
        else:
            keys = db.Key.from_path('UsersBlogPost', int(postids))
            post = db.get(keys)
            post.title = title
            post.bpost = rant
            post.put()
            self.redirect("/blog")


class DeletePost(Handler):
    def render_Html(self, user, title="", error=False):
        self.render("delete.html", title=title, user=user, error=error)

    def get(self, postid):
        if self.get_username('username'):
            user = self.get_username('username')
            keys = db.Key.from_path('UsersBlogPost', int(postid))
            post = db.get(keys)
            if user == post.user:
                title = post.title
                self.render_Html(user, title)
            else:
                title = post.title
                error = True
                self.render_Html(user, title, error)     
        else:
            self.redirect("/login")

    def post(self, postid):
        if self.get_username('username'):
            user = self.get_username('username')
            keys = db.Key.from_path('UsersBlogPost', int(postid))
            post = db.get(keys)   
            post.delete()
            self.redirect('/blog')
        else:
            self.redirect("/login")


class BlogPost(Handler):
    def render_Html(self, post="", user="", comments="", testKey="", task="",
                     message=""):
        self.render("singlepost.html", post=post, user=user, comments=comments,
                     editKey=testKey, task=task, message=message)

    def get_post_comments(self):
        return db.GqlQuery("select * from Comments")

    def get_posts(self, postid):
        keys = db.Key.from_path('UsersBlogPost', int(postid))
        post = db.get(keys)
        return post

    def get(self, postid):
        user = self.get_username('username')
        comments = db.GqlQuery("select * from Comments")
        post = self.get_posts(postid)
        task = self.request.get('task')
        if task == "EditComment":
            editKey = self.request.get('edit')
            testKey = db.Key.from_path('Comments', int(editKey))
            self.render_Html(post, user, comments, testKey, task)
        
        elif task == "DeleteComment":
            editKey = self.request.get('delete')
            testKey = db.Key.from_path('Comments', int(editKey))
            self.render_Html(post, user, comments, testKey, task)

        else:
            self.render_Html(post, user, comments)
    
    def test_for_none(self, item):  # move to handle and update other classes
        if item is None or item == "":
            return True

    def post(self, postid):
        if self.get_username('username'):
            user = self.get_username('username')
        task = self.request.get('task')
        key = db.Key.from_path('UsersBlogPost', int(postid))
        post = db.get(key)
        comments = db.GqlQuery("select * from Comments")
        if task == 'EditComment':
            editKey = self.request.get('edit')
            Etitle = self.request.get('Etitle')
            Ecomments = self.request.get('Ecomment') 
            commentKey = db.Key.from_path('Comments', int(editKey))
            commentEdit = db.get(commentKey)
            commentEdit.comment = Ecomments
            commentEdit.title = Etitle
            # add test to make sure current user is creator of post before editing
            if user == commentEdit.user:
                commentEdit.put()
                return self.redirect('/blog')
            else:
                editKey = self.request.get('edit')
                message = "You are not the creator of this comment."
                self.render_Html(post, user, comments, editKey,
                                 task, message)
            
        elif task =='DeleteComment':
            editKey = self.request.get('delete')
            testKey = db.Key.from_path('Comments', int(editKey))
            deleteComment = db.get(testKey)
            # add test to make sure current user us the creator of the pst before deleting it
            if user == deleteComment.user:
                deleteComment.delete()
                self.redirect('/blog')
            else:
                message = "You are not the creator of this comment."
                self.render_Html(post, user, comments, editKey,
                                 task, message)
        else:
            error = False
            user = self.get_username("username")
            title = self.request.get('Ctitle')
            comment = self.request.get('comment')  # form comment
            comments = db.GqlQuery("select * from Comments") # comments stored in db
            post = self.get_posts(postid)
            if self.test_for_none(comment) or self.test_for_none(title):
                print "hello"
                error=True
                #self.render('singlepost.html', Ctitle=title,
                          #   comment=comment, user=user, comments=comments,
                          #   error=error, post=post)
                self.redirect('/blog/{}'.format(postid))
            else:
                print "bye"
                comment = Comments(user=user, comment=comment, title=title,
                                    commentId=str(postid))
                comment.put()
                self.render('singlepost.html', post=post, user=user,
                             comments=comments)


# in the future try to merge all render_Html and get render_Htmlinto 
# a single callable function(DRY)

class SignUp(Handler):
    def render_Html(self, name="", email="", error=False, user=""):
        self.render("register.html", name=name, email=email , error=error,
                     user=user)

    def get(self):
        if self.get_username('username'):
            self.redirect("/blog")
        else:
            self.render_Html()

    def post(self):
        name = self.request.get("name")
        pwd = self.request.get("pwd")
        verifypwd = self.request.get("verifypwd")
        email = self.request.get("email")

        if pwd != verifypwd or name == "":
            error = True
            self.render_Html(name, email, error)

        Uname = db.GqlQuery("select * from User")
        for i in Uname:
            if name in i.userName:
                error = True
                self.render_Html(name, email, error)
                break

        else:
            pwdHash = make_hash(pwd)
            user = User(userName=name, email=email, passHash=pwdHash)
            self.response.headers.add_header('Set-Cookie',
                '{}={}; Path=/'.format('username', make_hash(name)))
            user.put()
            self.make_cookie(name, make_hash(name))
            self.redirect("/welcome?username={}".format(name))

class Welcome(Handler):
    def get(self):
        user = self.request.get('username')
        if user is not None:
            self.render("welcome.html", user=user)
        else:
            self.redirect("/Signup")

class Login(Handler):
    def render_Html(self, name="", error=False, user=""):
        self.render("login.html", name=name, error=error, user=user)

    def get(self):
            self.render_Html()

    def post(self):
        name = self.request.get("name")
        pwd = self.request.get("pwd")

        # add try statement to handle error when a user is not in db 
        try:
            uname = db.GqlQuery("select * from User  WHERE userName =:1", name)[0]       
            if name != uname.userName or not validate_pwd(pwd, uname.passHash):
                error = True
                name = ""
                self.render_Html(name, error)
            else:
                self.response.headers.add_header('Set-Cookie',
                    '{}={}; Path=/'.format("username", name))
                self.redirect('/blog')
        except:
            message = "User not found!"
            self.render("login.html", message=message, user="")

class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie',
                                          "username=; Path=/")
        self.redirect('/blog')

app = webapp2.WSGIApplication([('/blogform', MainPage),
                              ('/blog', BlogPage), # main
                              ('/blog/([0-9]+)', BlogPost), # single post
                              ('/SignUp', SignUp),
                              ('/login', Login),
                              ('/welcome', Welcome),
                              ('/logout', Logout),
                              ('/editpost/([0-9]+)', EditPost),
                              ('/delete/([0-9]+)', DeletePost)],
                              debug=True)
