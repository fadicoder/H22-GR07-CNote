def keywords_matrix(text):

    phrases = text.split(".")
    words = []

    for phrase in phrases:
        words.append(phrase.split(' '))

    print(words)
    return words