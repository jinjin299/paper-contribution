# coding=utf=8
import datetime
from paper import paper4
from bs4 import BeautifulSoup, element

class analyzer(object):
    def __init__(self):

    def list_papers(self, br):
        soup = BeautifulSoup(br.data, 'lxml')
        return soup.find_all('div', {'class' : 'search-results-item'})

    def extract(self, br):
        authors = []
        seasons = {'SPR':'MAR','SUM':'JUN','FAL':'SEP','WIN':'DEC'}
        soup = BeautifulSoup(br.data, 'lxml')
        
        ccnt = int(soup.find('span', {'class' : 'TCcountFR'}).value)
        cont = soup.find('div', 'l-content')
        title = cont.find('div', 'title').value.content
        
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
                for p in p_field:
                    ptxt = p.getText(strip=True)
                    if ptxt.startswith("Published:"):
                        d = p.value.content
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
                    break

        return paper4(title, authors, date, ccnt)
