from gui import cursoroperations as co
from idea import Idea
from gui.highlighting import HighlightingSystem
from account import Account, Error
from notes import Notes
import dictmanager as dm
import os
import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *

'''
- extract
- delete 1 selected idea + with no phrase
- change doc.blockCount() to count(\n)

- generate keys with selection bug
- sign up page same page???
- docs
- translate to french

- adjust repair
- highlighting bug
- test laod and save as
- create table if not exists
- donc allow up down selection when no selection
- change to document.defaultFont()
- do things with selection
'''


class MainWindow(QMainWindow):
    DEFAULT_FONT = QFont('Calibri', 15)

    def __init__(self):

        self.highlighter = None
        self.summery_text = None
        self.notes_text = None
        self.keywords_text = None
        self.headLines_text = None
        self.notes = None
        self.account = Account()

        self.app = QApplication(sys.argv)
        super().__init__()
        self.widgets_lst = QStackedWidget()
        self.setCentralWidget(self.widgets_lst)
        self.setWindowTitle("C-Note")
        self.notes_dict = dict()

        self.notes_page = self.__notes_page()
        self.welcome_widget = self.__welcome_page()
        self.widgets_lst.addWidget(self.notes_page)
        self.widgets_lst.addWidget(self.welcome_widget)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)

        self.highlight_color = QColorConstants.Cyan
        self.text_color = QColorConstants.Red
        self.menubar = QMenuBar()
        self.__init_menubar()
        self.menubar.setVisible(False)
        self.setMenuBar(self.menubar)

        self.main_toolbar = QToolBar()
        self.__init_toolbar()
        self.main_toolbar.setVisible(False)
        self.addToolBar(self.main_toolbar)

        self.generated_keys = []
        self.added_keys = []
        self.all_keys = self.generated_keys + self.added_keys
        self.last_text = self.notes_text

    def __init_menubar(self):
        """
        Initialise les éléments de la bare de menu.
        """
        save_act = QAction('Save', self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('Saving...')
        save_act.triggered.connect(self.save)

        save_as_act = QAction('Save as', self)
        save_as_act.setShortcut('Ctrl+Shift+S')
        save_as_act.setStatusTip('Saving...')
        save_as_act.triggered.connect(self.save_as)

        save_on_cloud_act = QAction('Save on cloud', self)
        save_on_cloud_act.triggered.connect(lambda: self.save_on_cloud(True))

        load_act = QAction('Load', self)
        load_act.setShortcut('Ctrl+L')
        load_act.triggered.connect(lambda: self.create_note(from_disk=True))

        export_docs_act = QAction('Export to .docx', self)
        export_docs_act.triggered.connect(self.save_on_disk_docx)

        self.clear_text_act = QAction('Clear all notes', self)
        self.clear_text_act.triggered.connect(self.clear_notes)

        sign_out_act = QAction('Sign out', self)
        sign_out_act.triggered.connect(self.sign_out)

        exit_act = QAction('Save and exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.closeEvent)

        edit_username_act = QAction('Edit username', self)
        edit_username_act.triggered.connect(self.prompt_username)
        edit_pwd_act = QAction('Edit password', self)
        edit_pwd_act.triggered.connect(self.prompt_password)

        adjust_keys_act = QAction('Adjust keywords with text', self)
        adjust_keys_act.setShortcut('F5')
        adjust_keys_act.triggered.connect(self.adjust_keys_with_notes)

        insert_image_act = QAction('Insert image', self)
        insert_image_act.triggered.connect(self.insert_image)

        generate_act = QAction('Generate keywords', self)
        generate_act.setShortcut('Ctrl+G')
        generate_act.triggered.connect(self.generate)
        clear_gen_keys_act = QAction('Clear generated keywords', self)
        clear_gen_keys_act.triggered.connect(self.clear_gen_keys)
        clear_added_keys_act = QAction('Clear added keywords', self)
        clear_added_keys_act.triggered.connect(self.clear_added_keys)
        clear_all_keys_act = QAction('Clear all keywords', self)
        clear_all_keys_act.triggered.connect(self.clear_all_keys)

        account_menu = self.menubar.addMenu('Account')
        account_menu.addAction(edit_username_act)
        account_menu.addAction(edit_pwd_act)
        account_menu.addSeparator()
        account_menu.addAction(sign_out_act)
        account_menu.addAction(exit_act)

        self.file_menu = self.menubar.addMenu('File')
        self.file_menu.addAction(save_act)
        self.file_menu.addAction(save_as_act)
        self.file_menu.addAction(save_on_cloud_act)
        self.file_menu.addAction(load_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_docs_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.clear_text_act)


        self.insert_menu = self.menubar.addMenu('Insert')
        self.insert_menu.addAction(insert_image_act)

        self.keywords_menu = self.menubar.addMenu('Keywords')
        self.keywords_menu.addAction(generate_act)
        self.keywords_menu.addSeparator()
        self.keywords_menu.addActions([clear_added_keys_act, clear_gen_keys_act, clear_all_keys_act])
        self.keywords_menu.addSeparator()
        self.keywords_menu.addAction(adjust_keys_act)
    def save_on_disk_docx(self):
        sumtext = self.summery_text.toHtml()
        headtext = self.headLines_text.toHtml()
        maintext = self.notes_text.toHtml()
        genekeys = self.generated_keys
        adkeys = self.added_keys
        self.notes.save_on_disk_docx(maintext, sumtext, headtext, genekeys, adkeys)
    def __init_toolbar(self):

        self.keyword_line = QLineEdit()
        self.keyword_line.setMaximumWidth(250)
        self.keyword_line.setPlaceholderText('Add keyword')
        self.keyword_line.setAcceptDrops(False)
        self.keyword_line.keyPressEvent = self.add_key_line_press_event

        self.size_spin = QSpinBox()
        self.size_spin.setValue(MainWindow.DEFAULT_FONT.pointSize())
        self.size_spin.valueChanged.connect(lambda: self.last_text.setFontPointSize(self.size_spin.value()))

        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(MainWindow.DEFAULT_FONT)
        self.font_combo.currentFontChanged.connect(
            lambda: self.last_text.setFontFamily(self.font_combo.currentFont().family()))

        align_left_act = QAction(QIcon('resources/AlignLeft.png'), 'Align left', self)
        align_center_act = QAction(QIcon('resources/AlignCenter.png'), 'Align center', self)
        align_right_act = QAction(QIcon('resources/AlignRight.png'), 'Align right', self)
        align_left_act.triggered.connect(lambda: self.last_text.setAlignment(Qt.AlignmentFlag.AlignLeft))
        align_center_act.triggered.connect(lambda: self.last_text.setAlignment(Qt.AlignmentFlag.AlignCenter))
        align_right_act.triggered.connect(lambda: self.last_text.setAlignment(Qt.AlignmentFlag.AlignRight))

        self.bold_act = QAction(QIcon('resources/Bold.png'), 'Bold text', self)
        self.italic_act = QAction(QIcon('resources/Italic.png'), 'Italic text', self)
        self.underline_act = QAction(QIcon('resources/Underline.png'), 'Underline text', self)
        self.bold_act.setCheckable(True)
        self.italic_act.setCheckable(True)
        self.underline_act.setCheckable(True)

        def bold(checked: bool):
            if checked:
                self.last_text.setFontWeight(QFont.Weight.Bold)
            else:
                self.last_text.setFontWeight(QFont.Weight.Normal)

        self.bold_act.triggered.connect(bold)
        self.italic_act.triggered.connect(lambda checked: self.last_text.setFontItalic(checked))
        self.underline_act.triggered.connect(lambda checked: self.last_text.setFontUnderline(checked))

        highlight_pixmap = QPixmap(100, 100)
        highlight_pixmap.fill(self.highlight_color)
        text_color_pixmap = QPixmap(100, 100)
        text_color_pixmap.fill(self.text_color)
        self.highlight_act = QAction(QIcon('resources/Highlight.png'), 'Highlight', self)
        self.highlight_color_picker_act = QAction(QIcon(highlight_pixmap), 'Highlighter color picker', self)
        self.text_color_act = QAction(QIcon('resources/TextColor.png'), 'Color Text', self)
        self.text_color_picker_act = QAction(QIcon(text_color_pixmap), 'Text color picker', self)
        self.highlight_color_picker_act.triggered.connect(lambda: self.select_color(True))
        self.text_color_picker_act.triggered.connect(lambda: self.select_color(False))
        self.highlight_act.triggered.connect(lambda: self.color(True))
        self.text_color_act.triggered.connect(lambda: self.color(False))

        self.main_toolbar.setStyleSheet("QToolBar{spacing:45px;}")
        self.main_toolbar.addWidget(self.keyword_line)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addWidget(self.font_combo)
        self.main_toolbar.addWidget(self.size_spin)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addActions([align_left_act, align_center_act, align_right_act])
        self.main_toolbar.addSeparator()
        self.main_toolbar.addActions([self.bold_act, self.italic_act, self.underline_act])
        self.main_toolbar.addSeparator()
        self.main_toolbar.addActions([self.highlight_act, self.highlight_color_picker_act])
        self.main_toolbar.addSeparator()
        self.main_toolbar.addActions(([self.text_color_act, self.text_color_picker_act]))

        # self.notes_highlighter.highlightBlock(self.notes_text.textCursor().selection().toPlainText()))

    def __welcome_page(self):
        """
        Construit l'interface graphique du widget de bienvenue.
        :return : le widget de bienvenue
        """
        welcome_widget = QWidget()
        root = QVBoxLayout()
        welcome_widget.setLayout(root)

        # Initialise les widgets
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.login_btn = QPushButton('Log in')
        self.signup_btn = QPushButton('Sign up')
        self.error_label = QLabel()
        self.__welcome_page_properties()

        # Organise les éléments
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.signup_btn)
        root.addWidget(self.username_input)
        root.addWidget(self.password_input)
        root.addWidget(self.error_label)
        root.addSpacing(20)
        root.addLayout(buttons_layout)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # action au clic
        self.login_btn.clicked.connect(self.log_in)
        self.password_input.keyPressEvent = self.password_line_key_event
        self.username_input.keyPressEvent = self.username_line_key_event
        self.signup_btn.clicked.connect(self.sign_up)

        return welcome_widget

    def __welcome_page_properties(self):
        """
        Cette méthode établit les propriétés des widgets de bienvenue.
        """
        self.username_input.setPlaceholderText('Username')
        self.username_input.setFont(MainWindow.DEFAULT_FONT)
        self.username_input.setMaximumWidth(400)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setFont(MainWindow.DEFAULT_FONT)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMaximumWidth(400)
        self.error_label.setFont(self.DEFAULT_FONT)
        self.error_label.setStyleSheet('color: red')

    def __notes_page(self):

        notes_page = QTabWidget()

        first_tab = QWidget()
        layout = QVBoxLayout()
        first_tab.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_page.setTabsClosable(True)

        self.create_note_btn = QPushButton('New notes')
        self.notes_combo = QComboBox()
        self.open_selected_notes_btn = QPushButton('Open selected notes')
        self.load_btn = QPushButton('Load notes from disk')
        self.fill_notes_combo()

        layout.addWidget(self.create_note_btn)
        choose_notes_layout = QHBoxLayout()
        choose_notes_layout.addWidget(self.notes_combo)
        choose_notes_layout.addWidget(self.open_selected_notes_btn)
        layout.addSpacing(50)
        layout.addLayout(choose_notes_layout)
        layout.addSpacing(50)
        layout.addWidget(self.load_btn)

        notes_page.addTab(first_tab, "C-Note - " + self.account.username)

        self.create_note_btn.clicked.connect(self.prompt_title)
        notes_page.currentChanged.connect(self.set_current_tab)
        notes_page.tabCloseRequested.connect(lambda index: self.close_tab(notes_page, index))
        self.open_selected_notes_btn.clicked.connect(lambda: self.create_note())
        self.load_btn.clicked.connect(lambda: self.create_note(from_disk=True))

        self.create_note_btn.setMinimumSize(800, 150)
        self.load_btn.setMinimumSize(200, 50)
        return notes_page

    def __notes_widget(self, index, new_notes):
        """
        Cette méthode construit les éléments de la page des notes
        :return : Widget de note
        """

        notes_widget = QWidget()
        texts_layout = QVBoxLayout()
        texts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_widget.setLayout(texts_layout)

        # Initilizing widget elements
        self.summery_text = QTextEdit()
        self.notes_text = QTextEdit()
        self.keywords_text = QTextEdit()
        self.headLines_text = QTextEdit()
        self.highlighter = HighlightingSystem(self.keywords_text, self.notes_text, self.set_freeze)
        self.__notes_wid_properties(new_notes)
        self.notes_dict[index] = (
            self.headLines_text, self.keywords_text, self.notes_text, self.summery_text, self.notes, self.highlighter)

        # Organizing elements in layouts

        middle_text_layout = QHBoxLayout()
        middle_text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        texts_layout.addWidget(self.headLines_text)
        middle_text_layout.addWidget(self.keywords_text, 2)
        middle_text_layout.addWidget(self.notes_text, 10)
        texts_layout.addLayout(middle_text_layout)
        texts_layout.addWidget(self.summery_text)

        # settings on events actions
        self.__set_on_events_notes_wid()

        return notes_widget

    def __notes_wid_properties(self, new_notes):
        """
        Initialise les propriétés des widgets de notes
        """

        self.headLines_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if new_notes:
            title_font = QFont('Arial', 22)
            title_font.setBold(True)
            self.headLines_text.setCurrentFont(title_font)
            self.headLines_text.insertPlainText(self.notes.title + '\n')
            self.headLines_text.setCurrentFont(MainWindow.DEFAULT_FONT)
            self.headLines_text.insertPlainText('auteur: ' + self.account.username + '\n')
        else:
            self.write_notes()

        self.headLines_text.setCurrentFont(MainWindow.DEFAULT_FONT)
        self.notes_text.setCurrentFont(MainWindow.DEFAULT_FONT)
        self.keywords_text.setCurrentFont(MainWindow.DEFAULT_FONT)
        self.summery_text.setCurrentFont(MainWindow.DEFAULT_FONT)

        self.headLines_text.setPlaceholderText('Write your headlines here...')
        self.notes_text.setPlaceholderText('Write your notes here...')
        self.summery_text.setPlaceholderText('Write your summery here...')

        self.headLines_text.setMaximumHeight(100)
        self.summery_text.setMaximumHeight(150)

        self.headLines_text.setAcceptDrops(False)
        self.summery_text.setAcceptDrops(False)
        self.keywords_text.setAcceptDrops(False)

        self.keywords_text.setReadOnly(True)
        self.notes_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.keywords_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def __set_on_events_notes_wid(self):
        self.notes_text.verticalScrollBar().valueChanged.connect(self.move_keys_bar)
        self.keywords_text.verticalScrollBar().valueChanged.connect(self.move_notes_bar)
        self.notes_text.dropEvent = self.drop_event_notes_text

        self.summery_text.cursorPositionChanged.connect(lambda: self.update_cursor_infos(self.summery_text, None))
        self.notes_text.cursorPositionChanged.connect(lambda: self.update_cursor_infos(self.notes_text, None))
        self.headLines_text.cursorPositionChanged.connect(lambda: self.update_cursor_infos(self.headLines_text, None))
        self.summery_text.mousePressEvent = lambda event: self.update_cursor_infos(self.summery_text, event)
        self.notes_text.mousePressEvent = lambda event: self.update_cursor_infos(self.notes_text, event)
        self.headLines_text.mousePressEvent = lambda event: self.update_cursor_infos(self.headLines_text, event)
        self.headLines_text.focusOutEvent = self.headlines_text_focus_out_event
        self.keywords_text_focus_out_event = self.keywords_text_focus_out_event
        self.keywords_text.mousePressEvent = self.keywords_text_mouse_clic_event
        self.keywords_text.keyPressEvent = self.keywords_text_press_event
        self.keywords_text.mouseMoveEvent = self.keywords_text_mouse_move_event

    # Les méthodes suivantes sont appelées lors des événements :

    def show_notes_page(self):
        self.menubar.setVisible(True)
        self.set_visible_editing_tools(False)
        self.username_input.clear()
        self.password_input.clear()
        self.widgets_lst.setCurrentWidget(self.notes_page)
        self.fill_notes_combo()
        self.notes_page.setTabText(0, "C-Note - " + self.account.username)

    def show_welcome_page(self):
        self.menubar.setVisible(False)
        self.main_toolbar.setVisible(False)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)
        self.error_label.setText('')
        self.username_input.setFocus()

    def create_note(self, new_title=None, from_disk=False):

        if new_title is None:  # Quand il n'y a pas de nouveau titre, on a affaire avec des notes déjà écrites
            if from_disk:
                self.notes = Notes.notesload(self.account)
            else:
                self.notes = self.notes_combo.currentData()
            new_notes = False

        else:
            self.notes = Notes(account=self.account, title=new_title)
            new_notes = True

        if self.notes is None:
            return

        tab_index = len(self.notes_page)
        self.notes_page.addTab(self.__notes_widget(tab_index, new_notes), self.notes.title)
        self.notes_page.setCurrentIndex(tab_index)

        self.notes_page.setTabText(tab_index, self.notes.title)

    def close_tab(self, notes_page, tab_index):

        if tab_index == 0:  # fermer 1er tab = sign out
            self.sign_out()
            return

        notes_page.removeTab(tab_index)

        self.save_on_cloud(True)

        notes_to_shift = dict()

        for index in self.notes_dict.keys():
            if index > tab_index:
                notes_to_shift[index-1] = self.notes_dict[index]

        for index in notes_to_shift.keys():
            self.notes_dict[index] = notes_to_shift[index]

        self.set_current_tab(notes_page.currentIndex())

    def prompt_title(self):
        widget = QWidget()
        widget.setWindowTitle('Titre')
        layout = QVBoxLayout()
        widget.setLayout(layout)
        widget.resize(250, 150)


        layout.addWidget(QLabel('Veuillez choisir un titre aux notes:'))
        notes_title_line = QLineEdit()
        submit_btn = QPushButton('Create notes')

        def submit_event():
            self.create_note(notes_title_line.text().strip())
            widget.close()
            return

        def key_press_event(event: QKeyEvent):
            if event.key() == Qt.Key.Key_Return:
                submit_event()
            QWidget.keyPressEvent(widget, event)
            if event.key() == Qt.Key.Key_Escape:
                widget.close()

        submit_btn.clicked.connect(submit_event)
        widget.keyPressEvent = key_press_event

        layout.addWidget(notes_title_line)
        layout.addWidget(submit_btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        widget.show()

    def prompt_username(self):
        widget = QWidget()
        widget.setWindowTitle('Change username')
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)
        widget.resize(250, 150)

        username_label = QLabel('Enter new username: ')
        new_user_line = QLineEdit()
        error_label = QLabel()
        error_label.setStyleSheet('color: red')
        submit_username_btn = QPushButton('rename username')

        def change_username():
            operation_successful = self.account.change_username(new_user_line.text())
            if operation_successful:
                widget.close()
            else:
                error_label.setText(self.account.error.get_desc())

        def key_event(event: QKeyEvent):
            if event.key() == Qt.Key.Key_Return:
                change_username()
                return
            QWidget.keyPressEvent(widget, event)

        layout.addWidget(username_label)
        layout.addWidget(new_user_line)
        layout.addWidget(error_label)
        layout.addWidget(submit_username_btn)

        submit_username_btn.clicked.connect(change_username)
        widget.keyPressEvent = key_event

        widget.show()

    def prompt_password(self):
        widget = QWidget()
        widget.setWindowTitle('Change password')
        widget.resize(250, 150)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)

        old_pwd_line = QLineEdit()
        new_pwd_line = QLineEdit()
        confirm_pwd_line = QLineEdit()

        old_pwd_line.setPlaceholderText('Old password')
        new_pwd_line.setPlaceholderText('New password')
        confirm_pwd_line.setPlaceholderText('Confirm password')

        old_pwd_line.setEchoMode(QLineEdit.EchoMode.Password)
        new_pwd_line.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_pwd_line.setEchoMode(QLineEdit.EchoMode.Password)

        error_label = QLabel()
        error_label.setStyleSheet('color: red')
        submit_pwd_btn = QPushButton('Change password')

        widget.show()

        def change_pwd():
            operation_successful = self.account.change_password(
                old_pwd_line.text(), new_pwd_line.text(), confirm_pwd_line.text())
            if operation_successful:
                widget.close()
            else:
                error_label.setText(self.account.error.get_desc())

        def key_event(event: QKeyEvent):
            if event.key() == Qt.Key.Key_Return:
                change_pwd()
                return
            if event.key() == Qt.Key.Key_Escape:
                widget.close()
            QWidget.keyPressEvent(widget, event)

        layout.addWidget(old_pwd_line)
        layout.addWidget(new_pwd_line)
        layout.addWidget(confirm_pwd_line)
        layout.addWidget(error_label)
        layout.addWidget(submit_pwd_btn)

        submit_pwd_btn.clicked.connect(change_pwd)
        widget.keyPressEvent = key_event

    def set_current_tab(self, index):

        if index == 0:
            self.set_visible_editing_tools(False)
            return

        self.set_visible_editing_tools(True)

        texts_tuple = self.notes_dict[index]
        self.headLines_text = texts_tuple[0]
        self.keywords_text = texts_tuple[1]
        self.notes_text = texts_tuple[2]
        self.summery_text = texts_tuple[3]
        self.notes = texts_tuple[4]
        self.highlighter.clear_all_selections(False)
        self.highlighter = texts_tuple[5]

        self.notes_text.setFocus()
        self.update_cursor_infos(self.notes_text, None)
        self.last_text = self.notes_text
        self.highlighter.clear_all_selections(False)

    def set_visible_editing_tools(self, visible):
        self.main_toolbar.setVisible(visible)
        self.keywords_menu.setEnabled(visible)
        self.file_menu.setEnabled(visible)
        self.insert_menu.setEnabled(visible)

    def password_line_key_event(self, event):

        if event.key() == Qt.Key.Key_Return:
            self.log_in()
            return

        QLineEdit.keyPressEvent(self.password_input, event)

    def username_line_key_event(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.username_input.clearFocus()
            self.password_input.setFocus()
            return

        QLineEdit.keyPressEvent(self.username_input, event)

    def fill_notes_combo(self):
        self.notes_combo.clear()
        for notes in self.account.notes_lst:
            self.notes_combo.addItem(notes.title, notes)

    def log_in(self):
        login_successful = self.account.log_in(self.username_input.text(), self.password_input.text())
        if login_successful:
            self.show_notes_page()
        else:
            self.show_error()

    def sign_up(self):

        if self.account.error == Error.Connection_Error:
            self.account = Account()

            return

        successful_operation = self.account.sign_up(self.username_input.text(), self.password_input.text())

        if successful_operation:
            self.log_in()

        else:
            self.show_error()

    def sign_out(self):
        self.save_every_thing()
        self.account.sign_out()
        self.notes = None
        self.show_welcome_page()

    def save_as(self):
        self.save(1)

    def show_error(self):
        self.error_label.setText(self.account.get_error_desc())
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

    def save_on_cloud(self, refill_notes_combo):
        self.highlighter.clear_all_selections(False)
        self.notes.save_on_cloud(self.account,
                                 self.notes_text.toHtml(),
                                 self.summery_text.toHtml(),
                                 self.headLines_text.toHtml(),
                                 self.generated_keys,
                                 self.added_keys)
        if refill_notes_combo:
            self.fill_notes_combo()

    def save(self, saveas):
        """
        Cette fonction sauvegarde le document
        """
        if saveas != 1:
            saveas = 0
        sumtext = self.summery_text.toHtml()
        headtext = self.headLines_text.toHtml()
        maintext = self.notes_text.toHtml()
        genekeys = self.generated_keys
        adkeys = self.added_keys
        self.notes.save_on_disk(maintext, sumtext, headtext, genekeys, adkeys, saveas)

    def write_notes(self):
        self.notes_text.setHtml(self.notes.notes_html)
        self.headLines_text.setHtml(self.notes.headLines_html)
        self.summery_text.setHtml(self.notes.summery_html)
        self.added_keys = self.notes.added_keys
        self.generated_keys = self.notes.generated_keys
        self.added_keys.sort(key=Idea.get_line)
        self.generated_keys.sort(key=Idea.get_line)
        self.all_keys = self.added_keys + self.generated_keys
        self.write_keys()

    def write_keys(self):
        """
        Cette fonction écrit la liste d'idées dans le keywords_text.
        """
        if self.all_keys is None:
            return

        self.all_keys.sort(key=Idea.get_line)
        self.keywords_text.clear()

        for i, key in enumerate(self.all_keys):
            self.keywords_text.setCurrentFont(MainWindow.DEFAULT_FONT)
            self.keywords_text.insertPlainText(str(key))

            if i < len(self.all_keys) - 1:
                if self.all_keys[i + 1].same_line(key):
                    # S'il y a une autre idée dans la même ligne, ne pas sauter de ligne
                    if not key.is_empty():  # ajouter l'espace seulement s'il y avait des mots clés avant
                        self.keywords_text.insertPlainText(' ')
                    continue

            self.keywords_text.setCurrentFont(key.max_font)
            self.keywords_text.insertPlainText(' ')
            self.keywords_text.insertPlainText('\n')

    def adjust_keys_with_notes(self):
        co.adjust_idea_fonts(self.notes_text, self.all_keys)
        self.write_keys()

    def update_cursor_infos(self, text, event):
        """
        Cette fonction est appelée à chaque fois que le curseur change de position. Elle initialise le QFont affiché
        dans le Toolbar et redéfinit last_wid au dernier widget utilisé. Si un event non null est donné en paramètre,
        cela signifie que la fonction est appelé en raison d'une clique de souris. Dans ce cas, le last_text change
        pour le widget actuel.
        """

        current_font = text.currentFont()
        self.font_combo.setCurrentFont(current_font)
        self.size_spin.setValue(current_font.pointSize())
        self.bold_act.setChecked(current_font.bold())
        self.italic_act.setChecked(current_font.italic())
        self.underline_act.setChecked(current_font.underline())

        if event is not None:
            # Si l'évènement n'est pas null, réaliser l'évènement de la clique de souris et réinitialiser last_text
            self.last_text = text
            QTextEdit.mousePressEvent(text, event)
            # Ensuite, effacer les surlignages
            self.highlighter.clear_all_selections(False)

    def insert_image(self):
        home = os.path.join(os.environ['HOMEPATH'])
        fil = 'Image files (*.jpg *.git)'
        dialog = QFileDialog.getOpenFileName(parent=self, caption='Choose image', directory=home, filter=fil)
        path = dialog[0]

        image = QImage(path)
        self.notes_text.textCursor().insertImage(image)

    def select_color(self, for_highlight):
        if for_highlight:
            self.highlight_color = QColorDialog.getColor(self.highlight_color)
            pixmap = QPixmap(100, 100)
            pixmap.fill(self.highlight_color)
            self.highlight_color_picker_act.setIcon(QIcon(pixmap))
        else:
            self.text_color = QColorDialog.getColor(self.text_color)
            pixmap = QPixmap(100, 100)
            pixmap.fill(self.text_color)
            self.text_color_picker_act.setIcon(QIcon(pixmap))

    def color(self, for_highlight):
        if for_highlight:
            self.last_text.setTextBackgroundColor(self.highlight_color)
        else:
            self.last_text.setTextColor(self.text_color)

        cursor = self.last_text.textCursor()
        cursor.clearSelection()
        self.last_text.setTextCursor(cursor)

    def drop_event_notes_text(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.DropAction.CopyAction)
            urls = event.mimeData().urls()
            if len(urls) >= 1:
                path = urls[0].toLocalFile()
                image = QImage(path)
                self.notes_text.textCursor().insertImage(image)
                return
        QTextEdit.dropEvent(self.notes_text, event)

    def move_notes_bar(self):
        pos = self.keywords_text.verticalScrollBar().sliderPosition()
        self.notes_text.verticalScrollBar().setSliderPosition(pos)

    def move_keys_bar(self):
        pos = self.notes_text.verticalScrollBar().sliderPosition()
        self.keywords_text.verticalScrollBar().setSliderPosition(pos)

    def keywords_text_mouse_clic_event(self, event: QMouseEvent):

        QTextEdit.mousePressEvent(self.keywords_text, event)
        if len(self.all_keys) == 0:
            return
        self.highlighter.highlight(event.pos(), self.all_keys)

    def keywords_text_mouse_move_event(self, event: QMouseEvent):

        QTextEdit.mouseMoveEvent(self.keywords_text, event)

        cursor = self.keywords_text.cursorForPosition(event.pos())
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
        if not len(cursor.selectedText().strip()) == 0:
            self.keywords_text.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            return

        # self.highlighter.light_highlight(event.pos(), self.all_keys)

        self.keywords_text.viewport().unsetCursor()

    def keywords_text_press_event(self, event: QKeyEvent):

        key = event.key()

        arrow_key_pressed = self.highlighter.highlight_with_key(key, self.all_keys)

        if arrow_key_pressed:
            return

        if Qt.Key.Key_Delete == key:
            self.del_selected_ideas()

        elif event.matches(QKeySequence.StandardKey.Copy):

            if self.highlighter.has_selection():
                self.highlighter.copy_selection()
                return
            else:
                HighlightingSystem.clear_copied_elements()

        elif event.matches(QKeySequence.StandardKey.Paste):
            if HighlightingSystem.has_copied_elements():
                self.add_copied_ideas()
                return

        QTextEdit.keyPressEvent(self.keywords_text, event)

    def headlines_text_focus_out_event(self, event: QFocusEvent):
        QTextEdit.focusOutEvent(self.headLines_text, event)

        # changer le titre des notes
        headlines = self.headLines_text.toPlainText().split('\n')
        if len(headlines) == 0:
            title = 'Sans titre'
        else:
            title = headlines[0]
            if title.strip() == '':
                title = 'Sans titre'
        self.notes.title = title
        self.fill_notes_combo()

        tab_index = None  # Selection l'objet notes correspondant au tab overt
        for index in self.notes_dict.keys():
            if self.notes_dict[index][0] == self.headLines_text:
                tab_index = index
                break

        self.fill_notes_combo()
        self.notes_page.setTabText(tab_index, title)
        self.notes.title = title

    def keywords_text_focus_out_event(self, event: QFocusEvent):
        QTextEdit.focusOutEvent(self.keywords_text, event)
        self.highlighter.clear_all_selections(False)

    def add_key_line_press_event(self, event: QKeyEvent):

        if event.key() == Qt.Key.Key_Space:  # remplacer le caractère espace par '_'
            self.keyword_line.insert('_')
            return

        if event.key() == Qt.Key.Key_Return:
            self.add_keyword()
            self.keyword_line.clear()
            return

        if event.matches(QKeySequence.StandardKey.Paste):
            return

        QLineEdit.keyPressEvent(self.keyword_line, event)

        word = self.keyword_line.text()
        if word == '':
            return
        if word[-1].isupper():
            self.keyword_line.setText(word.lower())

    def del_selected_ideas(self):

        selections = self.highlighter.pop_selected_elements()

        for pos in selections.keys():
            idea = selections[pos]
            cursor: QTextCursor = self.keywords_text.textCursor()
            cursor.setPosition(pos)
            cursor.movePosition(QTextCursor.MoveOperation.WordRight, QTextCursor.MoveMode.KeepAnchor)
            keyword = cursor.selectedText().strip().lower()
            idea.remove_keyword(keyword)

        self.set_freeze(False)
        self.write_keys()

    def set_freeze(self, freeze):
        self.notes_text.setReadOnly(freeze)
        self.keywords_menu.setDisabled(freeze)
        self.insert_menu.setDisabled(freeze)
        self.keyword_line.setDisabled(freeze)
        self.clear_text_act.setDisabled(freeze)

    def clear_gen_keys(self):
        self.generated_keys.clear()
        self.all_keys.clear()
        self.all_keys.extend(self.added_keys)
        self.generate_empty()
        self.write_keys()

    def clear_added_keys(self):
        self.added_keys.clear()
        self.all_keys.clear()
        self.all_keys.extend(self.generated_keys)
        self.write_keys()

    def clear_all_keys(self):

        self.highlighter.clear_all_selections(False)
        self.generated_keys.clear()
        self.added_keys.clear()
        self.all_keys.clear()
        self.write_keys()

    def clear_notes(self):
        self.notes_text.clear()
        self.headLines_text.clear()
        self.summery_text.clear()
        self.clear_all_keys()

    def add_copied_ideas(self):

        cursor = self.notes_text.textCursor()
        insert_line = cursor.blockNumber()
        copied_ideas = HighlightingSystem.get_copied_ideas(insert_line)
        last_line = copied_ideas[-1].line

        shift = last_line + 1 - insert_line
        for idea in self.generated_keys:
            if idea.line >= insert_line:
                idea.shift_line(shift)
        for idea in self.added_keys:
            if idea.line >= insert_line:
                idea.shift_line(shift)

        self.added_keys.extend(copied_ideas)
        self.added_keys.sort(key=Idea.get_line)
        self.generate_empty()
        self.all_keys.extend(copied_ideas)
        self.write_keys()

        for idea in copied_ideas:
            cursor.insertText(idea.phrase + '\n')

    def save_every_thing(self):
        for notes_tuple in self.notes_dict.values():
            self.notes = notes_tuple[4]
            self.save_on_cloud(False)

    def closeEvent(self, *args, **kwargs):
        self.save_every_thing()
        self.app.exit()

    def launch(self):
        """
        Lance le programme !
        """
        self.showMaximized()
        sys.exit(self.app.exec())

    def add_keyword(self):
        """
        Cette fonction ajoute le mot-clé entré manuellement
        """
        new_key = self.keyword_line.text().strip().lower()

        cursor = self.notes_text.textCursor()

        if cursor.hasSelection():
            phrase = cursor.selectedText()
            cursor.clearSelection()
        else:
            phrase = cursor.block().text()

        if new_key is None:
            new_key = phrase.strip().lower()

        line = cursor.blockNumber()
        cursor.setPosition(cursor.selectionStart())
        font = co.get_max_font_by_line(self.notes_text, cursor, line, True)
        new_idea = Idea(phrase, line, font, new_key)

        self.added_keys.append(new_idea)
        self.added_keys.sort(key=Idea.get_line)
        self.generate_empty()
        self.all_keys.append(new_idea)
        self.write_keys()

    def generate(self):
        """
        Cette fonction génère les mots-clés du text (ou de la partie sélectionnée du text). La fonction met à jour
        la liste des idées générée self.generated_keys.
        """
        cursor = self.notes_text.textCursor()
        text = cursor.selection().toPlainText()
        from_to = None
        if text == '':
            text = self.notes_text.toPlainText()
        else:
            doc = self.notes_text.document()
            start = doc.findBlock(cursor.selectionStart()).blockNumber()
            end = doc.findBlock(cursor.selectionEnd()).blockNumber()
            from_to = (start, end)
            self.generate_empty()

        max_fonts = co.get_max_fonts(self.notes_text, from_to)
        dm.get_ideas(text, max_fonts, self.generated_keys, from_to)
        self.generated_keys.sort(key=Idea.get_line)
        self.all_keys = self.added_keys + self.generated_keys
        self.write_keys()

        self.move_keys_bar()  # Afin d'aligner les mots-clés sur les notes

    def generate_empty(self):
        """
        Cette fonction parcour toutes les idées générées automatiquement. Si une ligne ne contient pas d'idée,
        la fonction ajoute une idée vide (sans mots-clés) à cette ligne.
        """
        doc = self.notes_text.document()
        i = 0
        nb_lines = doc.blockCount()
        for line in range(nb_lines):

            phrase = doc.findBlockByLineNumber(line).text()
            font = co.get_max_font_by_line(self.notes_text, self.notes_text.textCursor(), line, False)
            idea = Idea(phrase, line, font)

            if len(self.generated_keys) <= i:  # Si on se rend à la dernière idée, ajouter une idée
                self.generated_keys.insert(line, idea)
                self.all_keys.append(idea)
                i += 1

            elif self.generated_keys[i].line < line:  # Si l'idée i n'est pas n'est pas dans la line, ajouter idée vide.
                self.generated_keys.insert(line, idea)
                self.all_keys.append(idea)
                i += 1

            else:  # Si on n'est à la dernière idée mais qu'on est pas dans la même ligne, passer à la prochaine idée.
                while self.generated_keys[i].line <= line:
                    i += 1
                    if len(self.generated_keys) >= i:
                        break
