import socks
import socket
import requests
import stem.process
import HTMLParser

from pymongo import MongoClient
from stem.util import term

link_data = []

tor = None
parser = None
client = MongoClient('localhost', 27017)
db = client['darkweb']
pages = db['pages']

SOCKS_PORT = 9050;
MAIN_URL = "http://lacbzxobeprssrfx.onion/index.php"
DEPTH = 2

def main():
    proxy_setup()

    print_magenta_lines("ADDING INITIAL PAGE: " + MAIN_URL)
    r = query(MAIN_URL)
    
    global parser
    parser = ScraperParser()
    parser.feed(r.content)

    pages.insert({'depth': DEPTH+1, 'content': r.content, 'url': MAIN_URL})
    print_magenta_lines("MAIN_PAGE_ADDED: " + MAIN_URL)

    crawl(DEPTH)

    kill()

def crawl(depth):
    if depth == 0:
        return

    counter = len(link_data)
    print_white_lines("ADDING: " + str(counter) + " PAGES")
    while len(link_data) > 0:
        url = link_data.pop(0)
        if url[0:4] == "http":
            print_purple_lines("GETTING PAGE: " + url)
            r = query(url)
            parser.feed(r.content)
            pages.insert({'depth': depth, 'content': r.content, 'url': url})
            print_purple_lines("PAGED ADDED: " + url)

        counter -= 1

        if counter == 0:
            depth -= 1
            counter = len(link_data)
            print_magenta_lines("DECREASED DEPTH: " + str(depth))

        if depth == 0:
            return


############################################################
#                                                          #
#                    PARSING CONTENT                       #
#                                                          #
############################################################

class ScraperParser(HTMLParser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        if (tag == 'a'):
            for attr in attrs:
                if attr[0] == 'href':
                    self.last_link = attr[1]
                    self.collect_link = True

    def handle_endtag(self, tag):
        return

    def handle_data(self, data):
        try:    
            if self.collect_link:
                link_data.append(self.last_link)
                self.collect_link = False
        except:
            self.collect_link = False

############################################################
#                                                          #
#                   QUERYING FUNCTIONS                     #
#                                                          #
############################################################

def query(url):
    try:
        return requests.get(url)
    except:
        return "ERROR: Could not complete request."

def proxy_setup():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
    socket.socket = socks.socksocket
    socket.getaddrinfo = getaddrinfo

    global tor
    tor = stem.process.launch_tor_with_config(
        config = {
            'SocksPort': str(SOCKS_PORT),
        },
        init_msg_handler = print_lines)

def kill():
    tor.kill()
    print "DONE: Killed tor instance."    

def print_lines(line):
    print term.format(line, term.Color.BLUE)

def print_purple_lines(line):
    print term.format(line, term.Color.GREEN)

def print_white_lines(line):
    print term.format(line, term.Color.WHITE)

def print_magenta_lines(line):
    print term.format(line, term.Color.MAGENTA)

def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

def db_test():
    pid = pages.insert({'entry': 'test-entry'})
    assert pages.find_one({'_id': pid})['_id'] == pid

    print [i for i in pages.find()]
