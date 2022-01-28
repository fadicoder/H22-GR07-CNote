import sys
from tkinter import *

if __name__ != '__main__':
    sys.exit()


window = Tk()
window.title("C-Note")
window.configure(padx=10, pady=10, bg='#000150')


def launchNoteWindow():
    Label(window, text="C-Note", font="None 30", bg='#000150', fg='white').grid(row=0, columnspan=2, pady=10)
    keys_area = Text(window, width=25, font="None 12")
    keys_area.grid(row=2, column=0, padx=10)
    notes_text = Text(window, font="None 12")
    notes_text.grid(row=2, column=1, padx=10)

    Button(window, text="Submit", font="None 12", bg='white', fg='black').grid(row=3, columnspan=3, pady=10)

    window.mainloop()


def launchSignInWindow():

    Label(window, text="C-Note", font="None 30", bg='#000150', fg='white').grid(row=0, columnspan=2)
    window.mainloop()


if __name__ == '__main__':
    launchNoteWindow()
