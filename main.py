from tkinter import *

if __name__ == '__main__':

    window = Tk()
    window.title("C-Note")
    window.configure(padx=10, pady=10)

    keys_area = Text(window)
    keys_area.grid(row=0, column=0)

    notes_text = Text(window)
    notes_text.grid(row=0, column=1)

    window.mainloop()
