from google.appengine.ext.webapp.util import run_wsgi_app
from craezcounter import app as application


if __name__ == '__main__':
    run_wsgi_app(application)
