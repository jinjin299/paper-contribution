import logging
import re
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot
from time import sleep

def init():
    logging.basicConfig(
        filename='log', level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)s\t%(message)s')
    logging.info("#"*30 + "PROGRAM START" + "#"*30)


def Add_paper(paper, pset):
    for pi in pset:
        if paper == pi:
            logging.debug("STRONG EQUAL : %s", paper.title)
            return False
        elif paper.__eq__(pi):
            logging.debug("SSTRONG EQUAL : %s", paper.title)
            return False
        elif paper.weakeq(pi):
            fd = open("weak", 'a')
            fd.write(str(pi))
            fd.write(str(paper))
            fd.write("="*50)
            fd.close()
            logging.debug("WEAK EQUAL : %s", paper.title)
    pset.add(paper)

def Add_edge(p1, p2, eset):
    eset.add(p1.title + "\t" + p2.title)

def Add_pe(origin, paper, sign, pset, eset):
    Add_paper(paper, pset)
    if sign == "R":
        Add_edge(paper, origin, eset)
    else:
        Add_edge(origin, paper, eset)

def Cite_or_ref(bot, anal, origin, lv, sign, url, pset, eset):
    if not url:
        logging.debug("NOT %s : %s", sign, origin.title)
        return False

    n = 0
    lv = str(lv)

    bot.go_url(url)
    while True:
        bot.save()
        papers = anal.list_papers(bot.data)
        if len(papers) == 0:
            logging.debug("NOT %s 2 : %s", sign, origin.title)
            return False
        
        nurl = bot.get_url("next")
        if sign == "C":
            logging.debug("LEVEL %s-C : # %s / %s", lv, str(n), origin.ccnt)
        else:
            logging.debug("LEVEL %s-R : # %s", lv, str(n))

        ldict = {}
        for p in papers:
            n += 1
            paper = anal.extract_c(p)
            if paper:
                logging.debug("IN PAGE EXTRACT : # %s", str(n))
                Add_paper(paper, pset)
                Add_pe(origin, paper, sign, pset, eset)
                continue

            logging.debug("IN PAGE FAIL : # %s", str(n))
            purl = bot.get_url("paper", p)
            if ("[not available]" not in p.getText(strip=True)
                   and not purl):
                logging.error('ACCESS ERROR : %s', str(n))
                continue
            ldict[n] = purl

        for ni in ldict:
            bot.go_url(ldict[ni])
            bot.save()

            paper = anal.extract(bot.data)
            logging.debug("INSDIE LINK EXTRACT : # %s", str(ni))
            Add_pe(origin, paper, sign, pset, eset)
    
        if not nurl:
            break
        bot.go_url(nurl)
    
