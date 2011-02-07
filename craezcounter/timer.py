from datetime import date, datetime, timedelta
from time import mktime


def tomorrow():
    return date.today() + timedelta(1)


def restsec():
    return mktime(tomorrow().timetuple()) - \
           mktime(datetime.now().timetuple())
