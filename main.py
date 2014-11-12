#!/usr/bin/env python
import logging
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot

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
    title, year = lst[1].split("  ")
    
    longging.info('START : %s', nobel)
    bot.search(title, year)

    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        logging.error('ROOT SEARCH : %s (%s)', title, nobel)
        return False

    bot.link(papers[0])
    droot = anal.extract(bot.data)
    bot.save()
    logging.debug("LEVEL 1 : %s", droot.title)
    if not bot.follow_cited():
        logging.info('No citation : %s', droot.title)
        return False
    
    # Cited papers of original paper
    papers = anal.list_papers(bot.data)
    bot.link(papers[0])
    while True:
        bot.save()
        logging.debug("LEVEL 2")
        url = bot.url
        paper = anal.extract(bot.data)
        if paper in pset:
            logging.debug("Aleardy Exist : %s", paper.title)
        else:
            # Weak equality test
            for pi in pset:
                if paper.weakeq(pi):
                    logging.debug("Weak Equality : %s", paper.title)
            pset.add(anal.extract(bot.data))

        if not bot.follow_ref():
            logging.info('No Reference : %s', paper.title)
        else: 
            while True:
                bot.save()
                logging.debug("LEVEL 3")
                papers = anal.list_papers(bot.data)
                n = 1
                for p in papers:
                    paper = anal.extract_c(p)
                    if paper:
                        n += 1
                        continue
                        # We can extract data with short section
                    logging.debug('Check Link : %s', str(n))
                    if not bot.link(p):
                        logging.debug('Access Error : %s', str(n))
                        return False
                    paper = anal.extract(bot.data)
                    bot.back()
                    # manipulate paper
                    n += 1
                else:
                    if not bot.next():
                        break
            bot.go_url(url)

        if not bot.next():
            logging.info('Crawling finished with %s', droot.title)
            break

    pfd = open(nobel + ".papers", 'w')
    efd = open(nobel + ".edge", 'w')


def main():
    """
    Initialize basic element and parse list of article 
    and run a function to crawl and extract paper data
    """
    logging.basicConfig(
        filename='log', level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)s\t%(message)s')
    fd = open("list",'r')
    logging.info('Open list file')

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
