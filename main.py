from tkinter import *

if __name__ == '__main__':

    root = Tk()
    root.title("C-Note")
    root.configure(padx=10, pady=10, bg='#000150')

    Label(root, text="C-Note", font="None 30", bg='#000150', fg='white').grid(row=0, columnspan=2)
    keys_area = Text(root, width=25, font="None 12")
    keys_area.grid(row=2, column=0, padx=10)
    notes_text = Text(root, font="None 12")
    notes_text.grid(row=2, column=1, padx=10)

    root.mainloop()
