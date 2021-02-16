import re
import string
import sys

import requests
from bs4 import BeautifulSoup
from collections import Counter


class KeyWords(object):

    def __init__(self, url):
        self.url = url

    def start(self):
        """get html"""
        r = requests.get(self.url)
        self.html = r.text
        self.get_text()

    def get_text(self):
        """parsing text from html"""
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.text = self.soup.get_text()
        self.text = re.sub("^\s+|\n|\r|\s+$", '', self.text)
        with open('text.txt', 'w') as f:
            f.write(str(self.text))


if __name__ == '__main__':
    # get url in command line
    url = sys.argv[1]

    keywords = KeyWords(url)
    keywords.start()
