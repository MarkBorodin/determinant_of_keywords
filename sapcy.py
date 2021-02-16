import spacy

from collections import Counter
from string import punctuation

nlp = spacy.load("en_core_web_md")


def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']
    doc = nlp(text.lower())
    for token in doc:
        if (token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if (token.pos_ in pos_tag):
            result.append(token.text)
    return result  # 5


with open('text.txt', 'r') as f:
    text = f.read()
    all_words = get_hotwords(text)
    text_counts = Counter(all_words)
    # most popular words
    most_common = text_counts.most_common(10)
    print(most_common)
