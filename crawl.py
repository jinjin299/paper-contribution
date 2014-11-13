# coding:utf-8
import mechanize
import urllib2
from time import localtime, strftime, sleep

class wos_bot(object):
    def __init__(self):
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.open("http://medlib.korea.ac.kr/login")
        self.br.select_form('login')
        ID, PASS = open("id",'r').read().split("\t")
        self.br['id'] = ID
        self.br['password'] = PASS
        self.br['loginType']=['2']
        self.br.form.fixup()
        self.br.submit()
        self.br.open("http://apps.webofknowledge.com.ocam.korea.ac.kr")
        self.br.select_form(nr=0)
        self.br.submit()
        self.br.open("http://medlib.korea.ac.kr/proxy/userinfo?returnurl=http%3A%2F%2Fapps%2Ewebofknowledge%2Ecom%2Eocam%2Ekorea%2Eac%2Ekr%2F")
        self.br.select_form(nr=0)
        self.br.submit()
        self.br.select_form(nr=0)
        self.br.submit()
        for link in self.br.links():
            if link.text=="Web of ScienceTM Core Collection":
                self.br.follow_link(link)
                break

    def nohigh(self):
        self.url = self.br.geturl()
        self.data = self.br.response().get_data()
        if '<span class="hitHilite">' in self.data:
            datal = self.data.split('<span class="hitHilite">')
            for i in range(len(datal) - 1):
                data_str = "".join(datal[i+1].split('</span>',1))
                datal[i+1] = data_str
            self.data = "".join(datal)

    def link(self, paper):
        link = paper.find('a', {'class' : 'smallV110'})
        if link:
            self.br.follow_link(url=link.get('href'))
            self.nohigh()
            return True
        else:
            return False

    
    def follow_cited(self):
        for link in self.br.links():
            attrs = dict(link.attrs)
            if 'title' in attrs and attrs['title'] == \
                    "View all of the articles that cite this one":
                self.br.follow_link(link)
                self.nohigh()
                return True

        else:
            return False

    def follow_ref(self):
        for link in self.br.links():
            attrs = dict(link.attrs)
            if 'title' in attrs and  attrs['title'] == \
                    "View this record’s bibliography":
                self.br.follow_link(link)
                self.nohigh()
                return True
        else:
            return False

    def back(self, n=1):
        for i in range(n-1):
            self.br.back()
        self.br.back()
        self.nohigh()

    def next(self):
        for link in self.br.links():
            attrs = dict(link.attrs)
            if 'title' in attrs and attrs['title']=='Next Page':
                self.br.follow_link(link)
                self.nohigh()
                return True
        return False

    def go_url(self, url):
        self.br.open(url)
        self.nohigh()

    def search(self, title, year):
        self.br.select_form("WOS_GeneralSearch_input_form")
        padding = ' NOT "(vol 76, pg 1796, 1996)"'
        self.br.form['value(input1)'] = '"' + title + '"' + padding
        self.br['value(select1)'] = ['TI']
        self.br['period'] = ['Year Range']
        self.br['startYear'] = [year]
        self.br['endYear'] = [year]
        self.br.form.fixup()
        self.br.submit()
        self.nohigh()

    def save(self):
        tstr = strftime("%y%m%d_%H:%M:%S", localtime())
        fd = open("pages/" + tstr + ".html", 'w')
        #fd = codecs.open("pages/" + tstr + ".html", 'w', 'utf-8')
        fd.write(self.data)
        fd.close()

# line width 79 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
