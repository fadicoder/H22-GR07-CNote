import pickle

class notes:
    @staticmethod
    def notessaves(maintxt,sumtxt,headtxt,genekeys,adkeys): #sauvegarde le document
        strgene = ""

        for element in genekeys :
            strgene += str(element)
        strad = ""

        for element in adkeys :
            strad += str(element)

        txtsl=maintxt+'@&%*'+sumtxt+'@&%*'+headtxt+'@&%*'+strgene+'@&%*'+strad#mets ensemble le tout pour optimiser la sauvegarde
        #print(txtsl) #prinnt pour vérifier que ca fonctionne
        pickle.dump(txtsl, open("savetest.bin", "wb")) #sauvegarde le document
    @staticmethod
    def notesload():
        txtsl='hey'
        txtsl = pickle.load(open(r"savetest.bin", "rb"))
        return txtsl