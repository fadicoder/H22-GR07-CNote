from PyQt5.QtGui import QFont
from sortedcontainers import sorteddict
import threading

import dictmanager

DICT_PATH = r'dictionary.txt'
USAGE_DICT = sorteddict.SortedDict()


def open_dict():
    """
    This function fill the ordered dictionary USAGE_DICT with the words written in the file 'dictionary.txt'.
    The words are the keys and there value is an int that represent the percentage of usage of the word.
    """
    with open(DICT_PATH, 'r') as dict_file:
        for line in dict_file.readlines():
            word_info = line.split(' ')
            USAGE_DICT[word_info[0]] = int(word_info[1])


# Opening the dictionary with a seperated thread:
dict_thread = threading.Thread(target=open_dict)
dict_thread.start()


class Idea:
    """
    This class defines the concept of an idea which is a list of keywords associated with a sentace.
    The idea object also contains the biggest font of the sentence for front-end purposes.
    """

    def __init__(self, phrase: str, line: int, max_font: QFont, keywords=None):

        if keywords is None:
            keywords = list()
        self.keywords = keywords
        self.phrase = phrase
        self.line = line
        self.max_font = max_font

    def __str__(self):
        if self.is_empty():
            return ''
        return ' '.join(self.keywords)

    def is_empty(self):
        return len(self.keywords) == 0

    def add_keyword(self, new_keyword):
        if new_keyword not in self.keywords:
            self.keywords.append(new_keyword)

    def in_same_line(self, idea2):
        return self.line == idea2.line


def get_line(idea: Idea):
    return idea.line


def words_matrix(text):
    """
    This function create a matrix of words from a string text. Each line of text represent a line of the matrix.
    """
    phrases = text.lower().split("\n")
    words = []

    for phrase in phrases:
        words.append(phrase.split(' '))

    return words


def is_key(word):
    """
    This function verify if the word given in argument is key with the dictionary USAGE_DICT.
    A word is key if the percentage of its usage is less than 40% according to the dictionary.

    :param word: string of the word to verify.
    :return: True if the word is key and False if it is not.
    """
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
    """
    This function analyses a text by extracting keywords.
    Each line (sentence) of the text is associated with its keywords as an idea.
    The function creates a list of ideas of all the text

    :param text: the string that will be analysed
    :param max_fonts: the biggest font of each line
    :return: A list of the ideas of the text
    """
    words = words_matrix(text)
    ideas = []

    for i, phrase in enumerate(words):
        idea = Idea(' '.join(phrase), i, max_fonts[i])

        for word in phrase:

            if is_key(word):
                idea.add_keyword(word)
        ideas.append(idea)

    return ideas