import socks
import socket
import requests
import stem.process

from pymongo import MongoClient
from stem.util import term

tor = None
client = MongoClient('localhost', 27017)
db = client['darkweb']
pages = db['pages']

SOCKS_PORT = 9050;

url = "http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page"

def main():
    setup()
    print query(url)


def kill():
    tor.kill()
    
def setup():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
    socket.socket = socks.socksocket
    socket.getaddrinfo = getaddrinfo

    global tor
    tor = stem.process.launch_tor_with_config(
        config = {
            'SocksPort': str(SOCKS_PORT),
        },
        init_msg_handler = print_lines)

def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]


def print_lines(line):
    print term.format(line, term.Color.BLUE)

def query(url):
    try:
        return requests.get(url)
    except:
        return "ERROR: Could not complete request."

def db_test():
    pid = pages.insert({'entry': 'test-entry'})
    assert pages.find_one({'_id': pid})['_id'] == pid

    print [i for i in pages.find()]
