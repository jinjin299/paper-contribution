# coding:utf-8
import urllib2
import codecs
import threading
import os
import sys
import logging
from time import localtime, strftime, sleep
from mechanize import Browser
from analyzer import analyzer


class thread_bot(threading.Thread):
    def __init__(self, queue, out_queue, stat_queue, cj=None):
        threading.Thread.__init__(self)
        self.br = Browser()
        self.br.set_handle_robots(False)
        if cj:
            self.br._ua_handlers['_cookies'].cookiejar = cj
        self.queue = queue
        self.out_queue = out_queue
        self.stat_queue = stat_queue

    def run(self):
        try:
            ni, url = self.queue.get()
            anal = analyzer()
            self.br.open(url)
            self.nohigh()
            logging.debug("INSDIE LINK EXTRACT : # %s", str(ni))
            paper = anal.extract(self.data)
            self.out_queue.put(paper)
        except:
            self.save()
            self.stat_queue.put([sys.exc_info(), self.getName()])
        self.queue.task_done()

    def save(self):
        tstr = strftime("%y%m%d_%H:%M:%S", localtime())
        if not os.path.exists("pages/%s" % tstr[:6]):
            os.system("mkdir pages/%s" % tstr[:6])
        fd = codecs.open("pages/%s/%s_%s.html" % (tstr[:6], tstr, self.getName()), 'w', 'utf-8')
        fd.write(self.data)
        fd.close()

    def nohigh(self):
        self.url = self.br.geturl()
        self.data = self.br.response().get_data().decode('utf-8', 'strict')
        if "en_US.Server.IDLimit" in self.data:
            raise Exception("Server Error")
        if '<span class="hitHilite">' in self.data:
            datal = self.data.split('<span class="hitHilite">')
            for i in range(len(datal) - 1):
                data_str = "".join(datal[i+1].split('</span>',1))
                datal[i+1] = data_str
            self.data = "".join(datal)

class wos_bot(object):
    def __init__(self, t=None):
        if t == "korea":
            self.br = Browser()
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
        else:
            self.br = Browser()
            self.br.set_handle_robots(False)
            self.br.open("http://apps.webofknowledge.com")
            self.br.select_form("roaming")
            ID, PASS = open("id", 'r').read().split("\t")
            self.br['username'] = ID
            self.br['password'] = PASS
            self.br.submit()
            for link in self.br.links():
                if link.text == 'continue and establish a new session':
                    self.br.follow_link(link)
                    break

            for link in self.br.links():
                if link.text=="Web of ScienceTM Core Collection":
                    self.br.follow_link(link)
                    break

    def nohigh(self):
        self.url = self.br.geturl()
        self.data = self.br.response().get_data().decode('utf-8', 'strict')
        if "en_US.Server.IDLimit" in self.data:
            raise Exception("Server en_US.Server.IDLimit Error")

        if '<span class="hitHilite">' in self.data:
            datal = self.data.split('<span class="hitHilite">')
            for i in range(len(datal) - 1):
                data_str = "".join(datal[i+1].split('</span>',1))
                datal[i+1] = data_str
            self.data = "".join(datal)

    def get_url(self, url_type, paper=None):
        if (url_type == "paper"):
            link = paper.find('a', {'class' : 'smallV110'})
            if (link and
                    ("record.do?product=wos" in str(link).split("&", 2)[0].lower())):
                return self.parse_url(link.get('href'))
        else:
            ttxt = {"cite" : "View all of the articles that cite this one",
                    "ref" : "View this record’s bibliography",
                    "next" : "Next Page"}[url_type]
            for link in self.br.links():
                attrs = dict(link.attrs)
                if ('title' in attrs and attrs['title'] == ttxt):
                    return self.parse_url(link.url)
        return False

    def parse_url(self, url):
        if url.startswith("/"):
            base_url = "http://apps.webofknowledge.com"
        else:
            base_url = ""
        return base_url + url

    def back(self, n=1):
        for i in range(n-1):
            self.br.back()
        self.br.back()
        self.nohigh()

    def go_url(self, url):
        self.br.open(url)
        self.nohigh()

    def go_n(self, n):
        url = self.url
        tmp = url.split("doc=")
        tmp2 = tmp[1].split("&")
        tmp[1] = "&".join([str(n)] + tmp2[1:])
        url = "doc=".join(tmp)
        self.br.open(url)
        self.nohigh()

    def search(self, title, year=None):
        self.br.select_form("WOS_GeneralSearch_input_form")
        padding = ' NOT "(vol 76, pg 1796, 1996)" NOT "and its interactions with antibiotics"'
        self.br.form['value(input1)'] = '"' + title + '"' + padding
        self.br['value(select1)'] = ['TI']
        if year:
            self.br['period'] = ['Year Range']
            self.br['startYear'] = [year]
            self.br['endYear'] = [year]
        self.br.form.fixup()
        self.br.submit()
        self.nohigh()

    def save(self, s=''):
        tstr = strftime("%y%m%d_%H:%M:%S", localtime())
        if not os.path.exists("pages/%s" % tstr[:6]):
            os.system("mkdir pages/%s" % tstr[:6])
        fd = codecs.open("pages/%s/%s_%s.html" % (tstr[:6], tstr, s), 'w', 'utf-8')
        fd.write(self.data)
        fd.close()

    def cookiejar(self):
        return self.br._ua_handlers['_cookies'].cookiejar

# line width 79 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
