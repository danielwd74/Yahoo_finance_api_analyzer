from tkinter import *
import sys

def escape(e):
    print('escape')
    window.withdraw()
    sys.exit()

window = Tk()
frame = Frame(window, width=200, height=400)
window.bind('<Escape>', escape)
frame.pack()

window.mainloop()