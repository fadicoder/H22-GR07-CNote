from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
import sys



app = QApplication(sys.argv)


class Window(QMainWindow):

    def __init__(self):

        super().__init__()

        self.summery_text = QPlainTextEdit()
        self.notes_text = QPlainTextEdit()
        self.keywords_text = QPlainTextEdit()
        self.headLines_text = QPlainTextEdit()

        self.menubar = self.__menubar()
        self.menubar.setVisible(False)
        self.setMenuBar(self.menubar)

        self.widgets_lst = QStackedWidget()
        self.setCentralWidget(self.widgets_lst)
        self.setWindowTitle("C-Note")

        self.notes_widget = self.__notes_widget()
        self.welcome_widget = self.__welcome_widget()
        self.widgets_lst.addWidget(self.notes_widget)
        self.widgets_lst.addWidget(self.welcome_widget)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)

    def __menubar(self):

        save_act = QAction('Save', self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('Saving...')
        save_act.triggered.connect(self.save)

        menubar = QMenuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addActions([save_act])

        return menubar


    def __welcome_widget(self):

        welcome_widget = QWidget()
        root = QVBoxLayout()
        welcome_widget.setLayout(root)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setFont(QFont('None', 12))
        self.username_input.setMaximumWidth(400)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setFont(QFont('None', 12))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaximumWidth(400)

        buttons = QHBoxLayout()
        self.login_btn = QPushButton('Log in')
        self.signup_btn = QPushButton('Sign up')
        buttons.addWidget(self.login_btn)
        buttons.addWidget(self.signup_btn)
        self.login_btn.clicked.connect(self.login)

        root.addWidget(self.username_input)
        root.addWidget(self.password_input)
        root.addSpacing(20)
        root.addLayout(buttons)

        root.setAlignment(Qt.AlignCenter)

        self.grabKeyboard = self.enter_login
        return welcome_widget

    def __notes_widget(self):

        notes_widget = QTabWidget()
        root = QVBoxLayout()
        notes_widget.setLayout(root)

        title = QLabel('C-Note')
        title.setFont(QFont("None", 20))
        root.addSpacerItem(QSpacerItem(0, 25))
        root.addWidget(title, 0, Qt.AlignCenter)
        root.addSpacerItem(QSpacerItem(0, 25))

        texts_layout = QVBoxLayout()
        texts_layout.setAlignment(Qt.AlignCenter)
        middle_text_layout = QHBoxLayout()
        middle_text_layout.setAlignment(Qt.AlignVCenter)

        self.headLines_text.setFont(QFont('None', 12))
        self.headLines_text.setMaximumHeight(100)
        self.headLines_text.setPlaceholderText('Write your headlines here...')
        self.keywords_text.setMaximumWidth(400)
        self.keywords_text.setFont(QFont('None', 12))
        self.keywords_text.setPlaceholderText('Write yout keywords here...')
        self.notes_text.setFont(QFont('None', 12))
        self.notes_text.setPlaceholderText('Write your notes here...')
        self.summery_text.setMaximumHeight(100)
        self.summery_text.setFont(QFont('None', 12))
        self.summery_text.setPlaceholderText('Write your summery here...')

        texts_layout.addWidget(self.headLines_text)
        middle_text_layout.addWidget(self.keywords_text)
        middle_text_layout.addWidget(self.notes_text)
        texts_layout.addLayout(middle_text_layout)
        texts_layout.addWidget(self.summery_text)
        root.addLayout(texts_layout)

        return notes_widget

    def launch(self):
        self.showMaximized()
        sys.exit(app.exec())

    def login(self):
        """ verifie if password matches username :"""
        self.menubar.setVisible(True)
        self.widgets_lst.setCurrentWidget(self.notes_widget)

    def show_welcom_page(self):
        self.menubar.setVisible(False)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)

    def enter_login(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Enter:
            self.login()

    def save(self):
        print("Save!")

