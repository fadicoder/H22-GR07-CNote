import dictmanager
import sys
import notes
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *


class Window(QMainWindow):

    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()

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

        self.genrated_keys = []
        self.added_keys = []
        self.all_keys = []

        self.addToolBar(self.main_toolbar)

    def __init_menubar(self):
        """
        Initializing the elements of the menubar
        """
        save_act = QAction('Save', self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('Saving...')
        save_act.triggered.connect(self.save)

        load_act = QAction('Load', self)
        load_act.setShortcut('Ctrl+L')
        load_act.triggered.connect(self.load)

        sign_out_act = QAction('Sign out', self)
        sign_out_act.triggered.connect(self.show_welcome_page)

        exit_act = QAction('exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.app.exit)

        file_menu = self.menubar.addMenu('File')
        file_menu.addAction(exit_act)

        account_menu = self.menubar.addMenu('Account')
        account_menu.addAction(save_act)
        account_menu.addAction(load_act)
        account_menu.addSeparator()
        account_menu.addAction(sign_out_act)

    def __init_toolbar(self):

        font_bar = QToolBar()

        self.size_spin = QSpinBox()
        self.size_spin.setValue(15)
        self.size_spin.valueChanged.connect(self.__set_font_size)

        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.__set_font_family)

        font_bar.addWidget(self.size_spin)
        font_bar.addWidget(self.font_combo)

        align_left_act = QAction(QIcon('resources/AlignLeft.png'), 'Align left', self)
        align_center_act = QAction(QIcon('resources/AlignCenter.png'), 'Align center', self)
        align_right_act = QAction(QIcon('resources/AlignRight.png'), 'Align right', self)
        align_justify_act = QAction(QIcon('resources/AlignJustify.png'), 'Justify', self)
        align_left_act.triggered.connect(lambda: self.__current_widget().setAlignment(Qt.AlignLeft))
        align_center_act.triggered.connect(lambda: self.__current_widget().setAlignment(Qt.AlignCenter))
        align_right_act.triggered.connect(lambda: self.__current_widget().setAlignment(Qt.AlignRight))
        align_justify_act.triggered.connect(lambda: self.__current_widget().setAlignment(Qt.AlignJustify))

        alignment_bar = QToolBar()
        alignment_bar.addActions([align_left_act, align_center_act, align_right_act, align_justify_act])

        self.main_toolbar.addWidget(font_bar)
        self.main_toolbar.addWidget(alignment_bar)

    def __current_widget(self):



        if self.headLines_text.hasFocus():
            return self.headLines_text
        if self.notes_text.hasFocus():
            print('note')
            return self.notes_text
        if self.summery_text.hasFocus():
            print('summery')
            return self.summery_text

        return QTextEdit()

    def __welcome_widget(self):
        """
        Built the graphical user interface
        :return: the built welcome widget
        """
        welcome_widget = QWidget()
        root = QVBoxLayout()
        welcome_widget.setLayout(root)

        # Initilizing widget elements
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.login_btn = QPushButton('Log in')
        self.signup_btn = QPushButton('Sign up')
        self.__welcome_wid_properties()

        # Organizing elements in layouts
        buttons = QHBoxLayout()
        buttons.addWidget(self.login_btn)
        buttons.addWidget(self.signup_btn)
        root.addWidget(self.username_input)
        root.addWidget(self.password_input)
        root.addSpacing(20)
        root.addLayout(buttons)
        root.setAlignment(Qt.AlignCenter)

        # setting on events
        self.login_btn.clicked.connect(self.login)

        return welcome_widget

    def __welcome_wid_properties(self):
        """
        setting properties of the welcome widget elements.
        """
        self.username_input.setPlaceholderText('Username')
        self.username_input.setFont(QFont('None', 12))
        self.username_input.setMaximumWidth(400)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setFont(QFont('None', 12))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaximumWidth(400)

    def __notes_widget(self):
        """
        Building note's widget graphical interface
        :return: note's widget
        """

        notes_widget = QTabWidget()
        keywords_widget = QWidget(self)
        root = QVBoxLayout()
        notes_widget.setLayout(root)

        # Initilizing widget elements
        self.summery_text = QTextEdit()
        self.notes_text = QTextEdit()
        self.keywords_text = QTextEdit()
        self.headLines_text = QTextEdit()
        self.keyword_line = QLineEdit()
        self.add_btn = QPushButton('Add keyword')
        self.generate_btn = QPushButton('Generate')
        self.__notes_wid_properties()

        # Organizing elements in layouts
        texts_layout = QVBoxLayout()
        texts_layout.setAlignment(Qt.AlignCenter)
        middle_text_layout = QHBoxLayout()
        middle_text_layout.setAlignment(Qt.AlignVCenter)
        texts_layout.addWidget(self.headLines_text)
        keywords_layout = QVBoxLayout(keywords_widget)
        keywords_layout.addWidget(self.keywords_text)
        add_key_layout = QHBoxLayout()
        add_key_layout.addWidget(self.keyword_line)
        add_key_layout.addWidget(self.add_btn)
        add_key_layout.addWidget(self.generate_btn)
        keywords_layout.addLayout(add_key_layout)
        notes_widget.setLayout(keywords_layout)
        middle_text_layout.addWidget(keywords_widget, 2)
        middle_text_layout.addWidget(self.notes_text, 10)
        texts_layout.addLayout(middle_text_layout)
        texts_layout.addWidget(self.summery_text)
        bottom_submit_btn = QHBoxLayout()
        bottom_submit_btn.setAlignment(Qt.AlignRight)
        texts_layout.addLayout(bottom_submit_btn)
        root.addLayout(texts_layout)

        # settings on events actions
        self.__set_on_events_notes_wid()

        return notes_widget

    def __notes_wid_properties(self):
        """
        Initialize note's widget properties
        """
        self.headLines_text.setMaximumHeight(100)
        self.notes_text.setFont(QFont('None', 15))
        self.headLines_text.setPlaceholderText('Write your headlines here...')
        self.headLines_text.setFont(QFont('None', 15))
        self.keywords_text.setReadOnly(True)
        self.keywords_text.setPlaceholderText('Click on generate to generate your keywords')
        self.keywords_text.setFont(QFont('None', 15))
        self.notes_text.setPlaceholderText('Write your notes here...')
        self.summery_text.setMaximumHeight(150)
        self.summery_text.setPlaceholderText('Write your summery here...')
        self.summery_text.setFont(QFont('None', 15))
        self.notes_text.setLineWrapMode(QTextEdit.NoWrap)

    def __set_on_events_notes_wid(self):
        self.notes_text.verticalScrollBar().valueChanged.connect(self.__move_keys_bar)
        self.notes_text.verticalScrollBar().valueChanged.connect(self.__move_notes_bar)
        self.add_btn.clicked.connect(lambda: self.write_keys(self.keyword_line.text()))
        self.generate_btn.clicked.connect(
            lambda: self.write_keys(dictmanager.get_ideas(self.notes_text.toPlainText(), self.get_max_fonts()))
        )
        self.summery_text.cursorPositionChanged.connect(self.__init_shown_font)
        self.notes_text.cursorPositionChanged.connect(self.__init_shown_font)
        self.keywords_text.cursorPositionChanged.connect(self.__init_shown_font)

    def __set_font_size(self):
        self.__current_widget().setFontPointSize(self.size_spin.value())

    def __set_font_family(self):
        self.__current_widget().setFontFamily(self.font_combo.currentFont().family())

    def enable_keyword(self):
        if self.notes_text.selectionChanged():
            self.add_btn.setEnabled(True)
        else:
            self.add_btn.setEnabled(False)

    def __add_keyword(self, new_key):
        self.added_keys.append(new_key)

        self.added_keys.sort(key=dictmanager.get_ideas)

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

        sumtext = self.summery_text.toHtml()
        headtext = self.headLines_text.toHtml()
        maintext = self.notes_text.toHtml()
        notes.Notes.notessaves(maintext, sumtext, headtext)

    def load(self):
        print('Loading...')

    def write_keys(self, keys):
        """
        This function write the list of ideas given in argument in the keywords_text.
        :param keys: list of ideas to write
        """
        if len(keys) == 0:
            return

        elif type(keys) == list:

            for key in keys:
                last_font = self.keywords_text.font()
                self.keywords_text.insertPlainText(str(key))
                print(str(key))
                self.keywords_text.setCurrentFont(key.max_font)
                self.keywords_text.insertPlainText(' ')
                self.keywords_text.setCurrentFont(last_font)
                self.keywords_text.insertPlainText('\n')

    def get_max_fonts(self):
        """
        This calculates the biggest font of each line and return thess fonts.
        :return: A list of the biggest font of each line.
        """

        doc = self.notes_text.document()
        self.notes_text.moveCursor(QTextCursor.Start)
        max_fonts = []

        for i in range(doc.lineCount()):

            current_font = self.notes_text.currentFont()
            max_font = current_font



            # This second for loop calculates the biggest font of the line "i"
            for j in range(doc.findBlockByLineNumber(i).length()-1):
                print(str(doc.findBlockByLineNumber(i)))
                self.notes_text.moveCursor(QTextCursor.NextCharacter)
                current_font = self.notes_text.currentFont()
                if current_font.pointSize() > max_font.pointSize():
                    max_font = self.notes_text.currentFont()

            max_fonts.append(max_font)
            self.notes_text.moveCursor(QTextCursor.NextBlock)

        return max_fonts

    def __init_shown_font(self):
        current_font = self.__current_widget().currentFont()

        self.font_combo.setCurrentFont(current_font)
        self.size_spin.setValue(current_font.pointSize())

    def __move_keys_bar(self):
        pos = self.notes_text.verticalScrollBar().sliderPosition()
        self.keywords_text.verticalScrollBar().setSliderPosition(pos)

    def __move_notes_bar(self):
        pos = self.keywords_text.verticalScrollBar().sliderPosition()
        self.notes_text.verticalScrollBar().setSliderPosition(pos)

    def launch(self):
        """
        Launching the program!
        """
        self.showMaximized()
        sys.exit(self.app.exec())
