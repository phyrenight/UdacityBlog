import os

import jinja2
import webapp2

from google.appengine.ext import db
from models import BlogPost

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                autoescape=True)


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
            postBlog = BlogPost(title = title, post = rant)
            postBlog.put()
            self.redirect("/blogpost")


class BlogPage(Handler):
    def get(self):
        posts = db.GqlQuery("select * from BlogPost")
        self.render('blogpost.html', posts=posts)


app = webapp2.WSGIApplication([('/blog', MainPage),
                               ('/blogpost',BlogPage)],
                               debug=True)
