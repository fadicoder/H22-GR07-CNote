from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QBrush, QColorConstants, QTextCursor
import cursoroperations as co
from sortedcontainers import SortedDict


class Highlighter(QSyntaxHighlighter):

    STANDARD_FORMAT = QTextCharFormat()
    STANDARD_FORMAT.setBackground(QBrush(QColorConstants.Yellow))

    def __init__(self, parent_text):
        super().__init__(parent_text)
        self.text = parent_text
        self.phrases = SortedDict()


    def highlightBlock(self, phrase):

        cursor: QTextCursor = self.text.textCursor()
        line = cursor.selectionStart()
        start = co.get_start_of_phrase(cursor, phrase, line)

        pos = self.phrases.bisect(phrase) - 1
        in_dict = True if pos != len(self.phrases) and self.phrases.keys()[pos] == phrase else False

        if in_dict:
            self.phrases.popitem(pos)
            self.rehighlight()
        else:
            self.phrases[start] = phrase
            self.setFormat(start, phrase, Highlighter.STANDARD_FORMAT)



    def rehighlight(self) -> None:

        self.text.setTextBackgroundColor(QColorConstants.White)

        for pos, phrase in self.phrases:
            self.setFormat(pos, phrase, Highlighter.STANDARD_FORMAT)



