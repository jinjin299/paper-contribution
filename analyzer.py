# coding=utf=8
from datetime import datetime
from paper import paper4
from bs4 import BeautifulSoup, element

class analyzer(object):
    def __init__(self):
        pass

    def list_papers(self, data):
        soup = BeautifulSoup(data, 'lxml')
        return soup.find_all('div', {'class' : 'search-results-item'})

    def extract_s(self, paper):
        cont = paper.find('div', {'class' : 'search-results-content'})
        for div in cont.find_all('div'):
            print div
        print 123
        
        cont = paper.find('div', {'class' : 'search-results-data'})
        print cont.find('a').contents[0].strip()


    def extract(self, data):
        authors = []
        seasons = {'SPR':'MAR','SUM':'JUN','FAL':'SEP','WIN':'DEC'}
        soup = BeautifulSoup(data, 'lxml')
        ccnt = soup.find('span', {'class' : 'TCcountFR'}).getText(strip=True)
        ccnt = int(ccnt)
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
                        d = p.find('value').contents[0]
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

                            date = datetime.strptime(d, "%b %Y")
                        else:
                            date = datetime.strptime(d, "%b %d %Y")
                        date = date.strftime("%Y.%m.%d")
                        break

        
        return paper4(title, authors, date, ccnt)
