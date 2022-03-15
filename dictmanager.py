from sortedcontainers import sorteddict
import threading

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
    Cette classe définit le concept d'une idée qui est une liste de mots-clés associée à une phrase
    et au plus grand font de la phrase.
    """

    def __init__(self, phrase: str, line: int, max_font, keywords=None):

        if keywords is None:
            keywords = list()
        if type(keywords) == str:
            keywords = [keywords]

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

    def same_line(self, idea2):
        return self.line == idea2.line

    def get_line(self):
        return self.line


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

    :param: word: string of the word to verify.
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


def get_ideas(text, max_fonts: list, ideas: list, from_to: tuple):
    """
    Cette fonction analyse un text en déduisant ses mots clés. Chaque ligne est considérée comme une phrase.
    Chaque phrase sera associée à une liste de mots clés dans un objet Idea.
    Remarque : La liste de mots clé d'une idée pourrait être nulle.
    La fonction met à jour la liste des idées donnée en paramètre en y inscrivant les idées déduites du text entre
    les lignes indiquées par le tuple from_to.
    :param text: le text à analyser.
    :param max_fonts: les plus grands fonts des lignes à analyser.
    :param ideas list des idées à mettre à jour.
    :param from_to: indique la ligne de départ et la ligne de fin.
    """

    delete_old_ideas(ideas, from_to)
    words = words_matrix(text)

    for i, phrase in enumerate(words):
        idea = Idea(' '.join(phrase), i, max_fonts[i])

        for word in phrase:

            if is_key(word):
                idea.add_keyword(word)

        ideas.append(idea)


def delete_old_ideas(ideas: list, from_to: tuple = None):
    if from_to is None:
        ideas.clear()
        return

    start = from_to[0]
    end = from_to[1]

    for idea in ideas:
        if end <= idea.line >= start:
            ideas.remove(idea)


def add_idea_to_list(idea, line, ideas: list):
    i = line
    if len(ideas) < i:
        while ideas[i].line < line:
            i += 1
        if ideas[i].line == line:
            ideas[i] = idea
        return

    ideas.insert(i, idea)
