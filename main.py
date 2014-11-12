#!/usr/bin/env python
import logging
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot

def Add_paper(paper, pset):
    if paper in pset:
        logging.debug("STRONG EQUAL : %s", paper.title)
    else:
        for pi in pset:
            if paper.weakeq(pi):
                logging.debug("WEAK EQUAL : %s", paper.title)
        pset.add(paper)
    
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
    pset = set()
    eset = set()
    lst = line.strip().split("\t")
    nobel = lst[0]
    title, year = lst[1].split("  ")[:2]
    
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
    if not bot.follow_cited():
        logging.error("NOT CITED : %s (%s)", title, nobel)
        return False
    
    bot.save()
    papers = anal.list_papers(bot.data)
    bot.link(papers[0])
    nc = 0
    while True:
        nc += 1
        logging.debug("LEVEL 1 : %s / %s", str(nc), str(droot.ccnt))
        bot.save()
        url = bot.url
        paper = anal.extract(bot.data)
        Add_paper(paper, pset)

        if not bot.follow_ref():
            logging.debug('NOT REF : %s', paper.title)
        else: 
            n = 0
            while True:
                bot.save()
                logging.debug("LEVEL 2 : # %s", str(n))
                papers = anal.list_papers(bot.data)
                for p in papers:
                    n += 1
                    logging.debug('EXTRACT : # %s', str(n))
                    paper = anal.extract_c(p)
                    if paper:
                        Add_paper(paper, pset)
                        continue

                    if not bot.link(p):
                        logging.error('ACCESS ERROR : %s', str(n))
                        return False
                    paper = anal.extract(bot.data)
                    Add_paper(paper, pset)
                    bot.back()
                    # manipulate paper
                else:
                    if not bot.next():
                        break
            bot.go_url(url)

        if not bot.next():
            logging.info('Crawling finished with %s', droot.title)
            break
    #pfd = open(nobel + ".papers", 'w')
    #efd = open(nobel + ".edge", 'w')


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
    fd = open("pages/141111_19:30:10.html", 'r')
    papers = anal.list_papers(fd.read())
    n = 1
    for p in papers:
        print n,
        paper = anal.extract_c(p)
#        if not paper:
#            print 'Burst'
#        elif paper.title == 'Not Available':
#            print 'Not available'
#        else:
#            print 'Success'
        n += 1

    fd.close()

if __name__ == '__main__':
    #test()
    main()
