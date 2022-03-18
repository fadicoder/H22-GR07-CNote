from PyQt6.QtGui import QTextCursor


def move_cursor_to_line(cursor: QTextCursor, line: int):
    """
    Cette fonction déplace le curseur vers le block donné en paramètre.
    :param cursor : le curseur à déplacer.
    :param line : la ligne sur laquelle le curseur sera déplacé.
    """

    while cursor.blockNumber() < line:
        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
    while cursor.blockNumber() > line:
        cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)


def get_max_font_by_line(text, i: int, cursor_on_line: bool):
    """
    Cette fonction calcule le plus grand font de la ligne i donnée en paramètre et le retourne.
    Si le curseur n'est pas nécessairement sur la ligne à analyser, la fonction déplace celui-ci vers la ligne voulue.
    :param text : le widget du text à analyser
    :param i : numéro de la ligne à analyser
    :param cursor_on_line : un boolean qui indique si le curseur est nécessairement sur la ligne à analyser
    :return : le plus grand font de la ligne i
    """

    if not cursor_on_line:
        move_cursor_to_line(text.textCursor(), i)

    text.moveCursor(QTextCursor.MoveOperation.StartOfBlock)
    document = text.document()
    max_font = text.currentFont()

    for j in range(document.findBlockByLineNumber(i).length() - 1):

        text.moveCursor(QTextCursor.MoveOperation.NextCharacter)
        current_font = text.currentFont()
        if current_font > max_font:
            max_font = current_font

    return max_font


def get_max_fonts(text):
    """
    Cette fonction calcule la plus grande police de caractère d'une ligne et la retourne.
    :param text : le widget du text à analyser.
    :return Une liste des plus grandes police de caractère de chaque ligne.
    """

    doc = text.document()
    text.moveCursor(QTextCursor.MoveOperation.Start)
    max_fonts = []

    for i in range(doc.blockCount()):
        max_fonts.append(get_max_font_by_line(text, i, True))
        text.moveCursor(QTextCursor.MoveOperation.NextBlock)

    return max_fonts


def adjust_idea_fonts(text, all_keys: list):
    """
    Cette fonction ajuste le max_font de chaque idée de la liste d'idées donnée en paramètre pour qu'il corresponde
    au plus grand font de la ligne de l'idée. Ceci permettra le réalignement de chaque idée avec sa phrase.
    Remarque : Cette fonction a un potentiel limité. Elle ne peut pas réaligner les idées avec leurs phrases si le
    text des notes a été modifier. Pour cela, il faudrait régénérer les mots-clés.
    :param text : le widget du text à analyser.
    :param all_keys : liste de toutes les idées à vérifier
    """

    max_fonts = get_max_fonts(text)

    for i, idea in enumerate(all_keys):
        idea.max_font = max_fonts[idea.line]

        if len(all_keys) < i:
            # Si on n'est pas à la dernière idée, vérifier si la prochaine idée est dans même ligne

            while idea.same_line(i + 1):
                all_keys[i + 1].max_font = max_fonts[idea.line]
