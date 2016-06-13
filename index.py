import os
import random
import string
import jinja2
import webapp2
import hashlib

from google.appengine.ext import db
from models import BlogPost, User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

def get_salt():
   return  "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(5))

def make_hash(pwd, salt=None):
    if not salt:
        salt = get_salt()
    passHash = hashlib.sha256(salt + pwd).hexdigest()
    return "{}|{}".format(passHash,salt)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


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
            postBlog = BlogPost(title=title, post=rant)
            postBlog.put()
            self.redirect("/blog")


class BlogPage(Handler):
    def get(self):
        posts = db.GqlQuery("select * from BlogPost")
        self.render('blogpost.html', posts=posts)


class BlogPost(Handler):
    def get(self):
        pass

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
            print pwdHash
            user = User(userName=name, email=email, passHash=pwdHash)
            #user.put()
            self.redirect("/blog")

class login(Handler):
    def post(self):
        pass


class logout(Handler):
    def post(self):
        pass
app = webapp2.WSGIApplication([('/blogform', MainPage),
                              ('/blog', BlogPage),
                              ('/post', BlogPost),
                              ('/register',SignUp)],
                              debug=True)
