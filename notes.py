import pickle

class notes:
    def notessaves(maintxt,sumtxt,headtxt): #sauvegarde le document
        txtsl=maintxt+sumtxt+headtxt#mets ensemble le tout pour optimiser la sauvegarde
        #print(txtsl) #prinnt pour vérifier que ca fonctionne
        pickle.dump(txtsl, open("savetest.bin", "wb")) #sauvegarde le document
