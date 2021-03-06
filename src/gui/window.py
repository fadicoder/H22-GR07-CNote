from src import dictmanager as dm
from src.gui import cursoroperations as co
from src.idea import Idea
from src.gui.highlighting import HighlightingSystem
from src.account import Account, Error
from src.notes import Notes
import sys
import ctypes

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *


class MainWindow(QMainWindow):
    """
    Cette classe est la fenêtre principale du programme
    """

    DEFAULT_FONT = QFont('Calibri', 15)

    def __init__(self):
        """
        Initialisation de la fenêtre principale et les réglages par défault
        """

        self.highlighter = None
        self.summery_text = None
        self.notes_text = None
        self.keywords_text = None
        self.headLines_text = None
        self.notes = None
        self.file_menu = None
        self.keywords_menu = None
        self.clear_text_act = None
        self.notes_combo = None
        self.notes_dict = dict()
        self.account = Account()

        self.app = QApplication(sys.argv)
        super().__init__()
        self.widgets_lst = QStackedWidget()
        self.setCentralWidget(self.widgets_lst)
        self.setWindowTitle("C-Note")

        #  Indiquer au système d'exploitation que notre programme n'est pas python
        app_id = u'cnotes.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        self.setWindowIcon(QIcon('../resources/appIcon.jpg'))  # assigner une icon au programme

        self.notes_page = self.init_notes_page()
        self.welcome_widget = self.welcome_page()
        self.widgets_lst.addWidget(self.notes_page)
        self.widgets_lst.addWidget(self.welcome_widget)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)

        self.highlight_color = QColorConstants.Cyan
        self.text_color = QColorConstants.Red
        self.menubar = QMenuBar()
        self.init_menubar()
        self.menubar.setVisible(False)
        self.setMenuBar(self.menubar)

        self.toolbar = QToolBar()
        self.init_toolbar()
        self.toolbar.setVisible(False)
        self.addToolBar(self.toolbar)

        self.generated_keys = []
        self.added_keys = []
        self.all_keys = self.generated_keys + self.added_keys
        self.last_text = self.notes_text

    def init_menubar(self):
        """
        Initialise les éléments de la bare de menu.
        """
        save_act = QAction('Sauvegarder', self)
        save_act.setShortcut('Ctrl+S')
        save_act.triggered.connect(self.save)

        save_as_act = QAction('Sauvegarder sous', self)
        save_as_act.setShortcut('Ctrl+Shift+S')
        save_as_act.triggered.connect(lambda: self.save(1))

        save_on_cloud_act = QAction('Sauvegarder dans le compte', self)
        save_on_cloud_act.triggered.connect(lambda: self.save_on_cloud(True))

        load_act = QAction('Charger', self)
        load_act.setShortcut('Ctrl+L')
        load_act.triggered.connect(lambda: self.create_note(from_disk=True))

        export_docs_act = QAction('Exporter vers .docx', self)
        export_docs_act.triggered.connect(self.save_on_disk_docx)

        self.clear_text_act = QAction('Effacer toutes les notes', self)
        self.clear_text_act.triggered.connect(self.clear_notes)

        sign_out_act = QAction('Déconnection', self)
        sign_out_act.triggered.connect(self.sign_out)

        exit_act = QAction('Sauvgarder et quitter', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.closeEvent)

        edit_username_act = QAction("Modifier le nom d'utilisateur", self)
        edit_username_act.triggered.connect(self.prompt_username)
        edit_pwd_act = QAction('Modifier le nom de passe', self)
        edit_pwd_act.triggered.connect(self.prompt_password)

        generate_act = QAction('Générer des mots-clés', self)
        generate_act.setShortcut('Ctrl+G')
        generate_act.triggered.connect(self.generate)
        clear_gen_keys_act = QAction('Effacer les mots-clés générés', self)
        clear_gen_keys_act.triggered.connect(self.clear_gen_keys)
        clear_added_keys_act = QAction('Effacer les mots-clés ajoutés', self)
        clear_added_keys_act.triggered.connect(self.clear_added_keys)
        clear_all_keys_act = QAction('Effacer tous les mots-clés', self)
        clear_all_keys_act.triggered.connect(self.clear_all_keys)

        account_menu = self.menubar.addMenu('Compte')
        account_menu.addAction(edit_username_act)
        account_menu.addAction(edit_pwd_act)
        account_menu.addSeparator()
        account_menu.addAction(sign_out_act)
        account_menu.addAction(exit_act)

        self.file_menu = self.menubar.addMenu('Fichier')
        self.file_menu.addAction(save_act)
        self.file_menu.addAction(save_as_act)
        self.file_menu.addAction(save_on_cloud_act)
        self.file_menu.addAction(load_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_docs_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.clear_text_act)

        self.keywords_menu = self.menubar.addMenu('Mots-clés')
        self.keywords_menu.addAction(generate_act)
        self.keywords_menu.addSeparator()
        self.keywords_menu.addActions([clear_added_keys_act, clear_gen_keys_act, clear_all_keys_act])

    def save_on_disk_docx(self):
        """
        Cette fonction envoie les données pour enregistrer une copie des notes en format docx dans la machine locale
        """
        sumtext = self.summery_text.toHtml()
        headtext = self.headLines_text.toHtml()
        maintext = self.notes_text.toHtml()
        self.notes.save_on_disk_docx(maintext, sumtext, headtext)

    def init_toolbar(self):
        """
        Cette fonction initiallise la barre de paramètre et son contenu, les raccourcis, leurs valeurs, etc.
        """

        self.keyword_line = QLineEdit()
        self.keyword_line.setMaximumWidth(250)
        self.keyword_line.setPlaceholderText('Ajouter un mot-clé')
        self.keyword_line.setAcceptDrops(False)
        self.keyword_line.keyPressEvent = self.add_key_line_press_event

        self.size_spin = QSpinBox()
        self.size_spin.setValue(MainWindow.DEFAULT_FONT.pointSize())
        self.size_spin.valueChanged.connect(lambda size: self.last_text.setFontPointSize(size))

        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(MainWindow.DEFAULT_FONT)
        self.font_combo.setEditable(False)
        self.font_combo.currentFontChanged.connect(lambda font: self.last_text.setFontFamily(font.family()))

        align_left_act = QAction(QIcon('../resources/AlignLeft.png'), 'Aligner gauche', self)
        align_center_act = QAction(QIcon('../resources/AlignCenter.png'), 'Aligner centre', self)
        align_right_act = QAction(QIcon('../resources/AlignRight.png'), 'Aligner droite', self)
        align_left_act.triggered.connect(lambda: self.last_text.setAlignment(Qt.AlignmentFlag.AlignLeft))
        align_center_act.triggered.connect(lambda: self.last_text.setAlignment(Qt.AlignmentFlag.AlignCenter))
        align_right_act.triggered.connect(lambda: self.last_text.setAlignment(Qt.AlignmentFlag.AlignRight))

        self.bold_act = QAction(QIcon('../resources/Bold.png'), 'Texte gras', self)
        self.italic_act = QAction(QIcon('../resources/Italic.png'), 'Texte italique', self)
        self.underline_act = QAction(QIcon('../resources/Underline.png'), 'Texte souligné', self)
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
        self.highlight_act = QAction(QIcon('../resources/Highlight.png'), 'Surligner', self)
        self.highlight_color_picker_act = QAction(QIcon(highlight_pixmap), 'Couleur de surlignage', self)
        self.text_color_act = QAction(QIcon('../resources/TextColor.png'), 'Colorer le texte', self)
        self.text_color_picker_act = QAction(QIcon(text_color_pixmap), 'Couleur de texte', self)
        self.highlight_color_picker_act.triggered.connect(lambda: self.select_color(True))
        self.text_color_picker_act.triggered.connect(lambda: self.select_color(False))
        self.highlight_act.triggered.connect(lambda: self.color(True))
        self.text_color_act.triggered.connect(lambda: self.color(False))

        self.toolbar.setStyleSheet("QToolBar{spacing:45px;}")
        self.toolbar.addWidget(self.keyword_line)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.font_combo)
        self.toolbar.addWidget(self.size_spin)
        self.toolbar.addSeparator()
        self.toolbar.addActions([align_left_act, align_center_act, align_right_act])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.bold_act, self.italic_act, self.underline_act])
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.highlight_act, self.highlight_color_picker_act])
        self.toolbar.addSeparator()
        self.toolbar.addActions(([self.text_color_act, self.text_color_picker_act]))

    def welcome_page(self):
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
        self.login_btn = QPushButton('Connection')
        self.signup_btn = QPushButton('Inscription')
        self.error_label = QLabel()
        self.welcome_page_properties()

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

    def welcome_page_properties(self):
        """
        Cette méthode établit les propriétés des widgets de bienvenue.
        """
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setFont(MainWindow.DEFAULT_FONT)
        self.username_input.setMaximumWidth(400)
        self.password_input.setPlaceholderText('Mot de passe')
        self.password_input.setFont(MainWindow.DEFAULT_FONT)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMaximumWidth(400)
        self.error_label.setFont(self.DEFAULT_FONT)
        self.error_label.setStyleSheet('color: red')

    def init_notes_page(self):
        """
        Cette fonction est la fenetre qui liste toutes les notes ouvertes,
        et qui permet de facilement passer de l'une à l'autre
        """
        notes_page = QTabWidget()

        first_tab = QWidget()
        layout = QVBoxLayout()
        first_tab.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_page.setTabsClosable(True)

        create_note_btn = QPushButton('Nouvelles notes')
        self.notes_combo = QComboBox()
        open_selected_notes_btn = QPushButton('Ouvrir les notes sélectionnées')
        delete_notes_btn = QPushButton('Supprimer les notes sélectionnées')
        load_btn = QPushButton('Charger des notes du disk')
        self.fill_notes_combo()

        layout.addWidget(create_note_btn)
        choose_notes_layout = QHBoxLayout()
        choose_notes_layout.addWidget(self.notes_combo)
        actions_layout = QVBoxLayout()
        actions_layout.addWidget(open_selected_notes_btn)
        actions_layout.addWidget(delete_notes_btn)
        choose_notes_layout.addLayout(actions_layout)
        layout.addSpacing(50)
        layout.addLayout(choose_notes_layout)
        layout.addSpacing(50)
        layout.addWidget(load_btn)

        notes_page.addTab(first_tab, "C-Note - " + self.account.username)

        create_note_btn.clicked.connect(self.prompt_title)
        notes_page.currentChanged.connect(self.set_current_tab)
        notes_page.tabCloseRequested.connect(lambda index: self.close_tab(index, notes_page))
        open_selected_notes_btn.clicked.connect(lambda: self.create_note())
        delete_notes_btn.clicked.connect(self.delete_selected_notes)
        load_btn.clicked.connect(lambda: self.create_note(from_disk=True))

        create_note_btn.setMinimumSize(500, 60)
        load_btn.setMinimumHeight(60)

        return notes_page

    def notes_widget(self, index, new_notes):
        """
        Cette méthode construit les éléments de la page d'une note.
        :return : Widget de note
        """

        notes_widget = QWidget()
        texts_layout = QVBoxLayout()
        texts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_widget.setLayout(texts_layout)
        self.generated_keys = self.notes.generated_keys
        self.added_keys = self.notes.added_keys

        # Initilizing widget elements
        self.summery_text = QTextEdit()
        self.notes_text = QTextEdit()
        self.keywords_text = QTextEdit()
        self.headLines_text = QTextEdit()
        self.highlighter = HighlightingSystem(self.keywords_text, self.notes_text, self.set_freeze)
        self.notes_wid_properties(new_notes)
        self.notes_dict[index] = (
            self.headLines_text, self.keywords_text, self.notes_text, self.summery_text, self.notes, self.highlighter,
            self.added_keys, self.generated_keys)

        # Organizing elements in layouts

        middle_text_layout = QHBoxLayout()
        middle_text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        texts_layout.addWidget(self.headLines_text)
        middle_text_layout.addWidget(self.keywords_text, 2)
        middle_text_layout.addWidget(self.notes_text, 10)
        texts_layout.addLayout(middle_text_layout)
        texts_layout.addWidget(self.summery_text)

        # settings on events actions
        self.set_on_events_notes_wid()
        return notes_widget

    def notes_wid_properties(self, new_notes):
        """
        Initialise les propriétés des widgets de notes
        """
        self.headLines_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)
        self.notes_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)
        self.keywords_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)
        self.summery_text.document().setDefaultFont(MainWindow.DEFAULT_FONT)

        self.headLines_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if new_notes:
            title_font = QFont('Arial', 22)
            title_font.setBold(True)
            self.headLines_text.setCurrentFont(title_font)
            self.headLines_text.insertPlainText(self.notes.title + '\n')
            self.headLines_text.setCurrentFont(MainWindow.DEFAULT_FONT)
            self.headLines_text.insertPlainText('auteur: ' + self.account.username + '\n')
            self.headLines_text.setCurrentFont(MainWindow.DEFAULT_FONT)
        else:
            self.write_notes()

        self.headLines_text.setPlaceholderText('Écrivez votre titre ici...')
        self.notes_text.setPlaceholderText('Écrivez vos notes ici...')
        self.summery_text.setPlaceholderText('Écrivez votre résumé ici')

        self.headLines_text.setMaximumHeight(100)
        self.summery_text.setMaximumHeight(150)

        self.headLines_text.setAcceptDrops(False)
        self.summery_text.setAcceptDrops(False)
        self.keywords_text.setAcceptDrops(False)

        self.keywords_text.setReadOnly(True)
        self.notes_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.keywords_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def set_on_events_notes_wid(self):
        """
        Cette fonction va compléter et mettre en marche une nouvelle note lorsque tout est valide
        """
        self.notes_text.verticalScrollBar().valueChanged.connect(self.move_keys_bar)
        self.keywords_text.verticalScrollBar().valueChanged.connect(self.move_notes_bar)
        self.summery_text.cursorPositionChanged.connect(lambda: self.update_cursor_infos(self.summery_text, None))
        self.notes_text.cursorPositionChanged.connect(lambda: self.update_cursor_infos(self.notes_text, None))
        self.headLines_text.cursorPositionChanged.connect(lambda: self.update_cursor_infos(self.headLines_text, None))
        self.summery_text.mousePressEvent = lambda event: self.update_cursor_infos(self.summery_text, event)
        self.notes_text.mousePressEvent = lambda event: self.update_cursor_infos(self.notes_text, event)
        self.headLines_text.mousePressEvent = lambda event: self.update_cursor_infos(self.headLines_text, event)
        self.headLines_text.focusOutEvent = self.headlines_text_focus_out_event
        self.keywords_text.focusOutEvent = self.keywords_text_focus_out_event
        self.keywords_text.mousePressEvent = self.keywords_text_mouse_clic_event
        self.keywords_text.keyPressEvent = self.keywords_text_press_event
        self.keywords_text.mouseMoveEvent = self.keywords_text_mouse_move_event

    def show_notes_page(self):
        """
        Cette fonction va afficher la page de choix de notes/création de nouvelle note une fois connecté
        """
        self.menubar.setVisible(True)
        self.set_visible_editing_tools(False)
        self.username_input.clear()
        self.password_input.clear()
        self.widgets_lst.setCurrentWidget(self.notes_page)
        self.fill_notes_combo()
        self.notes_page.setTabText(0, "C-Note - " + self.account.username)

    def show_welcome_page(self):
        """
        Cette fonction va afficher la page de connection/création de compte
        """
        self.menubar.setVisible(False)
        self.toolbar.setVisible(False)
        self.widgets_lst.setCurrentWidget(self.welcome_widget)
        self.error_label.setText('')
        self.username_input.setFocus()

    def create_note(self, new_title=None, from_disk=False):
        """
        Cette fonction va charger une nouvelle note, qu'elle vienne d'etre créée ou non
        :param new_title : détermine si la note vient d'etre créée
        :param from_disk : détermine l'origine de la note
        """
        if new_title is None:  # Quand il n'y a pas de nouveau titre, on a affaire avec des notes déjà écrites
            if from_disk:
                self.notes = Notes.notesload(self.account)
            else:
                self.notes = self.notes_combo.currentData()
            new_notes = False

        else:
            if new_title == '':
                new_title = 'Sans titre'
            self.notes = Notes(account=self.account, title=new_title)
            new_notes = True

        if self.notes is None:
            return

        tab_index = len(self.notes_page)
        self.notes_page.addTab(self.notes_widget(tab_index, new_notes), self.notes.title)
        self.notes_page.setCurrentIndex(tab_index)

        self.notes_page.setTabText(tab_index, self.notes.title)

    def delete_selected_notes(self):
        """
        Cette fonction va supprimer une note de la base de données
        """
        notes = self.notes_combo.currentData()
        for tab_index in self.notes_dict.keys():
            if self.notes_dict[tab_index][4] == notes:
                self.close_tab(tab_index, save=False)

        self.account.delete_notes(notes)
        self.fill_notes_combo()

    def close_tab(self, tab_index, notes_page=None, save=True):
        """
        Cette fonction va supprimer une note de l'affichage à la demande de l'utilisateur
        """
        if tab_index == 0:  # fermer 1er tab = sign out
            self.sign_out()
            return

        if notes_page is None:
            notes_page = self.notes_page

        notes_page.removeTab(tab_index)

        self.save_on_cloud(True) if save else None  # sauvegarder si exigé

        notes_to_shift = dict()

        if len(self.notes_dict) == 1:
            self.notes_dict.clear()
            return

        for index in self.notes_dict.keys():
            if index > tab_index:
                notes_to_shift[index - 1] = self.notes_dict[index]

        for index in notes_to_shift.keys():
            self.notes_dict[index] = notes_to_shift[index]

        for index in notes_to_shift.keys():
            self.notes_dict.pop(index+1)

        self.set_current_tab(notes_page.currentIndex())

    def prompt_title(self):
        """
        Cette fonction va demander de choisir un titre lorsque l'utilisateur demande de créer un nouveau fichier de notes
        """
        widget = QWidget()
        widget.setWindowTitle('Titre')
        layout = QVBoxLayout()
        widget.setLayout(layout)
        widget.resize(250, 150)

        layout.addWidget(QLabel('Veuillez choisir un titre aux notes:'))
        notes_title_line = QLineEdit()
        submit_btn = QPushButton('Créer les notes')

        def submit_event():
            self.create_note(new_title=notes_title_line.text().strip())
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
        """
        Cette fonction va prendre en charge le changement de nom d'utilisateur à la demande de l'utilisateur
        """
        widget = QWidget()
        widget.setWindowTitle("Nom d'utilisateur")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)
        widget.resize(250, 150)

        username_label = QLabel("Entrer le nouveau nom d'utilisateur: ")
        new_user_line = QLineEdit()
        error_label = QLabel()
        error_label.setStyleSheet('color: red')
        submit_username_btn = QPushButton('Renommer')

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
        """
        Cette fonction va prendre en charge le changement de mot de passe à la demande de l'utilisateur
        """
        widget = QWidget()
        widget.setWindowTitle('Mot de passe')
        widget.resize(250, 150)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)

        old_pwd_line = QLineEdit()
        new_pwd_line = QLineEdit()
        confirm_pwd_line = QLineEdit()

        old_pwd_line.setPlaceholderText('Ancien mot de passe')
        new_pwd_line.setPlaceholderText('Nouveau mot de passe')
        confirm_pwd_line.setPlaceholderText('Confirmer le mot de passe')

        old_pwd_line.setEchoMode(QLineEdit.EchoMode.Password)
        new_pwd_line.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_pwd_line.setEchoMode(QLineEdit.EchoMode.Password)

        error_label = QLabel()
        error_label.setStyleSheet('color: red')
        submit_pwd_btn = QPushButton('Changer le mot de passe')

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
        """
        Cette fonction va changer l'affichage de la note selon la sélection de l'utilisateur.
        :param index : ceci est la note sélectionnée et qui doit etre affichée
        """
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
        self.added_keys = texts_tuple[6]
        self.generated_keys = texts_tuple[7]
        self.all_keys = self.generated_keys + self.added_keys

        self.notes_text.setFocus()
        self.update_cursor_infos(self.notes_text, None)
        self.last_text = self.notes_text
        self.highlighter.clear_all_selections(False)

    def set_visible_editing_tools(self, visible):
        """
        Modifie l'état de visibilité des utils des textes
        :param visible : boolean qui indique la visibilité des utils des textes
        """
        self.toolbar.setVisible(visible)
        self.keywords_menu.setEnabled(visible)
        self.file_menu.setEnabled(visible)

    def password_line_key_event(self, event):
        """
        Évènement de presse de bouton de l'entrée de texte du mot de passe. Si on entre ENTRER, l'utilisateur se connecte
        :param event: l'évènement
        """

        if event.key() == Qt.Key.Key_Return:
            self.log_in()
            return

        QLineEdit.keyPressEvent(self.password_input, event)

    def username_line_key_event(self, event):
        """
        Évènement de presse de bouttons pour l'entrée du mot d'utilisateur. Si on entre ENTRER, le focus passe à l'entrée
        du mot de passe.
        :param event : évènement
        """
        if event.key() == Qt.Key.Key_Return:
            self.username_input.clearFocus()
            self.password_input.setFocus()
            return

        QLineEdit.keyPressEvent(self.username_input, event)

    def fill_notes_combo(self):
        """
        Cette méthode remplit la liste des titres des notes dans la tab principale
        """
        self.notes_combo.clear()
        for notes in self.account.notes_lst:
            self.notes_combo.addItem(notes.title, notes)

    def log_in(self):
        """
        Cette fonction va prendre en charge la connection à la demande de l'utilisateur
        """
        login_successful = self.account.log_in(self.username_input.text(), self.password_input.text())
        if login_successful:
            self.show_notes_page()
        else:
            self.show_error()

    def sign_up(self):
        """
        Cette fonction va prendre en charge la création d'un nouveau compte à la demande de l'utilisateur
        """
        if self.account.error == Error.Connection_Error:
            self.account = Account()

            return

        successful_operation = self.account.sign_up(self.username_input.text(), self.password_input.text())

        if successful_operation:
            self.log_in()

        else:
            self.show_error()

    def sign_out(self):
        """
        Cette fonction va prendre en charge la déconnection à la demande de l'utilisateur
        """
        if self.account.is_signed_out():
            return
        self.save_every_thing(close_everything=True)
        self.account.sign_out()
        self.notes = None
        self.notes_dict.clear()
        self.notes_dict.clear()
        self.show_welcome_page()

    def show_error(self):
        """
        Cette fonction va afficher le code d'erreur si le code en rencontre un
        """
        self.error_label.setText(self.account.get_error_desc())
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

    def save_on_cloud(self, refill_notes_combo):
        """
        Cette fonction va enregistrer le document dans la base de données
        """
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
        """
        Cette fonction va charger les notes au premier plan.
        """
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

    def update_cursor_infos(self, text, event):
        """
        Cette fonction est appelée à chaque fois que le curseur change de position. Elle initialise le QFont affiché
        dans le Toolbar et redéfinit last_wid au dernier widget utilisé. Si un event non null est donné en paramètre,
        cela signifie que la fonction est appelé en raison d'une clique de souris. Dans ce cas, le last_text change
        pour le widget actuel.
        """

        if not text.textCursor().hasSelection():  # Ne pas mettre ajour les informations du texte s'il y a une selection
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

    def select_color(self, for_highlight):
        """
        Cette fonction saisit à l'utilisateur la couleur désirée pour le surlignage ou le texte.
        Cette fonction affiche aussi la couleur choisie dans l'icône de la couleur de surlignage ou de la couleur de
        texte.
        :param for_highlight : boolean qui indique si on veut la couleur de surlignage
        """
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
        """
        Cette fonction color le texte ou surligne le texte du dernier du bloc de texte actuellement en état de
        modification.
        :param for_highlight: Boolean qui indique si c'est un surlignage qui est exigé.
        """
        if for_highlight:
            self.last_text.setTextBackgroundColor(self.highlight_color)
        else:
            self.last_text.setTextColor(self.text_color)

        cursor = self.last_text.textCursor()
        cursor.clearSelection()
        self.last_text.setTextCursor(cursor)

    def move_notes_bar(self):
        """
        Cette fonction déplace la bare du bloc des notes selon la position de la barre du bloc des mots-clés.
        """
        pos = self.keywords_text.verticalScrollBar().sliderPosition()
        self.notes_text.verticalScrollBar().setSliderPosition(pos)

    def move_keys_bar(self):
        """
        Cette fonction déplace la bare du bloc des mots-clés selon la position de la barre du bloc des notes.
        """
        pos = self.notes_text.verticalScrollBar().sliderPosition()
        self.keywords_text.verticalScrollBar().setSliderPosition(pos)

    def keywords_text_mouse_clic_event(self, event: QMouseEvent):
        """
        Cette fonction est l'évènement de clique de souris pour le bloc des mots-clés.
        Elle permet le surlignage du mot cliqué
        :param event : évènement
        """

        QTextEdit.mousePressEvent(self.keywords_text, event)
        if len(self.all_keys) == 0:
            return
        self.highlighter.highlight(event.pos(), self.all_keys)

    def keywords_text_mouse_move_event(self, event: QMouseEvent):
        """
        Cette fonction est l'évènement de déplacement de souris pour le bloc des mots-clés.
        Elle changer la forme du curseur quand il s'envole sur un mot.
        :param event : évènement
        """
        QTextEdit.mouseMoveEvent(self.keywords_text, event)

        cursor = self.keywords_text.cursorForPosition(event.pos())
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
        if not len(cursor.selectedText().strip()) == 0:
            self.keywords_text.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            return

        # self.highlighter.light_highlight(event.pos(), self.all_keys)

        self.keywords_text.viewport().unsetCursor()

    def keywords_text_press_event(self, event: QKeyEvent):
        """
        Cette fonction est l'évènement de presse de bouton pour le bloc des mots-clés.
        Elle permet de déplacer le surlignage des idées avec les boutons des flèches.
        Elle permet aussi de copier et coller les idées.
        :param event : évènement
        """
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
        """
        Cette fonction va modifier le titre selon la première ligne de la première zone de texte
        """
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
        """
        Cette fonction permet l'effecenemnt de sélection des mots-clés une fois le focus n'est plus sur le bloc des
        mots-clés.
        :param event: évènement
        """
        QTextEdit.focusOutEvent(self.keywords_text, event)
        self.highlighter.clear_all_selections(False)

    def add_key_line_press_event(self, event: QKeyEvent):
        """
        Cette fonction va gérer la création d'une nouvelle idée, en remplaçant les espace par un _
        """
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
        """
        Cette fonction va effacer les idées sélectionnées par l'utilisateur
        """
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
        """
        Cette fonction va figer tout ce qui doit l'etre pour éviter que l'utilisateur change des choses lors d'une sélection
        """
        self.notes_text.setReadOnly(freeze)
        self.file_menu.setDisabled(freeze)
        self.keywords_menu.setDisabled(freeze)
        self.toolbar.setDisabled(freeze)
        self.clear_text_act.setDisabled(freeze)

    def clear_gen_keys(self):
        """
        Cette fonction va effacer les idées générées par le programme
        """
        self.generated_keys.clear()
        self.all_keys.clear()
        self.all_keys.extend(self.added_keys)
        self.generate_empty()
        self.write_keys()

    def clear_added_keys(self):
        """
        Cette fonction va effacer les idées ajoutées par l'utilisateur
        """
        self.added_keys.clear()
        self.all_keys.clear()
        self.all_keys.extend(self.generated_keys)
        self.write_keys()

    def clear_all_keys(self):
        """
        Cette fonction va effacer toutes les iddées
        """
        self.highlighter.clear_all_selections(False)
        self.generated_keys.clear()
        self.added_keys.clear()
        self.all_keys.clear()
        self.write_keys()

    def clear_notes(self):
        """
        Cette fonction vide tout ce qui peut etre vidé
        """
        self.notes_text.clear()
        self.headLines_text.clear()
        self.summery_text.clear()
        self.clear_all_keys()

    def add_copied_ideas(self):
        """
        Cette fonction va chercher le mot surligner pour le copier en idée.
        Si le curseur est dans la section des phrases, cela va copier l'idée en mot, si c'est dans la section des idées,
        ça va copier les idées et les phrases associées
        """
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

    def save_every_thing(self, close_everything=False):
        """
        Cette fonction va tout sauvegarder lorsque nécessaire
        """
        if close_everything:
            while len(self.notes_dict) > 0:
                self.close_tab(1, save=True)


        else:
            for notes_tuple in self.notes_dict.values():
                self.notes = notes_tuple[4]
                self.save_on_cloud(False)

    def closeEvent(self, *args, **kwargs):
        """
        Cette fonction ferme le programme
        """
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
            cursor.setPosition(cursor.selectionStart())
        else:
            phrase = cursor.block().text()
        line = cursor.blockNumber()

        if new_key is None:
            new_key = phrase.strip().lower()

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
        Cette fonction parcourt toutes les idées générées automatiquement. Si une ligne ne contient pas d'idée,
        la fonction ajoute une idée vide (sans mots-clés) à cette ligne.
        """
        doc = self.notes_text.document()
        i = 0
        nb_lines = doc.toPlainText().count('\n')
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

            else:
                # Si on n'est pas à la dernière idée, mais qu'on n'est pas dans la même ligne, passer à la
                # prochaine idée.
                while self.generated_keys[i].line <= line:
                    i += 1
                    if len(self.generated_keys) >= i:
                        break
