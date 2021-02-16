import re
import spacy
from nltk import tokenize
from operator import itemgetter
import math
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation


# Document text
with open('text.txt', 'r') as f:
    doc = f.read()


nlp = spacy.load("en_core_web_md")


# Remove stopwords
stop_words = set(stopwords.words('english'))

doc = doc.lower()
doc = doc.replace('\n', '').replace('–', '').replace('&', '')

# Step 1 : Find total words in the document
total_words = doc.split()
total_word_length = len(total_words)
print(f'total_word_length: {total_word_length}')


# Step 2 : Find total number of sentences
total_sentences = tokenize.sent_tokenize(doc)
total_sent_len = len(total_sentences)
print(f'total_sent_len: {total_sent_len}')


# Step 3: Calculate TF for each word
tf_score = {}
for each_word in total_words:
    each_word = each_word.replace('.', '')
    if each_word not in stop_words:
        if each_word in tf_score:
            tf_score[each_word] += 1
        else:
            tf_score[each_word] = 1
print(f'tf_score: {tf_score}')


# Dividing by total_word_length for each dictionary element
tf_score.update((x, y/int(total_word_length)) for x, y in tf_score.items())
print(f'tf_score: {tf_score}')


# Check if a word is there in sentence list
def check_sent(word, sentences):
    final = [all([w in x for w in word]) for x in sentences]
    sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
    return int(len(sent_len))


# Step 4: Calculate IDF for each word
idf_score = {}
for each_word in total_words:
    each_word = each_word.replace('.', '')
    if each_word not in stop_words:
        if each_word in idf_score:
            idf_score[each_word] = check_sent(each_word, total_sentences)
        else:
            idf_score[each_word] = 1


# Performing a log and divide
idf_score.update((x, math.log(int(total_sent_len)/y)) for x, y in idf_score.items())
print(f'idf_score: {idf_score}')


# Step 5: Calculating TF*IDF
tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}
print(f'tf_idf_score: {tf_idf_score}')


# Get top N important words in the document
def get_top_n(dict_elem, n):
    result = dict(sorted(dict_elem.items(), key=itemgetter(1), reverse=True)[:n])
    return result


print(get_top_n(tf_idf_score, 5))
