# coding=utf=8
import re
import os
import string
import codecs
from datetime import datetime
from paper import paper4, paper5
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
        seasons = {'SPR':'MAR', 'SUM':'JUN', 'FAL':'SEP', 'WIN':'DEC'}
        months = ["%02d"% i for i in range(1,13)]

        d = dstr.replace('  ', ' ')
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
            if (any(x in ds[1] for x in string.lowercase)
                    or any(x in ds[1] for x in string.uppercase)):
                ds[1] = ds[1][:3]
                d = " ".join(ds)
                date = datetime.strptime(d, "%d %b %Y")
            elif (any(x in ds[0] for x in string.lowercase)
                    or any(x in ds[0] for x in string.uppercase)):
                ds[0] = ds[0][:3]
                d = " ".join(ds)
                date = datetime.strptime(d, "%b %d %Y")
            else:
                date = datetime.strptime(d, "%m %d %Y")
        return date

    def extract_c(self, paper):
        cont = paper.find('span', {'class' : 'reference-title'})
        pat = re.compile('(?<!Edited )By')
        if not cont:
            return False
        elif "Published:" not in paper.getText():
            return False

        div = cont
        title = div.getText(strip=True)

        if (div.nextSibling == None
                or div.nextSibling.nextSibling == None):
            div = div.parent
        
        if pat.search(paper.getText()):
            while div.nextSibling != None:
                if (type(div) != element.NavigableString
                        and pat.search(div.getText())):
                    break
                div = div.nextSibling
            atxt = div.getText(strip=True).split("By:")[1]
            if "et al." in atxt:
                return False
            authors = [x.strip() for x in atxt.split(";") if x.strip!='']
        else:
            authors = []

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

        if paper.find('a', {'class' : 'smallV110'}):
            return paper4(title, authors, date, True, ccnt)
        else:
            return paper4(title, authors, date, False, ccnt)


    def extract(self, data, tn=4):
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
        if tn == 4: 
            return paper4(title, authors, date, True, ccnt)
        elif tn == 5:
            pat = re.compile("(\d+?) Cited References")
            rcnt = int(pat.search(data).group(1))
            return paper5(title, authors, date, rcnt, ccnt)

    def str_to_bool(self, s):
        if s == 'True':
            return True
        else:
            return False

    def Check_data(self, nobel):
        # No Check
        root = "data/" + nobel
        if (not os.path.isfile(root + ".paper4")
                or not os.path.isfile(root + ".edges")):
            logging.info("DATA ARE NOT EXIST")
            return set(), 0, 0
        data = codecs.open(root + ".paper4", 'r', 'utf-8').read()
        edata = codecs.open(root + ".edges", 'r', 'utf-8').read()
        pset, eset = set(), set()
        cont = ""
        nmax = 0 
        pat = re.compile("\n\n(\d+?)\n\n(.+?\n{5})====", re.DOTALL)
        pat2 = re.compile(
                "TITLE\n(.+?)\n\nAUTHORS\n(.+?)\n\nDATE\n(.+?)\n\n"
                + "CCNT\n(\d+?)\n\nLINK\n(.+?)\n\nMD5\n(.+?)\n\n\n\n\n", re.DOTALL)
        # Parse existing data and eset pset
        for i in pat.finditer(data):
            ni = int(i.group(1))
            if ni > nmax:
                nmax = ni
                cont = i.group(2)
            for j in pat2.finditer(i.group()):
                title = j.group(1)
                authors = [x.strip() for x in j.group(2).split("\n")
                        if x.strip() != '']
                pdate = datetime.strptime(j.group(3), "%Y.%m.%d")
                ccnt = int(j.group(4))
                link = self.str_to_bool(j.group(5))
                md5 = j.group(6)
                pset.add(paper4(title, authors, pdate, link, ccnt))

        for i in pat.finditer(edata):
            for j in [x.strip() for x in i.group(2).split("\n") if x != '']:
                eset.add(j)

        return pset, eset, nmax
