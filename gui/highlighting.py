from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QTextCursor, QColorConstants
from PyQt6.QtWidgets import QTextEdit
from sortedcontainers import SortedDict
from gui import cursoroperations as co, Input


class HighlightingSystem:

    def __init__(self, keys_text, notes_text, set_freeze_func):
        """
        Cette fonction initialize le système de surlignage des block des notes et des mots-clés.
        Cet object ne permet pas la modification du block notes lors du surlignage.

        Le dictionnaire des éléments surlignés est initialisé en tant que dictionnaire vide. Ce dictionnaire associe
        les positions d'un curseur à gauche des mots-clés surlignés avec la longueur des phrases de ces mot-clés.

        :param keys_text : block text des mots-clés
        :param notes_text : block text des notes
        :param set_freeze_func : méthode de 1 boolean en paramètre qui permet ou interdit la modification des mots-clés
        et du texte des notes.
        """
        self.notes_text = notes_text
        self.keys_text = keys_text
        self.all_keys = []
        self.set_freeze = set_freeze_func
        self.highlights = SortedDict()
        self.last_highlight_pos = 0
        self.original_text = None

    def highlight(self, pos, all_keys):
        """
        Cette fonction surligne ou dé-surligne les mots-clés avec leur phrase. La méthode utilise le module Input
        afin de vérifier les entrées dans le clavier et faire les selection selon ces entrées.

        Si la touche CONTROL est enfoncée, la selection est multiple.
        Si la touche SHIFT est enfoncée, la selection des élément entre le dernier surlignage et la position de la click
        est automatique
        Si aucun de ces deux touche n'est enfoncée, la selection est simple (un élément à la fois).

        Cette méthode fonction block toute modification du block des notes et des mots-clés et dé-block ceux-ci
        quand aucun élément n'est sélectionné.

        :param pos : position de la clique dans l'écran (QPoint)
        :param all_keys : liste des idées
        """

        self.all_keys = all_keys

        if self.original_text is None:  # si le document est nul, alors c'est la 1ère opération de surlignage.
            self.original_text = QTextEdit()
            self.original_text.setHtml(self.notes_text.toHtml())


        if Input.is_pressed(Qt.Key.Key_Control):
            self.__highlight_key(pos, True, True)

        elif Input.is_pressed(Qt.Key.Key_Shift):
            self.__highlight_from_to(pos)

        else:
            self.__clear_highlights(pos)
            self.__highlight_key(pos, True, True)


        if len(self.highlights) == 0:  # S'il n'y plus aucun surlignage, libérer le text
            self.original_text = None
            self.set_freeze(False)
            self.last_highlight_pos = 0
            return

        self.set_freeze(True)  # On ne peut pas modifier le text des notes qui contient des idées surlignées

    def __clear_highlights(self, exception):
        """
        Cette fonction efface tous les surlignages sauf si le seul surlignage actuel est celui de la position
        d'exception donnée en paramètre.
        :param exception : position du click d'exception
        """

        if len(self.highlights) == 1:
            keys_cursor = self.keys_text.cursorForPosition(exception)
            keys_cursor.movePosition(QTextCursor.MoveOperation.WordLeft)
            exception = keys_cursor.position()

            if self.highlights.keys()[0] == exception:
                return

        while len(self.highlights) != 0:
            pos = self.highlights.keys()[0]
            self.__highlight_key(pos, False, False)

    def __rehighlight(self):
        """
        Cette fonction re-surligne tous les éléments de la liste de surlignage
        """
        for pos in self.highlights.keys():
            self.__highlight_key(pos, True, False)

    def __highlight_key(self, pos, to_highlight, double_check_to_highlight):
        """
        Cette fonction cherche le mot-clé à la position donnée en paramètre et le surligne.
        Si le mot est déjà surligné, la fonction efface le surlignage.
        Si l'appel de la fonction n'exige pas ne pas vérifier l'état de surlignage de mot,
        alors l'opération désirée (surlignage ou dé-surlignage) sera effectuée sur le mot sans vérifier l'état précédent
        de ce mot.

        Remarque : quand l'appel de fonction exige de vérifier l'état précédent du mot,
        l'opération désirée (surlignage ou dé-surlignage) pourrait être modifié afin d'opposer l'état précédent.

        :param pos: position de la click ou du curseur
        :param to_highlight : boolean qui indique si le mot à position est à surligné ou non
        :param double_check_to_highlight : boolean qui indique de vérifier ou non l'état précèdent du mot
        """

        keys_cursor = self.keys_text.textCursor()
        if type(pos) == QPoint:  # si la position donnée est celle de la click de souris
            keys_cursor = self.keys_text.cursorForPosition(pos)
            keys_cursor.movePosition(QTextCursor.MoveOperation.WordLeft)
            highlight_pos = keys_cursor.position()

        else:  # Si la position donnée est celle d'un curseur
            keys_cursor.setPosition(pos)
            highlight_pos = pos

        keys_cursor.movePosition(QTextCursor.MoveOperation.NextWord, QTextCursor.MoveMode.KeepAnchor)
        keyword = keys_cursor.selectedText().strip()
        line = keys_cursor.blockNumber()

        if double_check_to_highlight:
            # verifications - pourrait modifier l'opération désirée sur le mot afin de s'opposer à l'état précédent :
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
        """
        Cette méthode cherche la phrase associée au mot-clé et à la ligne donnée en paramètre et la surligne.
        (ou efface le surlignage)
        Cette fonction modifie la liste des éléments surlignés.

        :param highlight_pos : position du mot clé (dans le block text des mot-clés.
        :param line : ligne de la phrase du mot-clé.
        :param to_highlight : boolean qui indique si la phrase est à surligner ou non
        :param double_check : boolean qui indique si l'appel de la fonction est causé directement par l'utilisateur.
        """
        if phrase.strip() == '':  # Si le mot-clé n'est pas associé à une phrase
            if to_highlight:  # Si l'opération exigée est le surlignage, ajouter l'élément à la liste
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
                self.__rehighlight()

        cursor.clearSelection()
        self.notes_text.setTextCursor(cursor)

    def __highlight_from_to(self, clic_pos):
        """
        Cette fonction surligne (ou non) tous les éléments entre la dernière surlignée à la position de click de souris.
        :param clic_pos: position de click de souris (QPoint)
        """

        cursor = self.keys_text.cursorForPosition(clic_pos)
        cursor.movePosition(QTextCursor.MoveOperation.WordLeft)
        clic_pos = cursor.position()


        if clic_pos > self.last_highlight_pos:
            first_pos = self.last_highlight_pos
            last_pos = clic_pos
        else:
            first_pos = clic_pos
            last_pos = self.last_highlight_pos

        cursor.setPosition(first_pos)
        cursor.movePosition(QTextCursor.MoveOperation.WordLeft)
        pos = cursor.position()

        while pos <= last_pos:
            pos = cursor.position()
            cursor.movePosition(QTextCursor.MoveOperation.NextWord)
            self.__highlight_key(pos, True, False)