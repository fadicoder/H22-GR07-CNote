import pickle
import easygui

class notes:
    openedfilebefore = False
    fileopenned = None
    @staticmethod
    def notessaves(maintxt,sumtxt,headtxt,genekeys,adkeys,saveas): #sauvegarde le document
        openededbeforetemp=None
        fileoptemp=None
        if saveas==1 :
            openededbeforetemp=notes.openedfilebefore
            fileoptemp=notes.fileopenned


        if notes.openedfilebefore ==False:
            fileopened=easygui.filesavebox()
            notes.fileopenned=fileopened
            notes.openedfilebefore = True
        if notes.fileopenned!=None:
            strgensv = ""
            for element in genekeys :
                strtemp=element.phrase
                strtemp += "@&&%*****"
                strtemp += str(element.line)
                strtemp += "@&&%*****"
                strtemp += element.max_font.toString()
                strtemp += "@&&%*****"
                strtemp+= str(element)
                strgensv+=strtemp
                strgensv+="@$?&"
            stradsv = ""
            for element in adkeys :
                strtemp = element.phrase
                strtemp += "@&&%*****"
                strtemp += str(element.line)
                strtemp += "@&&%*****"
                strtemp += element.max_font.toString()
                strtemp += "@&&%*****"
                strtemp += str(element)
                stradsv+=strtemp
                stradsv+="@$?&"
            txtsl=maintxt+'@&%*'+sumtxt+'@&%*'+headtxt+'@&%*'+strgensv+'@&%*'+stradsv#mets ensemble le tout pour optimiser la sauvegarde
         #  print(txtsl) #prinnt pour vérifier que ca fonctionne
            pickle.dump(txtsl, open(notes.fileopenned, "wb")) #sauvegarde le document
        if saveas==1:
            notes.openedfilebefore=openededbeforetemp
            notes.fileopenned=fileoptemp

    @staticmethod
    def notesload():

        filetoopen=easygui.fileopenbox()
        if notes.fileopenned != None:
            notes.fileopenned=filetoopen
            notes.openedfilebefore=True
            txtsl = pickle.load(open(notes.fileopenned, "rb"))
            return txtsl
        else:
            return None