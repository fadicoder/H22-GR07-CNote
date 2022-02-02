from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
import sys



app = QApplication(sys.argv)


class Window(QWidget):
    def __init__(self):

        super().__init__()


        self.setWindowTitle("C-Note")
        self.setGeometry(0, 0, 650, 400)
        root = QVBoxLayout()
        self.setLayout(root)

        title = QLabel('C-Note')
        title.setFont(QFont("None", 25))
        root.addWidget(title, 0, Qt.AlignCenter)

        texts_layout = QVBoxLayout()
        texts_layout.setAlignment(Qt.AlignCenter)
        middle_text_layout = QHBoxLayout()
        middle_text_layout.setAlignment(Qt.AlignVCenter)

        self.headLines_text = QTextEdit()
        self.keywords_text = QTextEdit()
        self.notes_text = QTextEdit()
        self.summery_text = QTextEdit()

        texts_layout.addWidget(self.headLines_text)
        middle_text_layout.addWidget(self.keywords_text)
        middle_text_layout.addWidget(self.notes_text)
        texts_layout.addLayout(middle_text_layout)
        texts_layout.addWidget(self.summery_text)
        root.addLayout(texts_layout)

    def launch(self):
        self.show()
        app.exec()
