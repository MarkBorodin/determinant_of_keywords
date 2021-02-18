import math
import re
import string
import sys
from collections import Counter
from operator import itemgetter

import requests
import spacy
from bs4 import BeautifulSoup
from gensim.summarization import keywords
from nltk import tokenize
from nltk.corpus import stopwords

import rake

nlp = spacy.load("en_core_web_md")


class KeyWords(object):

    def __init__(self, url, number_of_keywords=10, html=None):
        self.url = url
        self.number_of_keywords = number_of_keywords
        self.html = html
        self.stop_words = set(stopwords.words('english'))
        self.stoppath = "data/stoplists/SmartStoplist.txt"

    def start(self):
        """get html"""
        if self.html:
            self.get_text()
        else:
            r = requests.get(self.url)
            self.html = r.text
            self.get_text()

    def get_text(self):
        """parsing text from html"""
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.text_from_soup = self.soup.get_text()
        self.primary_text = re.sub("^\s+|\n|\r|\s+$", '', self.text_from_soup)
        self.my_clean()

    def my_clean(self):
        """cleaning text from unnecessary"""
        # load data
        text = self.text_from_soup
        # split into words
        from nltk.tokenize import word_tokenize
        tokens = word_tokenize(text)
        # convert to lower case
        tokens = [w.lower() for w in tokens]
        # remove punctuation from each word
        import string
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        # remove remaining tokens that are not alphabetic
        words = [word for word in stripped if word.isalpha()]
        # filter out stop words
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if not w in stop_words and len(w) > 2]
        self.text = words

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
        meta = str(self.soup.find_all('meta'))
        tags = h + b + em + i + title + head + meta
        self.keywords_in_tags = []
        for word in keywords:
            if type(word) is not str:
                if word[0] in tags:
                    self.keywords_in_tags.append(word[0])
            else:
                if word in tags:
                    self.keywords_in_tags.append(word)
        print(f'keywords in  main_tags: {self.keywords_in_tags}')
        return self.keywords_in_tags

    def keywords_tf_idf(self):
        """Term Frequency – How frequently a term occurs in a text. It is measured as the number of times a term t
         appears in the text / Total number of words in the document
        Inverse Document Frequency – How important a word is in a document.
         It is measured as log(total number of sentences / Number of sentences with term t)
        TF-IDF – Words’ importance is measure by this score. It is measured as TF * IDF"""

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

        self.tf_idf_list = []
        for key, value in key_words_tf_idf.items():
            temp = (key, value)
            self.tf_idf_list.append(temp)

        print(f'keywords according to tf idf: {self.tf_idf_list}')
        return self.tf_idf_list

    def rake_keywords(self):
        """get keywords according to rake"""
        stoppath = "data/stoplists/SmartStoplist.txt"
        rake_object = rake.Rake(stoppath, 3, 3, 4)
        self.keywords_rake_list = rake_object.run(self.primary_text)
        try:
            self.keywords_rake_list = self.keywords_rake_list[:self.number_of_keywords]
        except:
            pass
        print("Keywords according to rake:", self.keywords_rake_list)
        return self.keywords_rake_list

    def rake_phrase(self):
        """get phrases according to rake"""
        rake_object = rake.Rake(self.stoppath)
        phrase = rake_object.run(self.primary_text)
        self.phrase_rake_list = phrase[:self.number_of_keywords]
        print(f'phrases according to rake: {self.phrase_rake_list}')
        return self.phrase_rake_list

    def common_words_for_all_methods(self):
        """common_words_for_all_methods"""
        tf_idf_keywords_list = [word[0] for word in self.tf_idf_list]
        most_frequently_used_words_list = [word[0] for word in self.most_common]
        rake_keywords_list = [word[0] for word in self.keywords_rake_list]
        keywords_gensim_list = self.keywords_gensim_list
        all_words = tf_idf_keywords_list + most_frequently_used_words_list + rake_keywords_list + keywords_gensim_list
        self.all_methods_common_keywords_list = list(set([word for word in all_words if word in tf_idf_keywords_list and
            word in most_frequently_used_words_list and word in rake_keywords_list and word in keywords_gensim_list]))
        print(f'keywords that are common to all methods: {self.all_methods_common_keywords_list}')
        return self.all_methods_common_keywords_list

    def all_methods_keywords(self):
        """all_methods_keywords"""
        tf_idf_keywords_list = [word[0] for word in self.tf_idf_list]
        most_frequently_used_words_list = [word[0] for word in self.most_common]
        rake_keywords_list = [word[0] for word in self.keywords_rake_list]
        keywords_gensim_list = self.keywords_gensim_list
        self.all_methods_keywords_list = list(set(
            tf_idf_keywords_list + most_frequently_used_words_list + rake_keywords_list + keywords_gensim_list
        ))
        print(f'keywords from methods: {self.all_methods_keywords_list}')
        return self.all_methods_common_keywords_list

    def gensim(self):
        """get keywords according to gensim"""
        self.keywords_gensim_list = keywords(self.primary_text, words=5, split=True)
        print(f'keywords  according to gensim: {self.keywords_gensim_list}')
        return self.keywords_gensim_list

    def jaccard(self, word1, word2):
        """find jaccard index"""
        intersection = len(list(set(word1).intersection(word2)))
        union = (len(word1) + len(word2)) - intersection
        return float(intersection) / union

    def check_jaccard(self, words_list):
        """keywords + words that are close in index jaccard"""
        all_methods_keywords_list_with_jaccard = []
        self.get_hotwords(self.primary_text)
        for word1 in self.hotwords:
            for word2 in words_list:
                if word1 != word2:
                    j_index = self.jaccard(word1, word2)
                    if j_index > 0.8:
                        all_methods_keywords_list_with_jaccard.append(word1)
        self.check_jaccard_list = list(set(all_methods_keywords_list_with_jaccard + words_list))
        print(f'keywords + words that are close in index jaccard: {self.check_jaccard_list}')
        return self.check_jaccard_list

    def get_hotwords(self, text):
        """get hot words from text"""
        text = re.sub(r"[#$%&'()*+/<=>@^_`{|}©]", "", text)
        text = re.sub(r"[1234567890]", "", text)
        self.hotwords = []
        pos_tag = ['PROPN', 'ADJ', 'NOUN']
        doc = nlp(text.lower())
        for token in doc:
            if (token.text in nlp.Defaults.stop_words or token.text in string.punctuation):
                continue
            if (token.pos_ in pos_tag):
                self.hotwords.append(token.text)
        return self.hotwords


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
    tf_idf_keywords_in_tags = key_words.check_for_presence_in_main_tags(tf_idf_keywords)

    # tf_idf_keywords on the page, which are also contained in site name
    tf_idf_keywords_in_url = key_words.check_by_site_name(tf_idf_keywords)

    print('--------------------------------')
    ########################################
    print('most frequently used words on the page')

    # get most frequently used words
    most_frequently_used_words = key_words.most_frequently_used_words()

    # most_frequently_used_words on the page, which are also contained in main_tags tags
    most_frequently_used_words_in_tags = key_words.check_for_presence_in_main_tags(most_frequently_used_words)

    # most_frequently_used_words on the page, which are also contained in site name
    most_frequently_used_words_in_url = key_words.check_by_site_name(most_frequently_used_words)

    print('--------------------------------')
    ########################################
    print('keywords and phrases according to rake')

    # get keywords according to rake
    rake_keywords = key_words.rake_keywords()

    # keywords according to rake on the page, which are also contained in main_tags tags
    rake_keywords_in_tags = key_words.check_for_presence_in_main_tags(rake_keywords)

    # keywords according to rake on the page, which are also contained in site name
    rake_keywords_in_url = key_words.check_by_site_name(rake_keywords)

    print('--------------------------------')
    # get phrases according to rake
    rake_phrases = key_words.rake_phrase()

    # get phrases according to gensim
    print('--------------------------------')
    print('keywords according to gensim')
    keywords_gensim = key_words.gensim()

    # keywords according to gensim, which are also contained in main_tags tags
    keywords_according_to_gensim_in_tags = key_words.check_for_presence_in_main_tags(keywords_gensim)

    print('--------------------------------')
    print('common words for all methods')
    # get keywords that are common to all methods (tf_idf, most_frequently_used_words, rake keywords)
    keywords_that_are_common_to_all_methods = key_words.common_words_for_all_methods()

    print('--------------------------------')
    print('keywords from all methods')
    # get keywords from all methods (tf_idf, most_frequently_used_words, rake keywords)
    keywords_from_all_methods = key_words.all_methods_keywords()

    print('--------------------------------')
    print('keywords from all methods that are in the main tags')
    keywords_from_all_methods_that_are_in_the_main_tags = list(set(
        tf_idf_keywords_in_tags + most_frequently_used_words_in_tags +
        rake_keywords_in_tags + keywords_according_to_gensim_in_tags
                                                            ))
    print(keywords_from_all_methods_that_are_in_the_main_tags)

    # get phrases according to gensim
    print('--------------------------------')
    print('keywords from all methods with jaccard')
    keywords_jaccard = key_words.check_jaccard(keywords_from_all_methods_that_are_in_the_main_tags)
