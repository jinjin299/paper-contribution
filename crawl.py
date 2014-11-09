# coding:utf-8
import mechanize
from time import localtime, strftime

class wos_bot(object):
    def __init__(self):
        self.br = mechanize.Browser()

    def nohigh(self):
        self.data = self.resp.get_data()
        if '<span class="hitHilite">' in self.data:
            datal = self.data.split('<span class="hitHilite">')
            for i in range(len(datal) - 1):
                data_str = "".join(datal[i+1].split('</span>',1))
                datal[i+1] = data_str
            self.data = "".join(datal)

    def link(self, paper):
        link = paper.find('a', {'class' : 'smallV110'})
        if link:
            self.resp = self.br.follow_link(url=link.get('href'))
            self.nohigh()
            return True
        else:
            return False

    
    def follow_cited(self):
        for link in self.br.links():
            attrs = dict(link.attrs)
            if 'title' in attrs and attrs['title'] == \
                    "View all of the articles that cite this one":
                self.resp = self.br.follow_link(link)
                self.nohigh()
                return True

        else:
            return False

    def follow_ref(self):
        for link in self.br.links():
            attrs = dict(link.attrs)
            if 'title' in attrs and  attrs['title'] == \
                    "View this record’s bibliography":
                self.resp = self.br.follow_link(link)
                self.nohigh()
                return True
        else:
            return False

    def back(self, n=1):
        for i in range(n-1):
            self.br.back()
        self.resp = self.br.back()
        self.nohigh()

    def next(self):
        for link in self.br.links():
            attrs = dict(link.attrs)
            if 'title' in attrs and attrs['title']=='Next Page':
                self.resp = self.br.follow_link(link)
                self.nohigh()
                return True
        return False
        


    def search(self, title, year):
        self.br.open("http://apps.webofknowledge.com/")
        self.br.select_form("UA_GeneralSearch_input_form")
        padding = ' NOT "(vol 76, pg 1796, 1996)"'
        self.br.form['value(input1)'] = '"' + title + '"' + padding
        self.br['value(select1)'] = ['TI']
        self.br['period'] = ['Year Range']
        self.br['startYear'] = [year]
        self.br['endYear'] = [year]
        self.br.form.fixup()
        self.resp = self.br.submit()
        self.nohigh()

    def save(self):
        tstr = strftime("%y%m%d_%H:%M:%S", localtime())
        fd = open("pages/" + tstr + ".html", 'w')
        #fd = codecs.open("pages/" + tstr + ".html", 'w', 'utf-8')
        fd.write(self.data)
        fd.close()


# line width 79 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
