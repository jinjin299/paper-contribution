# coding=utf=8
import re
import string
from datetime import datetime
from paper import paper4
from bs4 import BeautifulSoup, element

class analyzer(object):
    def __init__(self):
        pass

    def list_papers(self, data):
        soup = BeautifulSoup(data, 'lxml')
        return soup.find_all('div', {'class' : 'search-results-item'})

    def stod(self, dstr):
        """
        From Given string of date, analyze the string
        """
        seasons = {'SPR':'MAR','SUM':'JUN','FAL':'SEP','WIN':'DEC'}
        months = ["%02d"% i for i in range(1,13)]

        d = dstr
        ds = d.split(" ")
        if len(ds) == 1:
            if "-" in d:
                date = datetime.strptime(d, "%Y-%m")
            else:
               date = datetime.strptime(d, "%Y")
        elif len(ds) == 2:
            if "-" in d:
                d = d.split("-", 1)[0] + u" " + ds[1]

            elif ds[0] in seasons:
                d = seasons[ds[0]] + u" " + ds[1]

            ds = d.split(" ")
            if ds[0] in months:
                date = datetime.strptime(d, "%m %Y")
            else:
                ds[0] = ds[0][:3]
                d = " ".join(ds)
                date = datetime.strptime(d, "%b %Y")
            
        else:
            if any(x in ds[1] for x in string.lowercase):
                ds[1] = ds[1][:3]
                d = " ".join(ds)
                date = datetime.strptime(d, "%d %b %Y")
            else:
                date = datetime.strptime(d, "%b %d %Y")
        date.strftime("%Y.%m.%d")

    def extract_c(self, paper):
        cont = paper.find('span', {'class' : 'reference-title'})
        if not cont:
            return False
        elif "Published:" not in paper.getText():
            return False

        div = cont
        title = div.getText(strip=True)

        if div.nextSibling == None:
            div = div.parent
        pat = re.compile('(?<!Edited )By')
        while div.nextSibling != None:
            if (type(div) != element.NavigableString
                    and pat.search9div.getText()):
                break
            div = div.nextSibling
        atxt = div.getText(strip=True).split("By:")[1]
        if "et al." in atxt:
            return False
        authors = [x.strip() for x in atxt.split(";") if x.strip!='']
        
        pat = re.compile('Published:')
        while div.nextSibling != None:
            if type(div) != element.NavigableString \
                and pat.search(div.getText()):
                break
            div = div.nextSibling
        d = div.getText(strip=True).split('Published:')[1].replace('.', '')
        date = self.stod(d)

        cont = paper.find('div', {'class' : 'search-results-data'})
        ccnt = int(cont.find('a').contents[0].replace(',', ''))

        return paper4(title, authors, date, ccnt)


    def extract(self, data):
        authors = []
        soup = BeautifulSoup(data, 'lxml')
        ccnt = soup.find('span', {'class' : 'TCcountFR'}).getText(strip=True)
        ccnt = int(ccnt.replace(',', ''))
        cont = soup.find('div', 'l-content')
        title = cont.find('div', 'title').value.contents[0].strip()
        
        for b in cont.find_all('div', 'block-record-info'):
            p_fields = b.find_all('p', 'FR_field')
            p_source = b.find('p' ,'sourceTitle')
           
            for p in p_fields:
                ptxt = p.getText(strip=True)
                if ptxt.startswith("By:"):
                    for i in ptxt[3:].split(";"):
                        if "(" in i:
                            name = i[i.index("(")+1:i.index(")")].strip()
                        else:
                            # No Parenthesis in name
                            print i #debug
                            exit(0)
                        authors.append(name)
                    break

            if p_source:
                for p in p_fields:
                    ptxt = p.getText(strip=True)
                    if ptxt.startswith("Published:"):
                        d = p.find('value').contents[0].replace('.', '')
                        date = self.stod(d)
                        break
        
        return paper4(title, authors, date, ccnt)
