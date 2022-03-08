import constant
from tkinter import *
from tkcalendar import DateEntry
import sys
from getData import *
from getReport import get_report_data

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
        self.label = Label(self.master, text="Please enter tickers and press enter")
        self.entry = Entry(self.master)
        self.entries = []
        self.master.bind('<Return>', self.add_entry)
        self.text = StringVar()
        self.label2 = Label(self.master, textvariable=self.text, wraplength=(constant.WINDOW_WIDTH - 10))
        self.enterB = Button(self.master, text="Get data", bg='lightblue', command=self.get_data)
        self.text2 = StringVar()
        self.label3 = Label(self.master, textvariable=self.text2, wraplength=(constant.WINDOW_WIDTH - 10))
        self.returnButton = Button(self.master, text='Return', command=self.return_main, width=10, fg='red')

        self.label.pack()
        self.entry.pack()
        self.label2.pack()
        self.enterB.pack()
        self.label3.pack()
        self.returnButton.pack()

    def add_entry(self, event):
        self.entries.append(self.entry.get()) 
        val = ''
        for text in self.entries:
            val += (text + ", ")
        self.text.set(val)
        self.entry.delete(0, 'end')
    
    def get_data(self):
        self.text.set("")
        usage = get_usage()
        self.text2.set('\n' + get_date_diff(self.entries) + "\n" + f"The number of requests used: {usage}/100")
        request_tickers(self.entries, usage)
        self.entries = []
        #routine to show usage
    
    def return_main(self):
        self.label.destroy()
        self.entry.destroy()
        self.label2.destroy()
        self.enterB.destroy()
        self.label3.destroy()
        self.returnButton.destroy()
        self.another = MainWindow(self.master)

class WindowGenerateOptionReport:
    def __init__(self, master):
        self.master = master
        self.tickerLabel = Label(self.master, text="Enter a ticker:")
        self.tickerEntry = Entry(self.master)
        self.dateLabel = Label(self.master, text="Enter a date for ticker:")
        self.dateEntry = DateEntry(self.master)
        self.boolvar = BooleanVar()
        #Calls are false
        self.callsChoice = Radiobutton(self.master, text='Calls', variable=self.boolvar, value=False)
        #Puts are True
        self.putsChoice = Radiobutton(self.master, text='Puts', variable=self.boolvar, value=True)
        self.getDataButton = Button(self.master, text='Get volume report', bg='pink', command=self.get_vol_report)
        self.stringVar = StringVar()
        self.resultLabel = Label(self.master, textvariable=self.stringVar, wraplength=(constant.WINDOW_WIDTH - 10), anchor="w", justify=LEFT)

        self.tickerLabel.grid(row=1, column=1, padx=5, pady=10)
        self.tickerEntry.grid(row=1, column=2)
        self.dateLabel.grid(row=2, column=1, padx=5)
        self.dateEntry.grid(row=2, column=2)
        self.callsChoice.grid(row=3, column=1)
        self.putsChoice.grid(row=3, column=2)
        self.getDataButton.grid(row=4, column=2, pady=10)
        self.resultLabel.grid(row=5, column=1, pady=5, columnspan=5)
        #self.label = Label(self.master, text='Hello')
        #self.label.pack()
    
    def get_vol_report(self):
        self.stringVar.set(get_report_data(self.dateEntry.get_date(), self.tickerEntry.get(), self.boolvar.get()))

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
    root.title('Options data')
    root.geometry(f"{constant.WINDOW_WIDTH}x{constant.WINDOW_HEIGHT}")
    root.bind('<Escape>', escape)
    main = MainWindow(root)
    root.mainloop()
