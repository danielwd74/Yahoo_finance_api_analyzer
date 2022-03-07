import constant
from tkinter import *
import sys

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.buttons = []
        #button for get options data
        self.buttons.append(Button(self.master, text="Get options data", wraplength=400, bg='RED', command=self.get_option_data))
        self.buttons[0].place(relx=0.5, rely=0.5, anchor=CENTER)
        #button for generating reports
        self.buttons.append(Button(self.master, text='Generate a report off options data', wraplength=400, bg='YELLOW', command=self.generate_report))
        self.buttons[1].place(relx=0.5, rely=0.4, anchor=CENTER)
        #button for daily change in open interest
        self.buttons.append(Button(self.master, text='Get daily change in open interest among strikes', wraplength=400, bg='GREEN', command=self.get_daily_change_strikes))
        self.buttons[2].place(relx=0.5, rely=0.6, anchor=CENTER)

    def destroy_buttons(self, buttons):
        for button in buttons:
            button.destroy()

    def get_option_data(self):
        self.destroy_buttons(self.buttons)
        self.another = WindowGetOptionData(self.master)

    def generate_report(self):
        self.destroy_buttons(self.buttons)
        self.another = WindowGenerateOptionReport(self.master)

    def get_daily_change_strikes(self):
        self.destroy_buttons(self.buttons)
        self.another = WindowDailyChangeInterest(self.master)

class WindowGetOptionData:
    def __init__(self, master):
        self.master = master
        self.label = Label(self.master, text="Hello there 1")
        self.label.pack()

class WindowGenerateOptionReport:
    def __init__(self, master):
        self.master = master
        self.label = Label(self.master, text='Hello')
        self.label.pack()

class WindowDailyChangeInterest:
    def __init__(self, master):
        self.master = master
        self.label = Label(self.master, text='Goodbye')
        self.label.pack()

def escape(e):
    root.withdraw()
    sys.exit()

if __name__ == "__main__":
    root = Tk()
    root.geometry(f"{constant.WINDOW_WIDTH}x{constant.WINDOW_HEIGHT}")
    root.bind('<Escape>', escape)
    main = MainWindow(root)
    root.mainloop()
