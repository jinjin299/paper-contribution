import logging
import re
import codecs
import Queue
import sys
import traceback
from analyzer import analyzer
from paper import paper4
from crawl import wos_bot, thread_bot
from time import sleep


def Add_paper(paper, pset):
    if paper.pdate == None:
        logging.warning("Paper Date is None %s", paper.title)
        raise Exception("Date is None")
    for pi in pset:
        if paper == pi:
            logging.debug("STRONG EQUAL : %s", paper.title)
            return False
        elif paper.weakeq(pi):
            fd = codecs.open("weak", 'a', 'utf-8')
            fd.write(unicode(pi))
            fd.write(unicode(paper))
            fd.write("="*50 + "\n")
            fd.close()
            logging.debug("WEAK EQUAL : %s", paper.title)
    pset.add(paper)

def Add_edge(p1, p2, eset):
    eset.add(p1.md5 + "\t" + p2.md5)

def Add_pe(origin, paper, sign, pset, eset):
    Add_paper(paper, pset)
    if sign == "R":
        Add_edge(paper, origin, eset)
    else:
        Add_edge(origin, paper, eset)

def write_data(nobel, nc, piset, eiset, mode='a'):
    pfd = codecs.open("data/" + nobel + ".paper4", mode, "utf-8")
    pfd.write("\n\n%d\n\n" % nc)
    for pi in piset:
        pfd.write(unicode(pi))
    pfd.write("====")
    pfd.close()

    efd = codecs.open("data/" + nobel + ".edges", mode, "utf-8")
    efd.write("\n\n%d\n\n" % nc)
    for ei in eiset:
        efd.write(ei + "\n")
    efd.write("\n\n\n\n\n====")
    efd.close()


