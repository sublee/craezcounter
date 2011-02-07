from google.appengine.ext import db
from google.appengine.api import memcache
from craezcounter.timer import *


class Counter(db.Model):

    total = db.IntegerProperty(default=0)
    check_cookie = db.BooleanProperty(default=True)
    check_ip = db.BooleanProperty(default=False)

    def __init__(self, *args, **kwargs):
        super(Counter, self).__init__(*args, **kwargs)
        try:
            self.today = memcache.get(str(self.key())) or 0
        except db.NotSavedError:
            self.today = 0

    def put(self, *args, **kwargs):
        putted = super(Counter, self).put(*args, **kwargs)
        memcache.set(str(self.key()), self.today, restsec())
        return putted
