from __future__ import absolute_import
from __future__ import print_function

import rake

stoppath = "data/stoplists/SmartStoplist.txt"

with open('text.txt', 'r') as f:
    text = f.read()


def get_keywords(text):
    stoppath = "data/stoplists/SmartStoplist.txt"
    rake_object = rake.Rake(stoppath, 3, 3, 4)
    keywords = rake_object.run(text)
    print("Keywords:", keywords)
    return keywords


def get_phrase(text):
    rake_object = rake.Rake(stoppath)
    phrase = rake_object.run(text)
    print(phrase)
    first_ten = phrase[:10]
    print(first_ten)


get_keywords(text)
get_phrase(text)
