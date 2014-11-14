import logging
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot

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

def Cite_or_ref(bot, anal, origin, sign, lv, pset, eset):
    sdict = {"R" : 'follow_ref', "C" : 'follow_cited'}
    lv = str(lv)
    fs = sdict[sign]
    url = bot.url
    if not getattr(wos_bot, fs)(bot):
        logging.debug("NOT %s : %s", sign, origin.title)
        return False
    else:
        n = 0
        while True:
            papers = anal.list_papers(bot.data)
            if len(papers) == 0:
                logging.debug("NOT %s 2 : %s", sign, origin.title)
                break
            bot.save()
            logging.debug("LEVEL %s-%s : # %s", lv, sign, str(n))
            for p in papers:
                n += 1
                logging.debug('EXTRACT : # %s', str(n))
                paper = anal.extract_c(p)
                if paper:
                    Add_paper(paper, pset)
                    if sign == "R":
                        Add_edge(paper, origin, eset)
                    else:
                        Add_edge(origin, paper, eset)
                    continue

                if not bot.link(p):
                    if "[not available]" not in p.getText(strip=True):
                        logging.error('ACCESS ERROR : %s', str(n))
                    continue
                bot.save()
                paper = anal.extract(bot.data)
                Add_paper(paper, pset)
                if sign == "R":
                    Add_edge(paper, origin, eset)
                else:
                    Add_edge(origin, paper, eset)
                bot.back()
            else:
                if not bot.next():
                    break
        bot.go_url(url)
    
def project(line):
    """
    With given line containing nobel, title,  and year,
    crawl given paper of bot, cited papers, and
    reference papers of cited papers.
    If the data is unavailable because of the license,
    the program will return False.
    """
    bot = wos_bot()
    anal = analyzer()
    pset, eset = set(), set()
    nobel, title, year = line.strip().split("\t")
    
    logging.info('START : %s', nobel)
    bot.search(title, year)

    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        logging.error('INVALID SEARCH INPUT: %s (%s)', title, nobel)
        return False

    bot.link(papers[0])
    bot.save()
    droot = anal.extract(bot.data)
    Add_paper(droot, pset)
    logging.debug("LEVEL 0 : %s", droot.title)

    Cite_or_ref(bot, anal, droot, "R", 1, pset, eset)

    if not bot.follow_cited():
        logging.error("NOT CITED : %s (%s)", title, nobel)
        return False
    
    papers = anal.list_papers(bot.data)
    if len(papers) == 0:
        logging.error("NOT CITED 2 : %s (%s)", title, nobel)
        return False
    bot.save()
    bot.link(papers[0])
    nc = 0
    while True:
        nc += 1
        logging.debug("LEVEL 1-C : %s / %s", str(nc), str(droot.ccnt))
        bot.save()
        paper1 = anal.extract(bot.data)
        Add_paper(paper1, pset)
        Add_edge(droot, paper1, eset)
        
        Cite_or_ref(bot, anal, paper1, "R", 2, pset, eset)
        Cite_or_ref(bot, anal, paper1, "C", 2, pset, eset)
        bot.save()

        if not bot.next():
            logging.info('FINISHED %s (%s)', droot.title, nobel)
            logging.info("#"*50)
            bot.save()
            break

    pfd = open("data/" + nobel + ".papers", 'w')
    for pi in pset:
        pfd.write(str(pi))
    pfd.close()
    efd = open("data/" + nobel + ".edges", 'w')
    for ei in eset:
        efd.write(ei+"\n")
    efd.close()


def main():
    """
    Initialize basic element and parse list of article 
    and run a function to crawl and extract paper data
    """
    logging.basicConfig(
        filename='log', level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)s\t%(message)s')
    logging.info("#"*30 + "PROGRAM START" + "#"*30)
    fd = open("list",'r')
    logging.info("READ LIST")

    for line in fd.readlines():
        if line.startswith("#"):
            continue
        project(line)

    fd.close()

def test():
    anal = analyzer()
    fd = open("pages/141114_11:35:17.html", 'r')
    papers = anal.list_papers(fd.read())
    n = 1
    for p in papers:
        print n,
        paper = anal.extract_c(p)
        n += 1

    fd.close()

if __name__ == '__main__':
    #test()
    main()
