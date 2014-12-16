# coding=utf=8
import re
import os
import string
import codecs
import logging
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

        d = dstr.replace('  ', ' ').replace('- ', '-').replace(' -', '-').replace(',', '')
        ds = d.split(" ")
        if len(ds) == 1:
            if d.count("-") == 2:
                date = datetime.strptime(d, "%Y-%b-%d")
            elif "-" in d:
                ds = d.split("-")
                if (any(x in d for x in string.lowercase)
                        or any(x in d for x in string.uppercase)):
                    date = datetime.strptime(d, "%Y-%b")
                elif len(ds[1]) == 4:
                    date = datetime.strptime(ds[0], "%Y")
                else:
                    date = datetime.strptime(d, "%Y-%m")
            else:
                date = datetime.strptime(d, "%Y")
        elif len(ds) == 2:
            if "-" in d:
                d = d.split("-", 1)[0] + u" " + ds[1]
                ds = d.split(" ")

            if ds[0] in seasons:
                d = seasons[ds[0]] + u" " + ds[1]

            ds = d.split(" ")
            if ds[0] in months:
                date = datetime.strptime(d, "%m %Y")
            else:
                ds[0] = ds[0][:3]
                d = " ".join(ds)
                date = datetime.strptime(d, "%b %Y")
            
        elif len(ds) == 3:
            if (any(x in ds[1] for x in string.lowercase)
                    or any(x in ds[1] for x in string.uppercase)):
                ds[1] = ds[1][:3]
                if "-" in ds[0]:
                    ds[0] = ds[0].split("-")[0]
                d = " ".join(ds)
                date = datetime.strptime(d, "%d %b %Y")
            elif (any(x in ds[0] for x in string.lowercase)
                    or any(x in ds[0] for x in string.uppercase)):
                ds[0] = ds[0][:3]
                d = " ".join(ds)
                date = datetime.strptime(d, "%b %d %Y")
            else:
                date = datetime.strptime(d, "%m %d %Y")
        else:
            if "-" in d:
                ds2 = d.split("-")
                d = " ".join([ds2[0], ds[-1]])
            else:
                d = " ".join([ds[0], ds[1], ds[3]])
            date = datetime.strptime(d, "%d %b %Y")
        return date

    def stod2(self, d):
        bl = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        ms = None
        for i in bl:
            pat = re.compile(i, re.I)
            if pat.search(d):
                ms = i
                break
        pat = re.compile("\d{4}")
        year = pat.search(d).group()
        d = d.replace(year, '')
        pat = re.compile('[^\d](\d{1,2})[^\d]')
        ml = pat.findall(d)
        try:
            if ms:
                if len(ml) == 1:
                    ds = ml[0]
                    date = datetime.strptime(
                            "%s %s %s" % (year, ms, ds), "%Y %b %d")
                elif len(ml) == 0:
                    pat = re.compile('^(\d{1,2})[^\d]')
                    if pat.search(d):
                        ds = pat.search(d).group(1)
                        date = datetime.strptime(
                                "%s %s %s" % (year, ms, ds), "%Y %b %d")
                        return date
                    date = datetime.strptime(
                            "%s %s" % (year, ms), "%Y %b")
                else:
                    raise Exception("stod2 error")
            else:
                if len(ml) == 2:
                    ms = ml[0]
                    ds = ml[1]
                    date = datetime.strptime(
                            "%s %s %s" % (year, ms, ds), "%Y %m %d")
                elif len(ml) == 1:
                    ms = ml[0]
                    date = datetime.strptime(
                            "%s %s" % (year, ms), "%Y %m")
                elif len(ml) == 0:
                    date = datetime.strptime(year, "%Y")
                else:
                    raise Exception("stod2 error")
        except:
            return datetime.strptime(year, "%Y")
        return date

    def extract_c(self, paper):
        div = paper.find('span', {'class' : 'reference-title'})
        if (paper.find('a', {'class' : 'smallV110'})
                or (not div) or ("Published:" not in paper.getText())):
            return False

        pat = re.compile('(?<!Edited )By:')

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
            authors = [x.strip() for x in atxt.split("; ") 
                    if x.strip != '' or x.strip != 'et al']
        else:
            authors = []

        pat = re.compile('Published:')
        while div.nextSibling != None:
            if type(div) != element.NavigableString \
                and pat.search(div.getText()):
                break
            div = div.nextSibling
        d = div.getText(strip=True).split('Published:')[1].replace('.', '')
        d = d.split("(")[0].strip()
        try:
            date = self.stod(d)
        except:
            try:
                date = self.stod2(d)
            except:
                date = datetime.today()
            

        cont = paper.find('div', {'class' : 'search-results-data'})
        ccnt = int(cont.find('a').contents[0].replace(',', ''))
        return paper4(title, authors, date, False, ccnt)


    def extract(self, data, tn=4):
        authors = []
        soup = BeautifulSoup(data, 'lxml')
        ccnt = soup.find('span', {'class' : 'TCcountFR'})
        ccnt = int(ccnt.getText(strip=True).replace(',', ''))
        cont = soup.find('div', 'l-content')
        title = cont.find('div', 'title').value.contents[0].strip()
        
        for b in cont.find_all('div', 'block-record-info'):
            p_fields = b.find_all('p', 'FR_field')
            p_source = b.find('p' ,'sourceTitle')
           
            for p in p_fields:
                ptxt = p.getText(strip=True)
                if ptxt.startswith("By:"):
                    for i in ptxt[3:].split("; "):
                        if "Anonymous" in i:
                            continue
                        elif "(" in i:
                            name = i[i.index("(")+1:i.index(")")].strip()
                        else:
                            # No Parenthesis in name
                            raise Exception("Author name %s" % i)
                        authors.append(name)
                    break

            if p_source:
                for p in p_fields:
                    ptxt = p.getText(strip=True)
                    if ptxt.startswith("Published:"):
                        d = p.find('value').contents[0].replace('.', '')
                        try:
                            date = self.stod(d)
                        except:
                            date = self.stod2(d)
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

    def Check_data(self, nobel, root="data/"):
        # No Check
        root = root + nobel
        if (not os.path.isfile(root + ".paper4")
                or not os.path.isfile(root + ".edges")):
            logging.info("DATA ARE NOT EXIST")
            return 0, 0, set(), 1
        data = codecs.open(root + ".paper4", 'r', 'utf-8').read()
        edata = codecs.open(root + ".edges", 'r', 'utf-8').read()
        pset, eset, nset = set(), set(), set()
        nmax = 0 
        pat = re.compile("\n\n(\d+?)\n\n(.+?\n{5})====", re.DOTALL)
        pat2 = re.compile(
                "TITLE\n(.+?)\n\nAUTHORS\n(.+?)\n\nDATE\n(.+?)\n\n"
                + "CCNT\n(\d+?)\n\nLINK\n(.+?)\n\nMD5\n(.+?)\n\n\n\n\n", re.DOTALL)
        # Parse existing data and eset pset
        for i in pat.finditer(data):
            ni = int(i.group(1))
            nset = set()
            if ni > nmax:
                nmax = ni
            for j in pat2.finditer(i.group()):
                title = j.group(1)
                authors = [x.strip() for x in j.group(2).split("\n")
                        if x.strip() != '']
                pdate = datetime.strptime(j.group(3), "%Y.%m.%d")
                ccnt = int(j.group(4))
                link = self.str_to_bool(j.group(5))
                md5 = j.group(6)
                paper = paper4(title, authors, pdate, link, ccnt)
                pset.add(paper)
                nset.add(paper)

        for i in pat.finditer(edata):
            for j in [x.strip() for x in i.group(2).split("\n") if x != '']:
                eset.add(j)

        return pset, eset, nset, nmax
