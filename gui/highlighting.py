from PyQt6.QtWidgets import QTextEdit
from sortedcontainers import SortedDict


highlights = SortedDict()


def highlight(keys_text: QTextEdit, notes_text: QTextEdit, phrase, line):
    highlights[line] = phrase

