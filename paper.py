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

        tmp =(u"TITLE\n%s\n\nAUTHORS\n%s\nDATE\n%s\n\nCCNT\n%s\n\n\n\n\n")
        return tmp % (self.title, auth, self.pdate, self.ccnt)
    
    def weakeq(self, paper):
        return (isinstance(paper, self.__class__) and self.title == paper.title)

    def __eq__(self, paper):
        a = dict(self.__dict__)
        b = dict(paper.__dict__)
        del a['ccnt']
        del b['ccnt']
        return (isinstance(paper, self.__class__) and a == b)


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