def Cite_or_ref(bot, anal, origin, lv, sign, url, pset, eset, recur=None):
    rdict = {"R" : "ref", "C" : "cite"}
    if not url:
        logging.debug("NOT %s : %s", sign, origin.title)
        return False

    n = 0
    lv = str(lv)

    bot.go_url(url)
    while True:
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

        if not recur:
            for p in papers:
                n += 1
                paper = anal.extract_c(p)
                if paper:
                    logging.debug("IN PAGE EXTRACT : # %s", str(n))
                    Add_pe(origin, paper, sign, pset, eset)
                    continue

                logging.debug("IN PAGE FAIL : # %s", str(n))
                purl = bot.get_url("paper", p)
                if "arXiv" in p.getText():
                    logging.warning("arXiv DATA")
                if "[not available]" in p.getText(strip=True):
                    continue
                elif not purl:
                    logging.error('ACCESS ERROR : %s', str(n))
                    continue
                ldict[n] = purl

            queue = Queue.Queue()
            out_queue = Queue.Queue()
            stat_queue = Queue.Queue()
            tl = []
            cj = bot.cookiejar()
            for i in range(len(ldict)):
                tl.append(thread_bot(queue, out_queue, stat_queue, cj))
                tl[-1].setDaemon(True)
                tl[-1].start()

            for i in [(x, ldict[x]) for x in ldict]:
                queue.put(i)

            queue.join()
            try:
                exc = stat_queue.get(block=False)
            except Queue.Empty:
                pass
            else:
                exc_type, exc_obj, exc_trace = exc[0]
                print exc_type
                print exc_obj
                traceback.print_tb(exc_trace)
                print exc[1]
                raise Exception("ERROR")
            logging.debug("Thread_bot finished")
            for i in range(len(ldict)):
                paper = out_queue.get()
                Add_pe(origin, paper, sign, pset, eset)

        else:
            for p in papers:
                n += 1
                purl = bot.get_url("paper", p)
                if purl:
                    ldict[n] = purl
                    continue
                else:
                    paper = anal.extract_c(p)
                    if paper:
                        logging.debug("IN PAGE EXTRACT : # %s", str(n))
                        Add_pe(origin, paper, sign, pset, eset)
                    else:
                        logging.error('ACCESS ERROR : %s', str(n))

            for ni in ldict:
                bot.go_url(ldict[ni])
                paper = anal.extract(bot.data)
                logging.debug("INSDIE LINK EXTRACT : # %s", str(ni))
                Add_pe(origin, paper, sign, pset, eset)
                if recur:
                    logging.debug("START RECURSION : # %s", str(ni))
                    rurl = bot.get_url(rdict[recur])
                    Cite_or_ref(bot, anal, paper, 0,
                                recur, rurl, pset, eset)
    
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
    nobel, title, year = line.strip().split("\t")
    logging.info("#" * 50) 
    logging.info('START : %s\t%s', nobel)
    bot.search(title, year)
    logging.info('SEARCH : %s\t%s', title, year)

    papers = anal.list_papers(bot.data)
    if len(papers) != 1:
        logging.error('INVALID SEARCH : %s (%s) NUM :# %s', title, nobel, str(len(papers)))
        bot.save("INVALID_SEARCH")
        return False

    bot.go_url(bot.get_url("paper", papers[0]))
    bot.save("ORIGIN_PAPER")

    droot = anal.extract(bot.data)
    curl = bot.get_url("cite")
    rurl = bot.get_url("ref")
    logging.debug("LEVEL 1 : %s", droot.title)

    if not curl:
        logging.error("NOT CITED : NO URL : %s (%s)", title, nobel)
        return False

    bot.go_url(curl)
    bot.save()
    papers = anal.list_papers(bot.data)
    if len(papers) == 0:
        logging.error("NOT CITED : FALSE CITED : %s (%s)", title, nobel)
        return False

    bot.go_url(bot.get_url("paper", papers[0]))
    curl = bot.br.geturl()
    
    # Check Previous Data
    logging.info("CHECK PREVIOUS DATA")
    pset, eset, nset, nmax = anal.Check_data(nobel)
    """
    pset : set of papers
    eset : set of edges
    nmax : maximum 2-C
    """
    bot.go_n(nmax)
    
    paper = anal.extract(bot.data)
    if paper in nset:
    # Continue previous result
        nc = nmax
        logging.info('RESTART : %s with last record # %s', nobel, str(nc))

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
    # First Start
        logging.info('INITIAL START : %s', nobel)
        nc = 0
        pset, eset = set(), set()

        Add_paper(droot, pset)
        Cite_or_ref(bot, anal, droot, 0, "R", rurl, pset, eset)
        write_data(nobel, 0, pset, eset, "w")
        bot.go_url(curl)

    del nset
    while True:
        nc += 1
        logging.info("LEVEL 2-C : %s / %s", str(nc), str(droot.ccnt))
        pset, eset = set(), set()
        paper1 = anal.extract(bot.data)
        if not paper1:
            logging.info("INVALID NEXT")
            break

        Add_pe(droot, paper1, "C", pset, eset)
        
        # Get Links
        curl = bot.get_url("cite")
        rurl = bot.get_url("ref")
        nurl = bot.get_url("next")
                
        # Go to the list 
        Cite_or_ref(bot, anal, paper1, 1,
                    "R", rurl, pset, eset)
        Cite_or_ref(bot, anal, paper1, 3, "C", curl, pset, eset)
        write_data(nobel, nc, pset, eset)

        # Go to the next paper page
        if not nurl:
            logging.info("END OF LIST")
            break
        else:
            bot.go_url(nurl)
            # Check Error on next paper page
            # If there is an error we should break 

    logging.info('FINISHED %s (%s)', droot.title, nobel)
    logging.info("#"*50)
    return True


def init():
    logging.basicConfig(
        filename='log', level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)s\t%(message)s')
    for i in range(3):
        logging.info("#" * 50)
    logging.info("PROGRAM INITILIZATION")

def main():
    """
    Initialize basic element and parse list of article 
    and run a function to crawl and extract paper data
    """
    init()
    logging.info("READ LIST FILE")
    logging.info("READ LIST")
    for line in open("list", 'r').readlines():
        if line.startswith("#"):
            logging.info("IGNORE : %s", line.strip())
            continue

        while True:
            try:
                if not project(line):
                    logging.error("#" * 50)
                    logging.error("PROGRAM FALSE RESULT")
            except:
                exc = sys.exc_info()
                exc_type, exc_obj, exc_trace = exc
                print exc_type
                print exc_obj
                traceback.print_tb(exc_trace)
                logging.error("PROGRAM ERROR")
                sleep(3)
            else:
                break

def test():
    anal = analyzer()
    fname = "pages/141130/141130_10:42:18.html"
    data = codecs.open(fname, 'r', 'utf8').read()
    pl = anal.list_papers(data)
    for i in range(len(pl)):
        if i != 12:
            continue
        print unicode(anal.extract_c(pl[i]))
    
if __name__ == '__main__':
    main()
