from PyQt5.QtGui import QFont
from sortedcontainers import sorteddict
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

    def __init__(self, phrase: str, line: int, max_font: QFont, keywords=None):

        if keywords is None:
            keywords = list()
        self.keywords = keywords
        self.phrase = phrase
        self.line = line
        self.max_font = max_font

    def __str__(self):
        string = ' '.join(self.keywords).strip()
        if string == '':
            return '\n'
        return string

    def is_empty(self):
        return len(self.keywords) == 0

    def add_keyword(self, new_keyword):
        if new_keyword not in self.keywords:
            self.keywords.append(new_keyword)


def words_matrix(text):
    phrases = text.split("\n")
    words = []

    for i, phrase in enumerate(phrases):
        words.append(phrase.split(' '))

    return words


def is_key(word):
    word = word.lower()
    if word == '' or word == ' ':
        return False

    dict_thread.join()  # at this point, the dictionary should be completed.

    pos = USAGE_DICT.bisect(word) - 1

    in_dict = True if pos != len(USAGE_DICT) and USAGE_DICT.keys()[pos] == word else False

    if in_dict:
        if USAGE_DICT[word] < 40:
            return True

    return False


def get_ideas(text, max_fonts):
    words = words_matrix(text)
    ideas = []

    for i, phrase in enumerate(words):
        idea = Idea(' '.join(phrase), i, max_fonts[i])

        for word in phrase:

            if is_key(word):
                idea.add_keyword(word)
                ideas.append(idea)

    return ideas
