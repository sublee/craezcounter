import os.path
import hashlib
from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from craezcounter.models import *
from craezcounter.timer import *


DEMO_KEY = 'agxjcmFlemNvdW50ZXJyDgsSB0NvdW50ZXIY_goM'


class BaseHandler(webapp.RequestHandler):

    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

    def render_template(self, path, **context):
        if 'request' not in context:
            context['request'] = self.request
        path = os.path.join(self.TEMPLATE_DIR, path)
        self.response.out.write(template.render(path, context))


class OverviewHandler(BaseHandler):

    def get(self):
        self.render_template('index.html', key=DEMO_KEY)


class GenerationHandler(BaseHandler):

    def get(self):
        self.render_template('generate.html')

    def post(self):
        counter = Counter()
        counter.check_cookie = bool(self.request.get('check-cookie'))
        counter.check_ip = bool(self.request.get('check-ip'))
        counter.put()
        self.redirect('/dashboard/%s' % counter.key())


class DashboardHandler(BaseHandler):

    def get(self, key):
        counter = Counter.get(key)
        self.render_template('dashboard.html', key=key, counter=counter)


class JsonpHandler(BaseHandler):

    def get(self, key):
        counter = Counter.get(key)
        hit = True
        # check a cookie
        if counter.check_cookie:
            if self.request.cookies.get(key):
                hit = False
            else:
                self.set_cookie(key, 1, tomorrow())
        # check a memcache
        if counter.check_ip:
            key = '%s-%s' % (key, self.request.remote_addr)
            hashed_key = hashlib.sha1(key).hexdigest()
            if memcache.get(hashed_key):
                hit = False
            else:
                memcache.set(hashed_key, True, restsec())
        if hit:
            self.hit(counter)
        jsonp = self.request.get('callback')
        data = dict(total=counter.total, today=counter.today)
        self.response.out.write('%s(%s)' % (jsonp, simplejson.dumps(data)))

    def set_cookie(self, name, value, expires=None):
        body = '%s=%s' % (name, value)
        if expires:
            body += '; expires=%s' % expires.strftime('%a, %d-%b-%Y %T')
        self.response.headers.add_header('Set-Cookie', body)

    def hit(self, counter):
        counter.today += 1
        counter.total += 1
        counter.put()
        return counter


class EmbedScriptHandler(BaseHandler):

    def get(self, key):
        width = self.request.get('width', '100%')
        self.response.headers.add_header('Content-Type', 'text/javascript')
        self.render_template('embed.js', key=key, width=width)


class EmbeddedHandler(BaseHandler):

    def get(self, key):
        self.render_template('embed.html', key=key)


app = webapp.WSGIApplication([
    ('/', OverviewHandler),
    ('/generate', GenerationHandler),
    ('/dashboard/(.+)', DashboardHandler),
    ('/(.+)/embed\.js', EmbedScriptHandler),
    ('/(.+)/embed', EmbeddedHandler),
    ('/(.+)/jsonp', JsonpHandler),
])
