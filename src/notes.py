import pickle
import easygui
from PyQt6.QtGui import QFont
import bs4
from htmldocx import HtmlToDocx


from idea import Idea


class Notes:

    def __init__(self, identification=None, account=None, notes_info=None, title=None, file=None):

        self.fileopenned = file
        self.id = identification
        self.added_keys = list()
        self.generated_keys = list()

        if identification is None:
            self.id = account.generate_id()

        if notes_info is None:
            self.summery_html = ""
            self.headLines_html = ""
            self.notes_html = ""

        else:
            attributes_list = notes_info.split('@&%*')
            self.summery_html = attributes_list[1]
            self.headLines_html = attributes_list[2]
            self.notes_html = attributes_list[0]

            restorelistgene = attributes_list[3].split("@$?&")
            for restoregene in restorelistgene:
                idea = restoregene.split("@&&%*****")
                if len(idea) <= 1:
                    break
                keywords = idea[3].split(' ')
                font = QFont()
                font.fromString(idea[2])

                self.generated_keys.append(Idea(idea[0], int(idea[1]), font, keywords))

            restorelistad = attributes_list[4].split("@$?&")

            for restoread in restorelistad:
                idea = restoread.split("@&&%*****")
                if len(idea) <= 1:
                    break
                keywords = idea[3].split(' ')
                font = QFont()
                font.fromString(idea[2])
                self.added_keys.append(Idea(idea[0], int(idea[1]), font, keywords))


        if title is None:
            self.title = Notes.extract_title(self.headLines_html)
        else:
            self.title = title

    @staticmethod
    def extract_title(html):
        headlines = bs4.BeautifulSoup(html, features='html.parser').get_text().split('\n')
        if len(headlines) >= 3:

            if headlines[2].strip() == '':
                title = 'Sans titre'
            else:
                title = headlines[2]

        else:
            title = 'Sans titre'

        return title

    @staticmethod
    def get_notes_info(maintxt, sumtxt, headtxt, genekeys, adkeys):

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
        txtsl = maintxt + '@&%*' + sumtxt + '@&%*' + headtxt + '@&%*' + strgensv + '@&%*' + stradsv  # mets ensemble le tout pour optimiser la sauvegarde
        return txtsl

    def save_on_disk(self, maintxt, sumtxt, headtxt, genekeys, adkeys, saveas):  # sauvegarde le document

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
            self.fileopenned = fileoptemp'''

    def save_on_disk_docx(self, maintxt, sumtxt, headtxt, genekeys, adkeys):  # sauvegarde le document en format docx

        txtsl = ''
        txtsl = self.get_notes_info(headtxt,  maintxt, sumtxt, genekeys, adkeys)
        txtsl = txtsl.replace("@&%*"," ")
        open('temphtml.txt','w').write(txtsl)
        transformer = HtmlToDocx()
        transformer.parse_html_file('temphtml.txt', self.title)

    def save_on_cloud(self, account, maintxt, sumtxt, headtxt, genekeys, adkeys):
        notes_info = self.get_notes_info(maintxt, sumtxt, headtxt, genekeys, adkeys)
        self.notes_html = maintxt
        self.summery_html = sumtxt
        self.headLines_html = headtxt
        self.generated_keys = genekeys
        self.added_keys = adkeys
        account.upload_notes(self, notes_info)

    @staticmethod
    def notesload(account):

        filetoopen = easygui.fileopenbox()
        if filetoopen is None:
            return None

        txtsl = pickle.load(open(filetoopen, "rb"))
        notes = Notes(account, notes_info=txtsl, file=filetoopen)

        return notes
