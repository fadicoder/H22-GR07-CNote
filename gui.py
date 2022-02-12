from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
import sys
import dictmanager


class Window(QMainWindow):

    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()

        self.summery_text = QTextEdit()
        self.notes_text = QTextEdit()
        self.keywords_text = QTextEdit()
        self.headLines_text = QTextEdit()

        self.widgets_lst = QStackedWidget()
        self.setCentralWidget(self.widgets_lst)
        self.setWindowTitle("C-Note")

        self.notes_widget = self.__notes_widget()
        self.welcome_widget = self.__welcome_widget()
        self.widgets_lst.addWidget(self.notes_widget)
        self.widgets_lst.addWidget(self.welcome_widget)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)

        self.menubar = QMenuBar()
        self.__init_menubar()
        self.menubar.setVisible(False)
        self.setMenuBar(self.menubar)

        self.main_toolbar = QToolBar()
        self.__init_toolbar()

        self.addToolBar(self.main_toolbar)

    def __init_menubar(self):
        save_act = QAction('Save', self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('Saving...')
        save_act.triggered.connect(self.save)

        signout_act = QAction('Sign out', self)
        signout_act.triggered.connect(self.show_welcome_page)

        exit_act = QAction('exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.app.exit)

        file_menu = self.menubar.addMenu('File')
        file_menu.addAction(exit_act)

        account_menu = self.menubar.addMenu('Account')
        account_menu.addAction(save_act)
        account_menu.addSeparator()
        account_menu.addAction(signout_act)

    def __init_toolbar(self):

        self.size_spin = QSpinBox()
        self.size_spin.setValue(15)
        self.size_spin.valueChanged.connect(self.__set_Font)

        self.main_toolbar.addWidget(self.size_spin)

    def __current_widget(self):

        if self.notes_text.isActiveWindow():
            return self.notes_text
        if self.summery_text.isActiveWindow():
            return self.summery_text
        if self.headLines_text.isActiveWindow():
            return self.headLines_text

    def __set_Font(self):
        wid = self.__current_widget()
        wid.setCurrentFont(QFont('None', self.size_spin.value()))

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

        return welcome_widget

    def __notes_widget(self):

        notes_widget = QTabWidget()
        keywords_widget = QWidget(self)
        root = QVBoxLayout()
        notes_widget.setLayout(root)

        title = QLabel('C-Note')
        title.setFont(QFont('None', 20))
        root.addSpacerItem(QSpacerItem(0, 25))
        root.addWidget(title, 0, Qt.AlignCenter)
        root.addSpacerItem(QSpacerItem(0, 25))

        texts_layout = QVBoxLayout()
        texts_layout.setAlignment(Qt.AlignCenter)
        middle_text_layout = QHBoxLayout()
        middle_text_layout.setAlignment(Qt.AlignVCenter)


        self.headLines_text.setMaximumHeight(100)
        self.notes_text.setFont(QFont('None', 15))
        self.headLines_text.setPlaceholderText('Write your headlines here...')
        self.headLines_text.setFont(QFont('None', 15))
        self.keywords_text.setReadOnly(True)
        self.keywords_text.setPlaceholderText('Click on generate to generate your keywords')
        self.keywords_text.setFont(QFont('None', 15))
        self.notes_text.setPlaceholderText('Write your notes here...')
        self.summery_text.setMaximumHeight(100)
        self.summery_text.setPlaceholderText('Write your summery here...')
        self.summery_text.setFont(QFont('None', 15))
        self.keyword_line = QLineEdit()
        self.add_btn = QPushButton('Add keyword')
        generate_btn = QPushButton('Generate')
        submit_btn = QPushButton('Submit')
        submit_btn.setMaximumWidth(50)

        self.notes_text.setLineWrapMode(QTextEdit.NoWrap)
        self.add_btn.clicked.connect(lambda: self.add_keyword(self.keyword_line.text()))
        generate_btn.clicked.connect(
            lambda: self.add_keyword(dictmanager.get_ideas(self.notes_text.toPlainText(), self.get_max_fonts()))
        )

        texts_layout.addWidget(self.headLines_text)

        keywords_layout = QVBoxLayout(keywords_widget)
        keywords_layout.addWidget(self.keywords_text)
        add_key_layout = QHBoxLayout()
        add_key_layout.addWidget(self.keyword_line)
        add_key_layout.addWidget(self.add_btn)
        add_key_layout.addWidget(generate_btn)

        keywords_layout.addLayout(add_key_layout)
        notes_widget.setLayout(keywords_layout)
        middle_text_layout.addWidget(keywords_widget, 2)
        middle_text_layout.addWidget(self.notes_text, 10)
        texts_layout.addLayout(middle_text_layout)
        texts_layout.addWidget(self.summery_text)
        bottom_submit_btn = QHBoxLayout()
        bottom_submit_btn.addWidget(submit_btn)
        bottom_submit_btn.setAlignment(Qt.AlignRight)
        texts_layout.addLayout(bottom_submit_btn)

        root.addLayout(texts_layout)

        return notes_widget

    def enable_keyword(self):
        if self.notes_text.selectionChanged():
            self.add_btn.setEnabled(True)
        else:
            self.add_btn.setEnabled(False)

    def login(self):
        self.menubar.setVisible(True)
        self.widgets_lst.setCurrentWidget(self.notes_widget)

    def show_welcome_page(self):
        self.menubar.setVisible(False)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)

    def enter_login(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Enter:
            self.login()

    def save(self):
        print("Save!")

    def add_keyword(self, keys):

        if len(keys) == 0:
            return

        new_text = ''
        if type(keys) == str:
            new_text = keys + '\n'
            self.keyword_line.clear()

        elif type(keys) == list:

            new_text = ''
            for key in keys:
                last_font = self.keywords_text.font()
                self.keywords_text.append(str(key))
                self.keywords_text.setCurrentFont(key.max_font)
                self.keywords_text.append(' ')
                self.keywords_text.setCurrentFont(last_font)

        text = self.keywords_text.toPlainText() + new_text
        self.keywords_text.setPlainText(text)

    def get_max_fonts(self):
        doc = self.notes_text.document()
        self.notes_text.moveCursor(QTextCursor.Start)
        max_fonts = []
        for i in range(doc.lineCount()):

            current_font = self.notes_text.currentFont()
            max_font = current_font

            # The next five line calculate the biggest font of each line
            for j in range(doc.findBlockByNumber(i).length()):
                self.notes_text.moveCursor(QTextCursor.NextCharacter)
                current_font = self.notes_text.currentFont()
                if current_font.pointSize() > max_font.pointSize():
                    max_font = self.notes_text.currentFont()

            max_fonts.append(max_font)
            self.notes_text.moveCursor(QTextCursor.NextBlock)

        return max_fonts

    def launch(self):
        self.showMaximized()
        sys.exit(self.app.exec())