def project(line):
    """
    With given line containing nobel, title,  and year,
    crawl given paper of bot, cited papers, and
    reference papers of cited papers.
    If the data is unavailable because of the license,
    the program will return False.
    """
    # Project Initialize
    bot = wos_bot()
    anal = analyzer()
    pset, eset = set(), set()
    nobel, title, year = line.strip().split("\t")

    logging.info('START : %s (%s)', title, nobel)
    bot.search(title, year)

    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        logging.error('INVALID SEARCH INPUT: %s (%s)', title, nobel)
        return False

    bot.go_url(bot.get_url("paper", papers[0]))
    bot.save()

    droot = anal.extract(bot.data)
    logging.debug("LEVEL 0 : %s", droot.title)
    curl = bot.get_url("cite")
    rurl = bot.get_url("ref")

    if not curl:
        logging.error("NOT CITED : %s (%s)", title, nobel)
        return False
    bot.get_url(curl)
    bot.save()
    papers = anal.list_papers(bot.data)
    if len(papers) == 0:
        logging.error("NOT CITED 2 : %s (%s)", title, nobel)
        return False

    bot.go_url(bot.get_url("paper", papers[0]))
    url = bot.url
    
    # Check Previous Data
    logging.info("CHECK PREVIOUS DATA")
    pfd = open("data/" + nobel + ".paper4", 'r')
    data = pfd.read()
    pfd.close()
    tmps = set()
    cont = ""
    nmax = 0 
    pat = re.compile("\n\n(\d+?)\n\n(.+?\n{4})==", re.DOTALL)
    for i in pat.finditer(data):
        ni = int(i.group(1))
        if ni > nmax:
            nmax = ni
            cont = i.group(2)
    pat = re.compile("TITLE\n(.+?)\n\n")
    for i in pat.finditer(cont):
        tmps.add(i.group(1))
    bot.go_n(nmax)
    tmp = anal.extract(bot.data)
    tmps = set()

    if tmp.title in tmps:
    # Continue previous result
        nc = nmax
        logging.info('RESTART : %s with last record # %s', nobel, str(nc))
        pat = re.compile("\n\n(\d+?)\n\n(.+?\n{4})==", re.DOTALL)
        pat2 = re.compile("TITLE\n(.+?)\n\n")
        for i in pat.finditer(data):
            break

        # Parse existing data and eset pset

        nurl = bot.get_url("next")
        if not nurl:
            logging.info('FINISHED %s (%s)', droot.title, nobel)
            logging.info("#"*50)
            return True
        else:
            bot.go_url(nurl)
            # Check Error on next paper page
            # If there is an error we should break 
    else:
    # Previosu data
        logging.info('INITIAL START : %s', nobel)
        nc = 0
        Add_paper(droot, pset)
        Cite_or_ref(bot, anal, droot, "R", 1, rurl, pset, eset)
        bot.go_url(url)

    while True:
        nc += 1
        logging.debug("LEVEL 1-C : %s / %s", str(nc), str(droot.ccnt))
        bot.save()
        paper1 = anal.extract(bot.data)

        Add_pe(droot, paper1, "C", pset, eset)
        
        # Get Links
        curl = bot.get_url("cite")
        rurl = bot.get_url("ref")
        nurl = bot.get_url("next")
                
        # Go to the list 
        Cite_or_ref(bot, anal, paper1, "R", 2, rurl, pset, eset)
        Cite_or_ref(bot, anal, paper1, "C", 2, curl, pset, eset)
        bot.save()

        # Go to the next paper page
        if not nurl:
            logging.info('FINISHED %s (%s)', droot.title, nobel)
            logging.info("#"*50)
            break
        else:
            bot.go_url(nurl)
            # Check Error on next paper page
            # If there is an error we should break 

    pfd = open("data/" + nobel + ".paper4", 'w')
    for pi in pset:
        pfd.write(str(pi))
    pfd.close()
    efd = open("data/" + nobel + ".edges", 'w')
    for ei in eset:
        efd.write(ei + "\n")
    efd.close()
    return True


def main():
    """
    Initialize basic element and parse list of article 
    and run a function to crawl and extract paper data
    """
    init()
    
    logging.info("READ LIST")

    for line in open("list", 'r').readlines():
        if line.startswith("#"):
            continue
        while True:
            try:
                project(line)
            except:
                sleep(1)
                pass
            else:
                break

def test():
    anal = analyzer()
    fd = open("pages/141114_14:02:41.html", 'r')
    papers = anal.list_papers(fd.read())
    n = 1
    pfd = open("data/test.pages", 'w')
    pset = set()
    for p in papers:
        print n,
        paper = anal.extract_c(p)
        if paper:
            pset.add(paper)
        n += 1
    pfd.write("==\n\n1\n\n")
    for pi in pset:
        pfd.write(str(pi))
    pfd.write("==\n\n2\n\n")
    for pi in pset:
        pfd.write(str(pi))

    fd.close()
    pfd.close()

def test2():
    pfd = open("data/test.pages", 'r')
    pat = re.compile("\n\n(\d+?)\n\n(?P<CONT>.+?\n{4})==", re.DOTALL)
    data = pfd.read()
    for i in pat.finditer(data):
        print i.group(1)
        cont = i.group(2)

    pat = re.compile("TITLE\n(.+?)\n\n")
    for i in pat.finditer(cont):
        print i.group(1)

def test3():
    fd = open("pages/141114_23:06:59.html", 'r')
    anal = analyzer()
    print str(anal.extract(fd.read(), 5))
    fd.close()

if __name__ == '__main__':
    #test()
    #test2()
    main()
