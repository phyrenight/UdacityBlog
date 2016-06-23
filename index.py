import os
import random
import string
import jinja2
import webapp2
import hashlib

from google.appengine.ext import db
from models import UsersBlogPost, User

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


def validate_pwd(pwd, passHash):
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

class MainPage(Handler):
    def render_Html(self, title="", rant="", error=""):
        self.render("blogform.html", title=title, rant=rant, error=error)

    def get(self):
        self.render_Html()

    def post(self):
        title = self.request.get("title")
        rant = self.request.get("rant")

    	if not title or not rant:
            error = True
            self.render_Html(title, rant, error)

        else:
            postBlog = UsersBlogPost(title=title, bpost=rant)
            postBlog.put()
            page = "/blog/{}".format(str(postBlog.key().id()))
            self.redirect(page)


class BlogPage(Handler):
    def get(self):
        posts = db.GqlQuery("select * from UsersBlogPost")
        self.render('blogpost.html', posts=posts)


class BlogPost(Handler):
    def render_Html(self, postid):
        self.render("singlepost.html", postid=postid)

    def get(self, postid):
        keys = db.Key.from_path('UsersBlogPost', int(postid))
        post = db.get(keys)
        self.render_Html(post)

# in the future try to merge all render_Html and get render_Htmlinto 
# a single callable function(DRY)

class SignUp(Handler):
    def render_Html(self, name="", email="", error=False):
        self.render("register.html", name=name, email=email , error=error)

    def get(self):
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
            pwdHash = make_hash(name, pwd)
            user = User(userName=name, email=email, passHash=pwdHash)
            self.response.headers.add_header('Set-Cookie',
                '{}={}; Path=/'.format(name, pwdHash))
            # user.put()
            self.redirect("/welcome?username={}".format(name))

class Welcome(Handler):
    def get(self):
        user = self.request.get('username')
        if username is not None:
            self.render("welcome.html", user=user)
        else:
            self.redirect("/Signup")

class Login(Handler):
    def render_Html(self, name="", error=False):
        self.render("login.html", name=name, error=error)

    def get(self):
        self.render_Html()

    def post(self):
        name = self.request.get("name")
        pwd = self.request.get("pwd")

        # add try statement to handle error when a user is not in db 
        uname = db.GqlQuery("select * from User WHERE userName =:1", name)[0]       
        if name != uname.userName or not validate_pwd(pwd, uname.userName):

            error = True
            name = ""
            self.render_Html(name, error)

        else:
            self.response.headers.add_header('Set-Cookie',
                 '{}={}; Path=/'.format(name))
            self.redirect('/blog')    


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
                              ('/logout', Logout)],
                              debug=True)
