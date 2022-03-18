import pickle

class notes:
    @staticmethod
    def notessaves(maintxt,sumtxt,headtxt): #sauvegarde le document
        txtsl=maintxt+sumtxt+headtxt#mets ensemble le tout pour optimiser la sauvegarde
        #print(txtsl) #prinnt pour vérifier que ca fonctionne
        pickle.dump(txtsl, open("savetest.bin", "wb")) #sauvegarde le document
    @staticmethod
    def notesload(maintext):
        txtsl='hey'
        txtsl = pickle.load(open(r"sample.bin", "rb"))
        maintext.setHtml(txtsl)
        print(maintext.toHtml)
        return