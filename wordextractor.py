from bisect import bisect
from sortedcontainers import sorteddict
from collections import OrderedDict
import threading

DICT_PATH = r'dictionary.txt'
USAGE_DICT = sorteddict.SortedDict()


def open_dict():
    with open(DICT_PATH, 'r') as dict_file:
        for line in dict_file.readlines():
            word_info = line.split(' ')
            USAGE_DICT[word_info[0]] = int(word_info[1])


dict_thread = threading.Thread(target=open_dict)
dict_thread.start()


class Idea:

    def __init__(self, phrase: str, keywords=None):
        super().__init__()
        if keywords is None:
            keywords = list()
        self.keywords = keywords
        self.phrase = phrase

    def __str__(self):
        return ' '.join(self.keywords)

    def __len__(self):
        return len(self.keywords)

    def add_keyword(self, new_keyword):
        self.keywords.append(new_keyword)


def __keywords_matrix(text):
    phrases = text.split(".")
    words = []

    for phrase in phrases:
        words.append(phrase.split(' '))

    return words


def __is_key(word):
    word = word.lower()
    if word == '' or word == ' ':
        return False

    pos = USAGE_DICT.bisect(word)

    in_dict = True if pos != len(USAGE_DICT) and USAGE_DICT.get(pos) == word else False
    print(word, in_dict)

    if in_dict:
        if USAGE_DICT[word] < 40:
            return True
    else:
        return False

    return True


def get_ideas(text):
    words = __keywords_matrix(text)
    ideas = []

    for phrase in words:
        idea = Idea(' '.join(phrase))

        for word in phrase:

            if __is_key(word):
                idea.add_keyword(word)

        ideas.append(idea)

    return ideas
