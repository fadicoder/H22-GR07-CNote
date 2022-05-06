import dictmanager as dm
from gui import cursoroperations as co, Input
import notes
from idea import Idea
from gui.highlighting import HighlightingSystem
import os
import sys

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *

'''
- image dimensions
- add draw
- extract
- repair adjust keys
- light high-light phrase monday
- cut
- families keywords tuesday
- delete 1 selected idea + with no phrase
- change doc.blockCount() to count(\n)
'''


class MainWindow(QMainWindow):

    DEFAULT_FONT = QFont('Calibri', 15)

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
        self.images = []
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

        load_act = QAction('Load', self)
        load_act.setShortcut('Ctrl+L')
        load_act.triggered.connect(self.load)

        self.clear_text_act = QAction('Clear all notes', self)
        self.clear_text_act.triggered.connect(self.clear_notes)

        sign_out_act = QAction('Sign out', self)
        sign_out_act.triggered.connect(self.show_welcome_page)

        exit_act = QAction('exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.app.exit)

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
        account_menu.addAction(save_act)
        account_menu.addAction(save_as_act)
        account_menu.addAction(load_act)
        account_menu.addSeparator()
        account_menu.addAction(sign_out_act)

        file_menu = self.menubar.addMenu('File')
        file_menu.addActions([self.clear_text_act, exit_act])

        self.insert_menu = self.menubar.addMenu('Insert')
        self.insert_menu.addAction(insert_image_act)

        self.keywords_menu = self.menubar.addMenu('Keywords')
        self.keywords_menu.addAction(generate_act)
        self.keywords_menu.addSeparator()
        self.keywords_menu.addActions([clear_added_keys_act, clear_gen_keys_act, clear_all_keys_act])
        self.keywords_menu.addSeparator()
        self.keywords_menu.addAction(adjust_keys_act)

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

    def __welcome_widget(self):
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
        self.__welcome_wid_properties()

        # Organise les éléments
        buttons = QHBoxLayout()
        buttons.addWidget(self.login_btn)
        buttons.addWidget(self.signup_btn)
        root.addWidget(self.username_input)
        root.addWidget(self.password_input)
        root.addSpacing(20)
        root.addLayout(buttons)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # action au clic
        self.login_btn.clicked.connect(self.show_notes_page)

        return welcome_widget

    def __welcome_wid_properties(self):
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

    def __notes_widget(self):
        """
        Cette méthode construit les éléments de la page des notes
        :return : Widget de note
        """

        notes_widget = QWidget()
        root = QVBoxLayout()
        notes_widget.setLayout(root)

        # Initilizing widget elements
        self.summery_text = QTextEdit()
        self.notes_text = QTextEdit()
        self.keywords_text = QTextEdit()
        self.headLines_text = QTextEdit()
        self.keyword_line = QLineEdit()
        self.highlighter = HighlightingSystem(self.keywords_text, self.notes_text, self.set_freeze)
        self.__notes_wid_properties()

        # Organizing elements in layouts
        texts_layout = QVBoxLayout()
        texts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        middle_text_layout = QHBoxLayout()
        middle_text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        texts_layout.addWidget(self.headLines_text)
        middle_text_layout.addWidget(self.keywords_text, 2)
        middle_text_layout.addWidget(self.notes_text, 10)
        texts_layout.addLayout(middle_text_layout)
        texts_layout.addWidget(self.summery_text)
        root.addLayout(texts_layout)

        # settings on events actions
        self.__set_on_events_notes_wid()

        return notes_widget

    def __notes_wid_properties(self):
        """
        Initialise les propriétés des widgets de notes
        """
        self.notes_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)
        self.headLines_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)
        self.keywords_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)
        self.summery_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)

        self.headLines_text.setPlaceholderText('Write your headlines here...')
        self.notes_text.setPlaceholderText('Write your notes here...')
        self.summery_text.setPlaceholderText('Write your summery here...')

        self.headLines_text.setMaximumHeight(100)
        self.summery_text.setMaximumHeight(150)

        self.headLines_text.setAcceptDrops(False)
        self.summery_text.setAcceptDrops(False)
        self.keywords_text.setAcceptDrops(False)

        self.keywords_text.setReadOnly(True)
        self.headLines_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self.keywords_text.mousePressEvent = self.keywords_text_mouse_clic_event
        self.keywords_text.keyPressEvent = self.keywords_text_press_event
        self.keywords_text.mouseMoveEvent = self.keywords_text_mouse_move_event

    # Les méthodes suivantes sont appelées lors des événements :

    def show_notes_page(self):
        self.menubar.setVisible(True)
        self.main_toolbar.setVisible(True)
        self.widgets_lst.setCurrentWidget(self.notes_widget)

    def show_welcome_page(self):
        self.menubar.setVisible(False)
        self.main_toolbar.setVisible(False)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)

    def enter_login(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_Enter:
            self.show_notes_page()

    def save_as(self):

        self.save(1)

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
        notes.notes.notessaves(maintext, sumtext, headtext, genekeys, adkeys, saveas)

    def load(self):
        """
        Cette fonction charge le document
        """
        txtsl = notes.notes.notesload()
        if txtsl is not None:
            attributes_list = txtsl.split('@&%*')
            self.summery_text.setHtml(attributes_list[1])
            self.headLines_text.setHtml(attributes_list[2])
            self.notes_text.setHtml(attributes_list[0])
            self.generated_keys.clear()
            self.added_keys.clear()
            self.all_keys = self.generated_keys + self.added_keys
            restorelistgene = attributes_list[3].split("@$?&")
            for restoregene in restorelistgene:
                if len(restorelistgene)-1 > restoregene:
                    idea = restoregene.split("@&&%*****")
                    keywords = idea[3].split(' ')
                    font = QFont()
                    font.fromString(idea[2])
                    self.generated_keys.append(Idea(idea[0], int(idea[1]), font, keywords))
            restorelistad = attributes_list[4].split("@$?&")
            for restoread in restorelistad:
                idea = restoread.split("@&&%*****")
                keywords = idea[3].split(' ')
                font = QFont()
                font.fromString(idea[2])
                self.generated_keys.append(Idea(idea[0], int(idea[1]), font, keywords))
            self.all_keys = self.generated_keys + self.added_keys

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
        self.images.append(image)
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
                self.images.append(image)
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

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        super().keyPressEvent(a0)
        Input.press_key(a0.key())

    def keyReleaseEvent(self, a0: QKeyEvent):
        super().keyReleaseEvent(a0)
        Input.release_key(a0.key())

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

    def launch(self):
        """
        Lance le programme !
        """

        self.notes_text.setFocus()
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
            print(phrase)

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
