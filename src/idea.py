class Idea:
    """
    Cette classe définit le concept d'une idée qui est une liste de mots-clés associée à une phrase
    et au plus grand font de la phrase.
    """

    def __init__(self, phrase: str, line: int, max_font, keywords=None):

        if keywords is None:
            keywords = list()
        if type(keywords) == str:
            keywords = [keywords]

        self.keywords = keywords
        self.phrase = phrase
        self.line = line
        if type(max_font) == str:
            self.max_font.fromString(max_font)
        else:
            self.max_font = max_font

    def __str__(self):
        if self.is_empty():
            return ''
        return ' '.join(self.keywords)

    def phrase_include_idea(self, phrase):
        """
        Cette fonction vérifie si l'idée est dans la phrase donnée
        """
        return self.phrase in phrase

    def is_empty(self):
        """
        Cette fonction vérifie si une ligne est vide
        """
        return len(self.keywords) == 0

    def add_keyword(self, new_keyword):
        """
        Cette fonction vérife que le mot clée n'existe pas déja avant de le rajouter
        """
        if new_keyword not in self.keywords:
            self.keywords.append(new_keyword)

    def shift_line(self, shift):
        """
        Cette fonction fait descendre les idées qui sont après l'endroit ou on essaie d'en rajouter
        """
        self.line = self.line + shift

    def remove_keyword(self, keyword):
        self.keywords.remove(keyword)

    def same_line(self, idea2):
        """
        Retourne si deux idées sont sur la meme ligne ou pas
        """
        return self.line == idea2.line

    def get_line(self):
        """
        Récupère la ligne de l'idée
        """
        return self.line
