import socks
import socket
import requests
import stem.process
import re
import HTMLParser

from pymongo import MongoClient
from stem.util import term

temp_data = []

tor = None
parser = None
client = MongoClient('localhost', 27017)
db = client['darkweb']
pages = db['pages']

SOCKS_PORT = 9050;
URL = "http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page"

def main():
    proxy_setup()
    r = query(URL)
    print_lines("")

    global parser
    parser = ScraperParser()
    parser.feed(r.content)

    kill()

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

        print "Encountered a start tag:", tag, attrs

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag

    def handle_data(self, data):
        try:    
            if self.collect_link:
                temp_data.append((self.last_link, data))
                self.collect_link = False
        except:
            self.collect_link = False

def parse_title():
    return


def parse_links(content):
    return

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

def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

def db_test():
    pid = pages.insert({'entry': 'test-entry'})
    assert pages.find_one({'_id': pid})['_id'] == pid

    print [i for i in pages.find()]
