# coding=utf-8
from datetime import date
import md5

class paper4(object):
    def __init__(
            self, title=u"", authors=[], pdate=date.today(),
            link=False, ccnt=0):
        self.title = title
        self.authors = authors
        self.pdate = pdate
        self.ccnt = ccnt
        self.link = link
        self.set_md5()

    def dtos(self):
        pdate = self.pdate
        if pdate.year < 1900:
            year = pdate.year
            mon = pdate.month
            day = pdate.day
            return "%d.%02d.%02d" % (year, mon, day)
        return pdate.strftime("%Y.%m.%d")

    def set_md5(self):
        auth = "\n".join(self.authors)
        tmp = u"TITLE\n%s\n\nAUTHORS\n%s\n\nDATE\n%s\n\nLINK\n%s"
        tmps = tmp % (self.title, auth, self.dtos(), self.link)
        self.md5 = md5.new(tmps.encode('utf-8')).hexdigest()

    def __unicode__(self):
        auth = "\n".join(self.authors)
        tmp = u"TITLE\n%s\n\nAUTHORS\n%s\n\nDATE\n%s" \
                + "\n\nCCNT\n%s\n\nLINK\n%s\n\nMD5\n%s"
        tmps = tmp % (
                self.title, auth, self.dtos(), self.ccnt,
                self.link, self.md5) + "\n\n\n\n\n"
        return tmps
    
    def weakeq(self, paper):
        return (isinstance(paper, self.__class__)
                and self.title == paper.title)

    def __hash__(self):
        return self.md5.__hash__()

    def __eq__(self, paper):
        return (isinstance(paper, self.__class__)
                and self.md5 == paper.md5)
    
    
class paper5(object):
    def __init__(
            self, title=u"", authors=[], pdate=date.today(), rcnt=0, ccnt=0):
        self.title = title
        self.authors = authors
        self.pdate = pdate
        self.rcnt = rcnt
        self.ccnt = ccnt

    def __str__(self):
        auth = u""
        for i in self.authors:
            auth += i + u"\n"

        tmp =(u"TITLE\n%s\n\nAUTHORS\n%s\nDATE\n%s\n\n"
                + "RCNT\n%s\n\nCCNT\n%s\n\n\n\n\n")
        return tmp % (self.title, auth, self.pdate, self.rcnt, self.ccnt)
    
    def weakeq(self, paper):
        return (isinstance(paper, self.__class__) and self.title == paper.title)

    def __eq__(self, paper):
        a = dict(self.__dict__)
        b = dict(paper.__dict__)
        del a['ccnt']
        del b['ccnt']
        return (isinstance(paper, self.__class__) and a == b)
