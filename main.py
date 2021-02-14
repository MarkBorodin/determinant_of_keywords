import re
import string
import sys

import requests
from bs4 import BeautifulSoup
from collections import Counter


class KeyWords(object):

    def __init__(self, url, number_of_keywords=5):
        self.url = url
        self.number_of_keywords = number_of_keywords

    def start(self):
        """get html"""
        r = requests.get(self.url)
        self.html = r.text
        self.get_text()

    def get_text(self):
        """parsing text from html"""
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.text = self.soup.text
        self.clean()

    def clean(self):
        """cleaning text from unnecessary"""
        # clean from trash
        text_d = self.text
        text_d = text_d.strip() # noqa
        text_d = text_d.lower()
        text_d = re.sub(r"[1234567890]", "", text_d)
        text_d = re.sub('https?://\S+|www\.\S+', '', text_d)
        text_d = re.sub('[%s]' % re.escape(string.punctuation), '', text_d)
        text_d = re.sub(r"[!#$%&'()*+,-./:;<=>?@[\]^_`{|}\n.,\-©\\]", "", text_d)
        text_d = text_d.replace('\n', '').replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace('…', '').replace('?', '').replace('!', '').replace('/', '').replace('\\', '')
        text_d = text_d.replace(' the ', '')
        text_d = text_d.strip().split(sep=' ')
        text = []
        for i in text_d:
            word = i.strip()
            text.append(word)
        # stop_words:
        for i in text:
            if len(i) == 1:
                text.remove(i)
            if i == '':
                text.remove(i)
            if i == ' ':
                text.remove(i)
            if i == '\\':
                text.remove(i)
            if i == 'and':
                text.remove(i)
            if i == 'of':
                text.remove(i)
            if i == 'for':
                text.remove(i)
            if i == 'to':
                text.remove(i)
            if i == 'with':
                text.remove(i)
            if i == 'the':
                text.remove(i)
            if i == 'is':
                text.remove(i)
            if i == 'in':
                text.remove(i)
            if i == 'on':
                text.remove(i)
            if i == 'your':
                text.remove(i)
            if i == 'you':
                text.remove(i)
            if i == 'we':
                text.remove(i)
            if i == 'any':
                text.remove(i)
            if i == 'from':
                text.remove(i)
            if i == 'if':
                text.remove(i)
            if i == 'us':
                text.remove(i)
            if i == 'no':
                text.remove(i)
            if i == 'yes':
                text.remove(i)
            if i == 'have':
                text.remove(i)
            if i == 'has':
                text.remove(i)
            if i == 'had':
                text.remove(i)
            if i == 'was':
                text.remove(i)
            if i == 'were':
                text.remove(i)
            if i == 'but':
                text.remove(i)
            if i == 'an':
                text.remove(i)
            if i == 'can':
                text.remove(i)
            if i == 'where':
                text.remove(i)
            if i == 'how':
                text.remove(i)
            if i == 'do':
                text.remove(i)
            if i == 'does':
                text.remove(i)
            if i == 'could':
                text.remove(i)
            if i == 'am':
                text.remove(i)
            if i == 'are':
                text.remove(i)
            if i == 'should':
                text.remove(i)
            if i == 'not':
                text.remove(i)
            if i == 'need':
                text.remove(i)
            if i == 'must':
                text.remove(i)
            if i == 'or':
                text.remove(i)
            if i == 'take':
                text.remove(i)
            if i == 'some':
                text.remove(i)
            if i == 'they':
                text.remove(i)

        self.text = text
        self.get_keywords()

    def get_keywords(self):
        """get some keywords"""
        # class for count
        self.text_counts = Counter(self.text)
        # most popular words
        self.most_common = self.text_counts.most_common(self.number_of_keywords)
        print(f'most frequently used words on the page: {self.most_common}')
        return self.most_common

    def get_all_words_rating(self):
        """count the number of each word"""
        print(self.text_counts)
        return self.text_counts

    def check_by_site_name(self):
        """the most frequently used words on the page, which are also contained in site name"""
        self.keywords_in_url = list()
        for i in self.most_common:
            if i[0] in self.url:
                self.keywords_in_url.append(i[0])
        print(f'keywords in url: {self.keywords_in_url}')

    def check_most_common_in_h_tags(self):
        """the most frequently used words on the page, which are also contained in h tags"""
        hs = str(self.soup.find_all(re.compile(r'h\d+')))
        self.most_common_in_h_tags = []
        for word in self.most_common:
            if word[0] in hs:
                self.most_common_in_h_tags.append(word[0])
        print(f'keywords in h tags: {self.most_common_in_h_tags}')
        return self.most_common_in_h_tags


if __name__ == '__main__':
    # get url in command line
    url = sys.argv[1]

    # number of keywords
    number_of_keywords = int(sys.argv[2])

    # get object. The first argument is url. The second argument is the number of keywords
    key_words = KeyWords(url, number_of_keywords)

    # get_keywords
    key_words.start()

    # check keywords by site name
    key_words.check_by_site_name()

    # check for the most frequently used words in tags h
    key_words.check_most_common_in_h_tags()
