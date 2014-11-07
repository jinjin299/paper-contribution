# coding=utf-8
from datetime import date

class paper4(object):
    def __init__(self, title=u"", authors=[], pdate=date.today(), ccnt=0):
        self.title = title
        self.authors = authors
        self.pdate = pdate
        self.ccnt = ccnt

    def __str__(self):
        auth = u""
        for i in self.authors:
            auth += i + u"\n"

        tmp = u"TITLE\n%s\n\nAUTHORS\n%s\nDATE\n%s\n\nCOUNT\n%s\n\n\n\n\n"
        return tmp % (self.title, auth, self.pdate, self.ccnt)

