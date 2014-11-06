import mechanize
import re
from bs4 import BeautifulSoup, element
from Levenshtein import distance

class wos_bot(object):
    def __init__(self);
        self.br = mechanize.Browser()
        self.br2 = mechanize.Browser()
        self.CITED = 0
        self.previous = ""

    def nohigh(self):
        self.data = self.resp.get_data()
        if '<span class="hitHilite">' in self.data:
            datal = self.data.split('<span class="hitHilite">')
            for i in range(len(datal)-1):
                data_str = "".join(datal[i+1].split('</span>',1))
                datal[i+1]=data_str
            self.data = "".join(datal)
    
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


    def search(self, title, year):
        self.br.open("http://apps.webofknowledge.com/")
        self.br.select_form("UA_GeneralSearch_input_form")
        padding = ' NOT "(vol 76, pg 1796, 1996)"'
        self.br.form['value(input1)'] = '"' + title + '"' + padding
        self.br['value(select1)'] = ['TI']
        self.br['period']=['Year Range']
        self.br['startYear'] = [year]
        sel.fbr['endYear'] = [year]
        self.br.form.fixup()
        self.resp = self.br.submit()
        self.nohigh()

    def list_papers(self):
        soup = BeautifulSoup(self.data, 'lxml')
        self.papers = soup.find_all('div',{'class':'search-results-item'})









fd = open("data/list2",'r')
for l in fd.readlines():
    s = l.split("\t")[1].split("  ")[0].strip()
    d = l.split("\t")[1].split("  ")[1].strip()
    br = mechanize.Browser()
    br.open("http://apps.webofknowledge.com")
    br.select_form("UA_GeneralSearch_input_form")
    br.form['value(input1)'] = '"'+s+'"'+' NOT "(vol 76, pg 1796, 1996)"'
    br['value(select1)'] = ['TI']
    br['period']=['Year Range']
    br['startYear'] = [d]
    br['endYear'] = [d]
    br.form.fixup()
    resp = br.submit()
    data = resp.get_data()
    n = 0
    for link in br.links():
        if 'full' in link.url:
            n+=1
    print n, l,
    s = BeautifulSoup(data,'lxml')
    for i in s.find_all('div',{'class':'search-results-content'}):
        for j in i.find_all('span',{'class':'label'}):
            if u"Published" in j.contents[0]:
                print re.search(r'\d{4}', j.next_sibling.contents[0].encode('utf-8')).group(0)
                break
# a = s.find(class="search-results-data-cite")
# print a.contents
# open("result.html",'w').write(data)
fd.close()

# aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
