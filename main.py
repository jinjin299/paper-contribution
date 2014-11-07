#!/usr/bin/env python
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot
#from bs4 import BeautifulSoup, element

def project(bot, anal):
    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        return False
    bot.link(papers[0])
    print anal.extract(bot.data)

    papers = anal.list_papers(bot.data)


def main():
    bot = wos_bot()
    anal = analyzer()
    fd = open("list",'r')
    for line in fd.readlines():
        lst = line.strip().split("\t")
        nobel = lst[0]
        title, year = lst[1].split("  ")
        bot.search(title, year)
        project(bot, anal)

    fd.close()

def test():
    anal = analyzer()
    fd = open("pages/141107_07:20:55.html",'r')
    print type(anal.extract(fd.read()))
    fd.close()

if __name__ == '__main__':
    test()
#    main()
