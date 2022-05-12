from PyQt6.QtGui import QTextCursor


def move_cursor_to_line(cursor: QTextCursor, line: int):
    """
    Cette fonction déplace le curseur vers le block donné en paramètre.
    :param cursor : le curseur à déplacer.
    :param line : la ligne sur laquelle le curseur sera déplacé.
    """
    this_line = cursor.blockNumber()
    last_line = this_line

    while this_line < line:
        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        this_line = cursor.blockNumber()
        if cursor.blockNumber() == last_line:
            return False
        last_line = this_line

    while cursor.blockNumber() > line:
        cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)

    return True


def get_start_of_phrase(cursor: QTextCursor, phrase: str, start_line: int):
    if cursor.document().toPlainText().count('\n') - 1 < start_line:
        return

    move_cursor_to_line(cursor, start_line)

    start_pos = cursor.position()

    cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor, len(phrase))

    while phrase not in cursor.selection().toPlainText():
        cursor.clearSelection()
        start_pos += 1  # avancer d'une position
        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor, len(phrase))

    return start_pos


def get_max_font_by_line(text, cursor, i: int, cursor_on_line: bool):
    """
    Cette fonction calcule le plus grand font de la ligne i donnée en paramètre et le retourne.
    Si le curseur n'est pas nécessairement sur la ligne à analyser, la fonction déplace celui-ci vers la ligne voulue.
    :param text : le widget du text à analyser.
    :param cursor : Le curseur qui sera déplacer entre les caractères pour déterminer la plus grande fonte.
    :param i : numéro de la ligne à analyser.
    :param cursor_on_line : un boolean qui indique si le curseur est nécessairement sur la ligne à analyser.
    :return : le plus grand font de la ligne i.
    """

    if not cursor_on_line:
        move_cursor_to_line(text.textCursor(), i)

    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
    document = text.document()
    text.setTextCursor(cursor)
    max_font = text.currentFont()

    for j in range(document.findBlockByLineNumber(i).length() - 1):

        cursor.setPosition(cursor.position()+1)
        text.setTextCursor(cursor)
        current_font = text.currentFont()
        if current_font.pointSize() > max_font.pointSize():
            max_font = current_font

    return max_font


def get_max_fonts(text, from_to):
    """
    Cette fonction calcule la plus grande police de caractère d'une ligne et la retourne.
    :param text : le widget du text à analyser.
    :param from_to : Un tuple qui contient les numéros des deux lignes qui limites les lignes ou il faudrait calculer
    la plus grande fonte.
    :return Une liste des plus grandes police de caractère de chaque ligne.
    """

    cursor = text.textCursor()
    max_fonts = []
    start = 0
    end = text.toPlainText().count('\n') + 1

    if from_to is None:
        cursor.movePosition(QTextCursor.MoveOperation.Start)

    else:
        start = from_to[0]
        end = from_to[1]
        move_cursor_to_line(cursor, start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)

    for i in range(start, end+1):
        max_fonts.append(get_max_font_by_line(text, cursor, i, True))
        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

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

    max_fonts = get_max_fonts(text, None)

    for i, idea in enumerate(all_keys):
        idea.max_font = max_fonts[idea.line]

        if len(all_keys) < i:
            # Si on n'est pas à la dernière idée, vérifier si la prochaine idée est dans même ligne

            while idea.same_line(i + 1):
                all_keys[i + 1].max_font = max_fonts[idea.line]


def move_cursor_to_next_word(cursor: QTextCursor, move_operation: QTextCursor.MoveOperation):


    valid_operation = cursor.movePosition(move_operation)
    first_line = cursor.blockNumber()

    if not valid_operation:
        return False



    cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
    last_position = cursor.position()

    if first_line != cursor.blockNumber():
        return

    while cursor.selectedText().strip() == '':
        cursor.clearSelection()
        valid_operation = cursor.movePosition(move_operation)

        if (not valid_operation) or (last_position == cursor.position()):
            return False

        last_position = cursor.position()
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)

    cursor.movePosition(QTextCursor.MoveOperation.StartOfWord)

    return True
