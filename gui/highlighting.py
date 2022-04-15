from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QTextCursor, QColorConstants
from PyQt6.QtWidgets import QTextEdit
from sortedcontainers import SortedDict
from gui import cursoroperations as co, Input


class HighlightingSystem:

    def __init__(self, keys_text, notes_text, set_freeze_func):
        self.notes_text = notes_text
        self.keys_text = keys_text
        self.all_keys = []
        self.set_freeze = set_freeze_func
        self.highlights = SortedDict()
        self.last_highlight_pos = 0
        self.original_text = None

    def highlight(self, pos, all_keys):

        self.all_keys = all_keys

        if self.original_text is None:  # si le document est nul, alors c'est la 1ère opération de surlignage.
            self.original_text = QTextEdit()
            self.original_text.setHtml(self.notes_text.toHtml())


        if Input.is_pressed(Qt.Key.Key_Control):
            self.__highlight_key(pos, True, True)

        elif Input.is_pressed(Qt.Key.Key_A):
            self.__highlight_from_to(pos)

        else:
            self.__clear_highlights(pos)
            self.__highlight_key(pos, True, True)


        if len(self.highlights) == 0:
            self.original_text = None
            self.set_freeze(False)
            return

        self.set_freeze(True)  # On ne peut pas modifier les notes qui contient des idées surlignée

    def __clear_highlights(self, exception):

        if len(self.highlights) == 1:
            keys_cursor = self.keys_text.cursorForPosition(exception)
            keys_cursor.movePosition(QTextCursor.MoveOperation.WordLeft)
            exception = keys_cursor.position()

            if self.highlights.keys()[0] == exception:
                return

        while len(self.highlights) != 0:
            pos = self.highlights.keys()[0]
            self.__highlight_key(pos, False, False)

    def __rehighlight(self, to_rehighlight, double_check):

        for pos in self.highlights.keys():
            self.__highlight_key(pos, to_rehighlight, double_check)

    def __highlight_key(self, pos, to_highlight, double_check_to_highlight):

        keys_cursor = self.keys_text.textCursor()
        if type(pos) == QPoint:
            keys_cursor = self.keys_text.cursorForPosition(pos)
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
            if keyword.strip() == '':
                return
            if highlight_pos in self.highlights.keys():
                to_highlight = False

        self.keys_text.setTextCursor(keys_cursor)
        if to_highlight:
            self.keys_text.setTextBackgroundColor(QColorConstants.Yellow)
            self.last_highlight_pos = highlight_pos

        else:
            self.keys_text.setTextBackgroundColor(QColorConstants.Transparent)

        keys_cursor.clearSelection()
        self.keys_text.setTextCursor(keys_cursor)

        for idea in self.all_keys:  # chercher la phrase de l'idée surlignée
            if idea.line < line:
                continue
            elif idea.line == line:
                if keyword in idea.keywords:
                    phrase = idea.phrase.lower()
                    self.__highlight_phrase(highlight_pos, phrase, line, to_highlight, double_check_to_highlight)
                    break

    def __highlight_phrase(self, highlight_pos, phrase, line, to_highlight, double_check):

        if phrase.strip() == '':
            if to_highlight:
                self.highlights[highlight_pos] = 0
            else:
                self.highlights.pop(highlight_pos)
            return

        cursor = self.notes_text.textCursor()
        co.move_cursor_to_line(cursor, line)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        last_pos = cursor.position()
        chars = len(phrase)
        cursor.setPosition(last_pos+chars, QTextCursor.MoveMode.KeepAnchor)
        while phrase not in cursor.selectedText().lower():
            cursor.clearSelection()
            last_pos += 1
            cursor.setPosition(last_pos)
            cursor.setPosition(last_pos + chars, QTextCursor.MoveMode.KeepAnchor)

        '''
        cursor = self.notes_text.textCursor()
        co.move_cursor_to_line(cursor, line)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        last_pos = cursor.position()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        while phrase in cursor.selectedText().lower():  # Avancer le curseur vers le début de la phrase
            cursor.clearSelection()
            cursor.setPosition(last_pos)
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter)
            last_pos = cursor.position()
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)

        cursor.clearSelection()
        cursor.setPosition(last_pos-1)
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)

        while phrase not in cursor.selectedText().lower():  # Reculer le curseur vers la fin de la phrase
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
        '''
        self.notes_text.setTextCursor(cursor)
        if to_highlight:
            self.notes_text.setTextBackgroundColor(QColorConstants.Yellow)
            self.highlights[highlight_pos] = len(phrase)
        else:
            original_cursor = self.original_text.textCursor()
            original_cursor.setPosition(last_pos)
            original_cursor.setPosition(last_pos + chars, QTextCursor.MoveMode.KeepAnchor)
            self.original_text.setTextCursor(original_cursor)

            original_html = original_cursor.selection().toHtml()
            cursor.insertHtml(original_html)
            self.highlights.pop(highlight_pos)
            if double_check:
                self.__rehighlight(True, False)

        cursor.clearSelection()
        self.notes_text.setTextCursor(cursor)

    def __highlight_from_to(self, end_pos):

        cursor = QTextEdit().cursorForPosition(end_pos)
        cursor.movePosition(QTextCursor.MoveOperation.WordLeft)

        for pos in self.highlights:
            if self.last_highlight_pos >= pos <= cursor.position():
                self.__highlight_key(pos, True, False)
