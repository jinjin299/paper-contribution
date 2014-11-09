#!/usr/bin/env python
import logging
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot
#from bs4 import BeautifulSoup, element

def project(bot, anal):
    plist = []
    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        logging.info('The article is not single')
        return False

    bot.link(papers[0])
    droot = anal.extract(bot.data)
    fd.write(droot)
    if bot.follow_cited():
        papers = anal.list_papers(bot.data)
        for p in papers:
            bot.link(p)
            data = anal.extract(bot.data)
            fd.write(data)
            if bot.follow_ref():
                while True:
                    papers2 = anal.list_papers(bot.data)
                    for p2 in papers2:
                        bot.link(p2)
                        data = anal.extract(bot.data)
                        fd.write(data)
                        bot.back()
                    else:
                        if not bot.next():
                            break
            else:
                print 1
        else:
            print 1
    else:
        print 1
    papers = anal.list_papers(bot.data)


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
    fd = open("pages/141107_07:05:05.html",'r')
    print anal.extract_s(fd.read())
    fd.close()

if __name__ == '__main__':
    test()
#    main()
