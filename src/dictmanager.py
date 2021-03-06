from sortedcontainers import SortedDict
import threading
import re
from idea import Idea

DICT_PATH = '../resources/dictionary.txt'
USAGE_DICT = SortedDict()


def open_dict():
    """
    Cette fonction remplis le dictionnaire utilisé appelé USAGE_DICT avec les mots dans le fichier 'dictionary.txt'.
    Les mots seront comparées aux idées et ces mots on un int qui représente la fréquence d'utilisation du mot.
    """
    with open(DICT_PATH, 'r') as dict_file:
        for line in dict_file.readlines():
            word_info = line.split(' ')
            USAGE_DICT[word_info[0]] = int(word_info[1])


# Ouverture du dictionnaire dans un thread séparé :
dict_thread = threading.Thread(target=open_dict)
dict_thread.start()


def words_matrix(text):
    """
    Cette fonction crée une matrice de mots à partir d'une string.
    Chaque ligne de texte représente une ligne de la matrice.
    """
    phrases = text.lower().split("\n")
    words = []

    for phrase in phrases:
        words.append(re.split('[ \\W\\d]+', phrase))

    return words, phrases


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

    dict_thread.join()  # À ce point, le dictionnaire doit être complété

    pos = USAGE_DICT.bisect(word) - 1

    in_dict = True if pos != len(USAGE_DICT) and USAGE_DICT.keys()[pos] == word else False

    if in_dict:
        if USAGE_DICT[word] <= 50:
            return True

    return False


def get_ideas(text, max_fonts: list, ideas: list, from_to: tuple):
    """
    Cette fonction analyse un text en déduisant ses mots clés. Chaque ligne est considérée comme une phrase.
    Chaque phrase sera associée à une liste de mots clés dans un objet Idea.
    Remarque : La liste de mots clé d'une idée pourrait être nulle.
    La fonction met à jour la liste des idées donnée en paramètre en y inscrivant les idées déduites du text entre
    les lignes indiquées par le tuple from_to.
    :param text : le text à analyser.
    :param max_fonts : les plus grands fonts des lignes à analyser.
    :param ideas : list des idées à mettre à jour.
    :param from_to : indique la ligne de départ et la ligne de fin.
    """

    start = 0
    if from_to is not None:
        start = from_to[0]

    delete_old_ideas(ideas, from_to, text)
    matrix = words_matrix(text)
    words = matrix[0]
    phrases = matrix[1]

    for i, words_in_phrase in enumerate(words):
        idea = Idea(phrases[i], i + start, max_fonts[i])

        for word in words_in_phrase:

            if is_key(word):
                idea.add_keyword(word)

        ideas.append(idea)


def delete_old_ideas(ideas: list, from_to: tuple, text: str):
    """
    Cette fonction supprime les anciennes idées sitées entre le limites données en paramètre.
    :param ideas : objet liste contenant les idées
    :param from_to : limites des lignes
    :param text : le text
    """
    if from_to is None:
        ideas.clear()
        return

    start = from_to[0]
    end = from_to[1]
    ideas_to_remove = []
    phrases = text.split('\n')

    for i, idea in enumerate(ideas):
        if start <= idea.line <= end:
            if idea.phrase_include_idea(phrases[idea.line - start]):
                ideas_to_remove.append(idea)

    for idea in ideas_to_remove:
        ideas.remove(idea)
