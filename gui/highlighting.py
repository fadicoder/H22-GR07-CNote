from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QTextCursor, QColorConstants
from PyQt6.QtWidgets import QTextEdit
from sortedcontainers import SortedDict
from gui import cursoroperations as co

highlights = SortedDict()


def highlight(notes_text, keys_text, pos, all_keys, ctrl_pressed):

    if ctrl_pressed:
        highlight_key(notes_text, keys_text, pos, all_keys, True, True)
    else:
        clear_all_highlights(notes_text, keys_text, all_keys)
        highlight_key(notes_text, keys_text, pos, all_keys, True, True)

        if len(highlights) == 0:
            notes_text.setReadOnly(False)

    notes_text.setReadOnly(True)  # On ne peut pas modifier les notes qui contient des idées surlignée


def rehighlight(notes_text, keys_text, all_keys, to_rehighlight, double_check):

    for pos in highlights.keys():
        highlight_key(notes_text, keys_text, pos, all_keys, to_rehighlight, double_check)


def clear_all_highlights(notes_text, keys_text, all_keys):

    rehighlight(notes_text, keys_text, all_keys, False, False)
    highlights.clear()
    notes_text.setReadOnly(False)


def highlight_key(notes_text, keys_text, pos, all_keys, to_highlight, double_check_to_highlight):
    """
    Cette fonction surligne l'idée du mot clée qui se trouve sur la position donnée en paramètre.
    L'idée inclue le mot clé avec sa phrase.
    :param notes_text : le QTextEdit des notes
    :param keys_text : le QTextEdit des mots-clés
    :param pos : la position du clic
    :param all_keys : liste de tous les mots-clés
    :return : return True si le surlignage a été effectué avec succès, sinon False.
    """

    keys_cursor = keys_text.textCursor()
    if type(pos) == QPoint:
        keys_cursor = keys_text.cursorForPosition(pos)
        keys_cursor.movePosition(QTextCursor.MoveOperation.WordLeft)
        highlight_pos = keys_cursor.position()

    else:
        keys_cursor.setPosition(pos)
        highlight_pos = pos

    keys_cursor.movePosition(QTextCursor.MoveOperation.NextWord, QTextCursor.MoveMode.KeepAnchor)
    keyword = keys_cursor.selectedText().strip()
    line = keys_cursor.blockNumber()

    if double_check_to_highlight:
        # verifications:
        if keyword == ' ':
            return
        if highlight_pos in highlights.keys():
            to_highlight = False

    keys_text.setTextCursor(keys_cursor)
    if to_highlight:
        keys_text.setTextBackgroundColor(QColorConstants.Yellow)
    else:
        keys_text.setTextBackgroundColor(QColorConstants.Transparent)

    keys_cursor.clearSelection()
    keys_text.setTextCursor(keys_cursor)

    for idea in all_keys:  # chercher la phrase de l'idée surlignée
        if idea.line < line:
            continue
        elif idea.line == line:
            if keyword in idea.keywords:
                phrase = idea.phrase
                highlight_phrase(notes_text, keys_text, highlight_pos, phrase, line, all_keys, to_highlight)
                break


def highlight_phrase(notes_text, keys_text, highlight_pos, phrase, line, all_keys, to_highlight):
    """
    Cette fonction surligne la phrase du text des notes donnée en paramètre à la ligne donnée en paramètre.
    :param to_highlight : indique si la phrase est à surligner ou s'il faut effacer le surlignage
    :param keyword: mot-clé
    :param notes_text : QTextEdit des notes
    :param phrase: phrase à surigner
    :param line : line surlaquelle la phrase se trouve
    """
    cursor = notes_text.textCursor()
    co.move_cursor_to_line(cursor, line)
    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
    last_pos = cursor.position()
    cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
    while phrase in cursor.selectedText():  # Avancer le curseur vers le début de la phrase
        cursor.clearSelection()
        cursor.setPosition(last_pos)
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter)
        last_pos = cursor.position()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)

    cursor.clearSelection()
    cursor.setPosition(last_pos - 1)
    cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)

    while phrase not in cursor.selectedText():  # Reculer le curseur vers la fin de la phrase
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)

    notes_text.setTextCursor(cursor)
    if to_highlight:
        highlights[highlight_pos] = cursor.selection().toHtml()
        notes_text.setTextBackgroundColor(QColorConstants.Yellow)
    else:
        notes_text.setTextBackgroundColor(QColorConstants.Transparent)
        highlights.pop(highlight_pos)
        rehighlight(notes_text, keys_text, all_keys, True, False)




    cursor.clearSelection()
    notes_text.setTextCursor(cursor)
