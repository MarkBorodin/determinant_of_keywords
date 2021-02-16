import math
import re
import string
import sys
from collections import Counter
from operator import itemgetter

import requests
import spacy
from bs4 import BeautifulSoup
from nltk import tokenize
from nltk.corpus import stopwords

import rake


class KeyWords(object):

    def __init__(self, url, number_of_keywords=10):
        self.url = url
        self.number_of_keywords = number_of_keywords
        self.stop_words = set(stopwords.words('english'))
        self.stoppath = "data/stoplists/SmartStoplist.txt"

    def start(self):
        """get html"""
        r = requests.get(self.url)
        self.html = r.text
        self.get_text()

    def get_text(self):
        """parsing text from html"""
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.primary_text = self.soup.get_text()
        self.primary_text = re.sub("^\s+|\n|\r|\s+$", '', self.primary_text)
        self.my_clean()

    def my_clean(self):
        """cleaning text from unnecessary"""

        # clean from trash
        text_d = self.primary_text
        text_d = text_d.strip() # noqa
        text_d = text_d.lower()
        text_d = re.sub(r"[1234567890]", "", text_d)
        text_d = re.sub('https?://\S+|www\.\S+', '', text_d)
        text_d = re.sub('[%s]' % re.escape(string.punctuation), '', text_d)
        text_d = re.sub(r"[!#$%&'()*+,-./:;<=>?@[\]^_`{|}\n.,\-©\\]", "", text_d)
        text_d = text_d.replace('–', '').replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace('…', '').replace('?', '').replace('!', '').replace('/', '').replace('\\', '')
        text_d = text_d.replace(' the ', '')
        text_d = text_d.strip().split(sep=' ')
        text = []
        for i in text_d:
            if i not in self.stop_words:
                text.append(i)
        self.text = text

    def most_frequently_used_words(self):
        """get most_frequently_used_words"""
        # class for count
        self.text_counts = Counter(self.text)
        # most popular words
        most_common = self.text_counts.most_common(self.number_of_keywords)
        self.most_common = [word for word in most_common if len(word[0]) > 2]
        print(f'most frequently used words on the page: {self.most_common}')
        return self.most_common

    def get_all_words_rating(self):
        """count the number of each word"""
        print(self.text_counts)
        return self.text_counts

    def check_by_site_name(self, keywords):
        """keywords on the page, which are also contained in site name"""
        self.keywords_in_url = list()
        for i in keywords:
            if i[0] in self.url:
                self.keywords_in_url.append(i[0])
        print(f'keywords in url: {self.keywords_in_url}')

    def check_for_presence_in_main_tags(self, keywords):
        """keywords on the page, which are also contained in main_tags (like h, b, em, title, head)"""
        h = str(self.soup.find_all(re.compile(r'h\d+')))
        b = str(self.soup.find_all('b'))
        em = str(self.soup.find_all('em'))
        i = str(self.soup.find_all('i'))
        title = str(self.soup.title)
        head = str(self.soup.find_all('head'))
        tags = h + b + em + i + title + head
        self.keywords_in_tags = []
        for word in keywords:
            if word[0] in tags:
                self.keywords_in_tags.append(word[0])
        print(f'keywords in  main_tags: {self.keywords_in_tags}')
        return self.keywords_in_tags

    def keywords_tf_idf(self):
        """Term Frequency – How frequently a term occurs in a text. It is measured as the number of times a term t
         appears in the text / Total number of words in the document
        Inverse Document Frequency – How important a word is in a document.
         It is measured as log(total number of sentences / Number of sentences with term t)
        TF-IDF – Words’ importance is measure by this score. It is measured as TF * IDF"""

        nlp = spacy.load("en_core_web_md")

        doc = self.primary_text.lower()
        doc = doc.replace('\n', '')
        doc = re.sub(r"[#$%&'()*+/<=>@^_`{|}©]", "", doc)
        doc = re.sub(r"[1234567890]", "", doc)

        # Step 1 : Find total words in the document
        total_words = doc.split()
        total_word_length = len(total_words)

        # Step 2 : Find total number of sentences
        total_sentences = tokenize.sent_tokenize(doc)
        total_sent_len = len(total_sentences)

        # Step 3: Calculate TF for each word
        tf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in self.stop_words:
                if each_word in tf_score:
                    tf_score[each_word] += 1
                else:
                    tf_score[each_word] = 1

        # Dividing by total_word_length for each dictionary element
        tf_score.update((x, y / int(total_word_length)) for x, y in tf_score.items())

        # Check if a word is there in sentence list
        def check_sent(word, sentences):
            final = [all([w in x for w in word]) for x in sentences]
            sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
            return int(len(sent_len))

        # Step 4: Calculate IDF for each word
        idf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in self.stop_words:
                if each_word in idf_score:
                    idf_score[each_word] = check_sent(each_word, total_sentences)
                else:
                    idf_score[each_word] = 1

        # Performing a log and divide
        idf_score.update((x, math.log(int(total_sent_len) / y)) for x, y in idf_score.items())

        # Step 5: Calculating TF*IDF
        tf_idf_score_temp = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}
        tf_idf_score = {}
        for item in tf_idf_score_temp.items():
            if len(item[0]) > 2:
                tf_idf_score.update({item[0]: item[1]})

        # Get top N important words in the document
        def get_top_n(dict_elem, n):
            result = dict(sorted(dict_elem.items(), key=itemgetter(1), reverse=True)[:n])
            return result

        key_words_tf_idf = get_top_n(tf_idf_score, 10)

        lst = []
        for key, value in key_words_tf_idf.items():
            temp = (key, value)
            lst.append(temp)

        print(f'keywords according to tf idf: {lst}')
        return lst

    def rake_keywords(self):
        """get keywords according to rake"""
        stoppath = "data/stoplists/SmartStoplist.txt"
        rake_object = rake.Rake(stoppath, 3, 3, 4)
        keywords = rake_object.run(self.primary_text)
        print("Keywords according to rake:", keywords)
        return keywords

    def rake_phrase(self):
        """get phrases according to rake"""
        rake_object = rake.Rake(self.stoppath)
        phrase = rake_object.run(self.primary_text)
        first_ten = phrase[:10]
        print(f'phrases according to rake: {first_ten}')
        return first_ten


if __name__ == '__main__':
    # get url in command line
    url = sys.argv[1]

    # number of keywords
    number_of_keywords = int(sys.argv[2])

    # get object. The first argument is url. The second argument is the number of keywords
    key_words = KeyWords(url, number_of_keywords)
    key_words.start()

    print('--------------------------------')
    ########################################
    print('keywords according to tf idf')

    # get keywords according to tf idf
    tf_idf_keywords = key_words.keywords_tf_idf()

    # tf_idf_keywords on the page, which are also contained in main_tags tags
    key_words.check_for_presence_in_main_tags(tf_idf_keywords)

    # tf_idf_keywords on the page, which are also contained in site name
    key_words.check_by_site_name(tf_idf_keywords)

    print('--------------------------------')
    ########################################
    print('most frequently used words on the page')

    # get most frequently used words
    most_frequently_used_words = key_words.most_frequently_used_words()

    # most_frequently_used_words on the page, which are also contained in main_tags tags
    key_words.check_for_presence_in_main_tags(most_frequently_used_words)

    # most_frequently_used_words on the page, which are also contained in site name
    key_words.check_by_site_name(most_frequently_used_words)

    print('--------------------------------')
    ########################################
    print('keywords and phrases according to rake')

    # get keywords according to rake
    key_words.rake_keywords()

    print('--------------------------------')
    # get phrases according to rake
    key_words.rake_phrase()

    print(key_words.primary_text)
