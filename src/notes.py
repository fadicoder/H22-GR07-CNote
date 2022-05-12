import pickle
import easygui
from PyQt6.QtGui import QFont
import bs4
from htmldocx import HtmlToDocx


from idea import Idea


class Notes:
    """
    Ceci est une instance de notes
    """
    def __init__(self, identification=None, account=None, notes_info=None, title=None, file=None):

        self.fileopenned = file #ceci est le fichier de la note
        self.id = identification #note le compte associé à la note
        self.added_keys = list()
        self.generated_keys = list()

        if identification is None: #associe un compte si ce n'est pas fait
            self.id = account.generate_id()

        if notes_info is None: #initialise les zones de texte si ce n'est pas déjà fait
            self.summery_html = ""
            self.headLines_html = ""
            self.notes_html = ""

        else: #sinon ceci va charger la note
            attributes_list = notes_info.split('@&%*') #cette section est pour les zones de textes
            self.summery_html = attributes_list[1]
            self.headLines_html = attributes_list[2]
            self.notes_html = attributes_list[0]

            restorelistgene = attributes_list[3].split("@$?&") # cette section est pour les listes de mots générées
            for restoregene in restorelistgene:
                idea = restoregene.split("@&&%*****")
                if len(idea) <= 1:
                    break
                keywords = idea[3].split(' ')
                font = QFont()
                font.fromString(idea[2])

                self.generated_keys.append(Idea(idea[0], int(idea[1]), font, keywords))

            restorelistad = attributes_list[4].split("@$?&")# cette section est pour les listes de mots ajoutées

            for restoread in restorelistad:
                idea = restoread.split("@&&%*****")
                if len(idea) <= 1:
                    break
                keywords = idea[3].split(' ')
                font = QFont()
                font.fromString(idea[2])
                self.added_keys.append(Idea(idea[0], int(idea[1]), font, keywords))


        if title is None: #créée un titre si il n'y en a pas, sinon le charge
            self.title = Notes.extract_title(self.headLines_html)
        else:
            self.title = title

    @staticmethod
    def extract_title(html):
        """
        Ceci va chercher le titre dans la première ligne de texte
        """
        headlines = bs4.BeautifulSoup(html, features='html.parser').get_text().split('\n')

        if len(headlines) >= 3:

            if headlines[2].strip() == '':
                title = 'Sans titre'# écrit ca si il n'y a rien sur la premiere ligne
            else:
                title = headlines[2]

        else:
            title = 'Sans titre'# écrit ca si il y a moins de 3 lignes

        return title

    @staticmethod
    def get_notes_info(maintxt, sumtxt, headtxt, genekeys, adkeys):
        """
        Cette fonction retourne tout ce qui a été rentré/modifié dans la note par l'utilisateur en une string
        :param maintxt : texte principal
        :param sumtxt : texte de résumé
        :param headtxt : texte de tete/informations importantes
        :param genekeys : liste des mots générée
        :param adkeys : liste des mots ajoutée par l'utilisateur
        """
        strgensv = ''

        for element in genekeys:
            strtemp = element.phrase
            strtemp += "@&&%*****"
            strtemp += str(element.line)
            strtemp += "@&&%*****"
            strtemp += element.max_font.toString()
            strtemp += "@&&%*****"
            strtemp += str(element)
            strgensv += strtemp
            strgensv += "@$?&"
        stradsv = ""
        for element in adkeys:
            strtemp = element.phrase
            strtemp += "@&&%*****"
            strtemp += str(element.line)
            strtemp += "@&&%*****"
            strtemp += element.max_font.toString()
            strtemp += "@&&%*****"
            strtemp += str(element)
            stradsv += strtemp
            stradsv += "@$?&"
        txtsl = maintxt + '@&%*' + sumtxt + '@&%*' + headtxt + '@&%*' + strgensv + '@&%*' + stradsv
        # mets ensemble le tout pour optimiser la sauvegarde
        return txtsl

    def save_on_disk(self, maintxt, sumtxt, headtxt, genekeys, adkeys, saveas):
        """
        Cette fonction va enregistrer le document sur la machine locale
        """
        if self.fileopenned is None or saveas:
            fileopened = easygui.filesavebox()
            if fileopened is None:
                return
            self.fileopenned = fileopened

        txtsl = self.get_notes_info(maintxt, sumtxt, headtxt, genekeys, adkeys)
        pickle.dump(txtsl, open(self.fileopenned, "wb"))  # sauvegarde le document

        '''        openededbeforetemp = None
        fileoptemp = None
        if saveas == 1:
            openededbeforetemp = self.openedfilebefore
            fileoptemp = self.fileopenned

        if saveas == 1:
            self.openedfilebefore = openededbeforetemp
            self.fileopenned = fileoptemp
        '''

    def save_on_disk_docx(self, maintxt, sumtxt, headtxt, genekeys, adkeys):
        """
        Cette fonction exporter les notes en format docx sur la machine locale
        """
        txtsl = ''
        txtsl = self.get_notes_info(headtxt,  maintxt, sumtxt, genekeys, adkeys)
        txtsl = txtsl.replace("@&%*"," ")
        open('temphtml.txt','w').write(txtsl)
        transformer = HtmlToDocx()
        transformer.parse_html_file('temphtml.txt', self.title)

    def save_on_cloud(self, account, maintxt, sumtxt, headtxt, genekeys, adkeys):
        """
        Cette fonction va sauvegarder la note dans le serveur
        :param: account :
        :param: account :
        :param: account :
        """
        notes_info = self.get_notes_info(maintxt, sumtxt, headtxt, genekeys, adkeys)
        self.notes_html = maintxt
        self.summery_html = sumtxt
        self.headLines_html = headtxt
        self.generated_keys = genekeys
        self.added_keys = adkeys
        account.upload_notes(self, notes_info)

    @staticmethod
    def notesload(account):
        """
        Cette fonction charge les notes
        :param: account : est le compte à laquelle les notes sont associées
        """
        filetoopen = easygui.fileopenbox()
        if filetoopen is None:
            return None

        txtsl = pickle.load(open(filetoopen, "rb"))
        notes = Notes(account, notes_info=txtsl, file=filetoopen)

        return notes
