#!/usr/bin/env python
import logging
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot
#from bs4 import BeautifulSoup, element

def project(bot, anal):
    pset = set()
    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        logging.info('The article is not single')
        return False

    bot.link(papers[0])
    droot = anal.extract(bot.data)
    fd.write(droot)
    if not bot.follow_cited():
        logging.info('No citation with %s', droot.title)
        break

    papers = anal.list_papers(bot.data)
    bot.link(papers[0])

    while True:
        url = bot.url
        paper = anal.extract(bot.data)
        if paper in pset:
            logging.debug("Aleardy Exist : %s", paper.title)
        else:
            pset.add(anal.extract(bot.data))

        if not bot.follow_ref():
            logging.info('No Reference')

        while True:
            papers = anal.list_papers(bot.data)
            for p in papers:
                paper = anal.extract_s(p)
                if paper:
                    # We can extract data with short section
                    break
                
                bot link(p)
                paper = anal.extract(bot.data)
                # manipulate paper
            else:
                if not bot.next():
                    break
        bot.go_url(url)
        if not bot.next():
            break




def main():
    logging.basicConfig(
        filename='main.log', level=logging.DEBUG,
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
    test()
#    main()
