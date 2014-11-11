#!/usr/bin/env python
import logging
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot

def project(bot, anal):
    """
    Crawl given paper of bot, cited papers, and
    reference papers of cited papers.
    If the data is unavailable because of the license,
    the program will return False.
    """

    pset = set()
    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        logging.info('Search Error')
        return False

    bot.link(papers[0])
    droot = anal.extract(bot.data)
    bot.save()
    logging.debug("LEVEL 1")
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
                for p in papers:
                    paper = anal.extract_s(p)
                    if paper:
                        pass

                        # We can extract data with short section
                    if not bot.link(p):
                        logging.debug('Access Error')
                        return False
                    paper = anal.extract(bot.data)
                    # manipulate paper
                else:
                    if not bot.next():
                        break
            bot.go_url(url)

        if not bot.next():
            logging.info('Crawling finished with %s', droot.title)
            break



def main():
    """
    Initialize basic element and parse list of article 
    and run a function to crawl and extract paper data
    """
    logging.basicConfig(
        filename='log', level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)s\t%(message)s')
    bot = wos_bot()
    anal = analyzer()
    fd = open("list",'r')
    logging.info('Open list file')

    for line in fd.readlines():
        lst = line.strip().split("\t")
        nobel = lst[0]
        title, year = lst[1].split("  ")
        logging.info('Start searching')
        bot.search(title, year)
        project(bot, anal)

    fd.close()

def test():
    anal = analyzer()
    fd = open("pages/141107_07:07:36.html",'r')
    papers = anal.list_papers(fd.read())
    print anal.extract_s(papers[0])
    fd.close()

if __name__ == '__main__':
    #test()
    main()
