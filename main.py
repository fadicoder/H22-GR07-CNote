from gui import Window


if __name__ == '__main__':

    window = Window()
    window.launch()



'''
if __name__ != '__main__':
    sys.exit()


window = Tk()
window.title("C-Note")
window.configure(padx=20, pady=20, bg='#000150')
window.anchor(anchor=N)
window.state('zoomed')

def launchNoteWindow():

    Label(window, text="C-Note", font="None 30", bg='#000150', fg='white').grid(row=0, column=0, pady=10)

    texts_frame = Frame(window, bg='#000150')
    headlines_area = Text(texts_frame, font="None 12", height=5)
    headlines_area.grid(row=0, padx=10, columnspan=2, pady=10)
    keys_area = Text(texts_frame, width=25, font="None 12", height=20)
    keys_area.grid(row=1, column=0, padx=10)
    notes_text = Text(texts_frame, font="None 12", height=20)
    notes_text.grid(row=1, column=1, padx=10)
    summery_area = Text(texts_frame, font="None 12", height=5)
    summery_area.grid(row=2, columnspan=3, padx=10, pady=10)
    texts_frame.grid(row=1, column=0)

    Button(window, text="Submit", font="None 12", bg='white', fg='black').grid(row=4, column=0, pady=10)




def launchSignInWindow():

    Label(window, text="C-Note", font="None 30", bg='#000150', fg='white').grid(row=0, columnspan=2)


if __name__ == '__main__':
    launchNoteWindow()
    '''

