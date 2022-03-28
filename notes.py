import pickle

class notes:
    @staticmethod
    def notessaves(maintxt,sumtxt,headtxt,genekeys,adkeys): #sauvegarde le document
        strgensv = ""

        for element in genekeys :
            strtemp=element.phrase
            strtemp += "@&&%*****"
            strtemp += str(element.line)
            strtemp += "@&&%*****"
            strtemp += element.max_font.toString()
            strtemp += "@&&%*****"
            strtemp+= str(element)
            print (strtemp)
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
            print(strtemp)
            stradsv+=strtemp
            stradsv+="@$?&"

        txtsl=maintxt+'@&%*'+sumtxt+'@&%*'+headtxt+'@&%*'+strgensv+'@&%*'+stradsv#mets ensemble le tout pour optimiser la sauvegarde
         #  print(txtsl) #prinnt pour vérifier que ca fonctionne
        pickle.dump(txtsl, open("savetest.bin", "wb")) #sauvegarde le document
    @staticmethod
    def notesload():
        txtsl='hey'
        txtsl = pickle.load(open(r"savetest.bin", "rb"))
        return txtsl