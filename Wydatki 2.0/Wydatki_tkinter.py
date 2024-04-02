import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle
from tkinter.messagebox import showinfo, showerror
from tkinter import filedialog

from tkcalendar import DateEntry
from calendar import month_name
from datetime import datetime

from os import path, getlogin, environ
import json

import pandas as pd
import Wydatki_DataOperations


# Constants

Categories_Dict = {
    'R': "Rent",
    'F': "Food",
    'C': "Cosmetics",
    'BF': "BonusFood",
    'P': "Parties",
    'T': "Tickets",
    'U': "University",
    'H': "Hobby",
    'CL': "Clothes",
    'INC': "Income",
}

Category_Tuple = (
    "Income",
    "Bill",
    "SelfCare",
    "Household",
    "Food",
    "EatingOutside",
    "Party",
    "Ticket",
    "Clothes",
    "Hobby",
)

TableColumns_Tuple = (
    "Date",
    "Amount",
    "Category",
    "Description",
    # For debug, hidden ID column
    #"ID",
)

TableWidth_Dict = {
    "Date": 150,
    "Amount": 100,
    "Category": 100,
    "Description": 400,
    #"ID": 30,
}


# WindowApps

class ScrollableFrameVertical(ttk.Frame):
    """It's just like normal frame but scrollable.
    Used in older version of this."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # tkinter object that are scrollable
        canvas = tk.Canvas(
            master=self
        )

        # the actual Scrollbar 
        scrollBar = ttk.Scrollbar(
            master=self,
            orient="vertical",
            command=canvas.yview,
        )
        self.scrollable_frame = ttk.Frame(
            master=canvas,
        )
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.configure(yscrollcommand=scrollBar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollBar.pack(side=tk.RIGHT, fill=tk.Y)


class PathOpenerApp(tk.Tk):
    def __init__(self, initialdir: str) -> None:
        super().__init__()
        self.title("Select month")
        self.initialdir = initialdir
        
        """ Settings """
        pad_set = 10
        settings = {
            "font": ("cambria", 12)
        }

        """ Styles """
        self.style = ttk.Style(self)
            # Buttons
        self.style.configure(
            style="TButton",
            relief="raised",
            **settings,
            )
            # Labels
        self.style.configure(
            style="TLabel",
            **settings,
        )
        
        """ Widgets """
        self.label = ttk.Label(
            master=self,
            style="TLabel",
            text="Select month:",
        )
        self.label.pack(padx=pad_set, pady=pad_set)

        self.button_open = ttk.Button(
            master=self,
            style="TButton",
            text="Search",
            command=self.get_file_path,
        )
        self.button_open.pack(padx=pad_set, pady=pad_set)

        self.button_newMonth = ttk.Button(
            master=self,
            style="TButton",
            text="Start new month",
            command=self.open_new_month,
        )
        self.button_newMonth.pack(padx=pad_set, pady=pad_set)

        """ Run after init """
        self.mainloop()

    """ Functions """

    def get_file_path(self):
        filetypes = [
            ("TXT files", "*.txt"),
            ("all files", "*.*"),
        ]
        self.filename = filedialog.askopenfilename(
            title="Select month",
            filetypes=filetypes,
            initialdir=self.initialdir,
        )
        self.destroy()

    def open_new_month(self):
        # We don't need anymore those two buttons.
        # New app runs to get first entry and create file.
        # Them those app window is destroyed as well and filename is returned
        self.destroy()
        NewMonthApp = NewMonth()
        self.filename = NewMonthApp.folderPath


class NewMonth(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Insert first Expense for new month")

        """ Settings """

        ipaddings = {
            "ipady": 1,
            "ipadx": 1,
        }

        paddings = {
            "pady": 5,
            "padx": 5,
        }

        # Frame for entry
        # Frame 
        EntryFrame = ttk.Entry(
            master=self,
        )
        EntryFrame.pack()

        """ DATE """
        # Date Label
        DateLabel = ttk.Label(
            master=EntryFrame,
            text="Date:",
        )
        DateLabel.grid(column=0, row=0, sticky="w", **paddings)

        # Date Entry
        self.DateInput = DateEntry(
            master=EntryFrame,
            date_pattern="dd.mm.yyyy",
            year=datetime.today().year,
            month=datetime.today().month
        )
        self.DateInput.grid(column=0, row=1, sticky="w", **paddings, **ipaddings)

        """ AMOUNT """
        # Amount Label
        AmountLabel = ttk.Label(
            master=EntryFrame,
            text=f"Price [%s]:" % "zł"
        )
        AmountLabel.grid(column=1, row=0, sticky="w", **paddings)

        # Amount entry
        self.AmountEntry = ttk.Entry(
            master=EntryFrame,
        )
        self.AmountEntry.grid(column=1, row=1, sticky="w", **paddings, **ipaddings)

        """ CATEGORY """
        # Category Label
        CatLabel = ttk.Label(
            master=EntryFrame,
            text="Category:",
        )
        CatLabel.grid(column=2, row=0, sticky="w", **paddings)

        # Category Entry
        self.CatEntry = ttk.Combobox(
            master=EntryFrame,
            state="readonly",
            values=list(Category_Tuple)
        )
        # To set value to combobox instead of inserting the value the id of the value is needed.
        # In this case, index method get id using variable from data list.
        self.CatEntry.grid(column=2, row=1, sticky="w", **paddings, **ipaddings)

        """ DESCRIPTION """
        # Bonus description Label
        BonusLabel = ttk.Label(
            master=EntryFrame,
            text="Description:"
        )
        BonusLabel.grid(column=3, row=0, sticky="w", **paddings)

        # Bonus description Entry
        self.BonusEntry = ttk.Entry(
            master=EntryFrame,
            width=50,
        )
        self.BonusEntry.grid(column=3, row=1, sticky="w", **paddings, **ipaddings)


        # Frame for buttons

        ButtonFrame = ttk.Frame(
            master=self
        )
        ButtonFrame.pack()

        CreateNewMonth = ttk.Button(
            master=ButtonFrame,
            text="Create new month file and add first entry.",
            command=self.get_data_and_create_newMonth
        )
        CreateNewMonth.pack(**paddings, **ipaddings)


        self.mainloop()

    """FUNCTIONS"""

    def get_data_and_create_newMonth(self):

        newFileYear = datetime.strptime(self.DateInput.get(), "%d.%m.%Y").year
        newFileMonth = datetime.strptime(self.DateInput.get(), "%d.%m.%Y").month

        FirstEntry = ExpensesApp.getExpenseEntries(
            (self.DateInput,
            self.AmountEntry,
            self.CatEntry,
            self.BonusEntry),
            newFileYear,
            newFileMonth,
            )

        if FirstEntry:
            # Check if the first entry is valid.
            # Creates folder name
            newFileName = f"{newFileYear}_{month_name[newFileMonth]}"
            fileLoc = environ["EXPENSES_PATH"]+f"\\{newFileName}.txt"

            isFile = path.isfile(fileLoc)
            

            if not isFile:
                # If file didn't exist before, data from list is convert to dict.
                data = {
                    "Date": [FirstEntry[0]],
                    "Amount": [FirstEntry[1]],
                    "Cat": [FirstEntry[2]],
                    "BonusDesc": [FirstEntry[3]]
                }
                # Them to DataFrame and to json file.
                # (To avoid problems with reading file it was done through DataFrame)
                data = pd.DataFrame(data)
                data = data.to_json()
                # metadata contains metadata of folder as well as first entry
                metadata = {
                        "creator": getlogin(),
                        "month": newFileMonth,
                        "year": newFileYear,
                        "data": data 
                    }
                with open(fileLoc, 'w') as file:
                    # Just before saving, data is convert to meet Json standards.
                    file.write(json.dumps(metadata))
                
                # After first entry, the main view will open.
                # PathOpener should always return path, With new file, the path is the same. 
                self.folderPath = fileLoc
                self.destroy()

            else:
                # If folder already exist the error is rised.
                showerror(
                title="This file already exist.",
                message=f"{newFileName} already exist."
                )
        

class ExpensesApp(tk.Tk):
    lastID = 0
    def __init__(self, expenses, month: int, year: int, user: str) -> None:
        super().__init__()
        # In case some nan will still exist.
        # The NaN values are complicated to work with and looks not so good.
        # The --- Looks much better.
        expenses.fillna(inplace=True, value="---")

        # The DataFrame we work with.
        self.expensesDF = expenses
        # Variable that control the month we are working with (used in new and modified)
        self.monthOfInterest = month
        self.yearOfInterest = year
        self.FileUser = user
        
        self.title(f"Hello {self.FileUser}! Here is your expenses in {month_name[self.monthOfInterest]} {self.yearOfInterest}")
        self.resizable(False, False)

        """ Settings """

        settings = {
            "font": ("cambria", 11),
        }

        ipaddings = {
            "ipady": 1,
            "ipadx": 1,
        }

        paddings = {
            "pady": 5,
            "padx": 5,
        }

        """ Styles """
        self.style = ThemedStyle()
        self.style.set_theme(theme_name="aquativo")

        # Labels
        self.style.configure(
            style="TLabel",
            **settings,
        )

        # TreeView
        self.style.configure(
            style="Treeview",
            **settings,
        )

        """ Widgets """

        # Main table
        self.tableTreeview = ttk.Treeview(
            master=self,
            height=30,
            columns=TableColumns_Tuple,
            show="headings",
        )

        # The part that write whole table using existing Expenses data.
        for column_ in TableColumns_Tuple:
            self.tableTreeview.column(column_, anchor=tk.CENTER, width=TableWidth_Dict[column_],)
            self.tableTreeview.heading(column_, text=column_, anchor=tk.CENTER)

        for row_ in range(0, self.expensesDF.shape[0]):
            currentRow = self.expensesDF.iloc[row_].to_list()
            # In case of some bugs that happens with floats, the round() is used.
            # It used to print 1.700000 instead of 1.7 of 1.70.
            currentRow[1] = round(currentRow[1], 2)
            # Appending ID column have to be done separately, otherwise error rises.
            currentRow.append(self.lastID)
            self.lastID += 1
            self.tableTreeview.insert('', tk.END, values=currentRow)

        self.tableTreeview.grid(row=0, column=0, sticky="nsew")

        # Scrollbar used in table:
        scrollbar = ttk.Scrollbar(
            master=self, 
            orient=tk.VERTICAL,
            command=self.tableTreeview.yview
        )
        self.tableTreeview.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Frame for entry
        # Frame 
        EntryFrame = ttk.Frame(
            master=self,
        )
        EntryFrame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        """ DATE """
        # Date Label
        DateLabel = ttk.Label(
            master=EntryFrame,
            text="Date:",
        )
        DateLabel.grid(column=0, row=0, sticky="w", **paddings)

        # Date Entry
        self.DateInput = DateEntry(
            master=EntryFrame,
            date_pattern="dd.mm.yyyy",
            year=self.yearOfInterest,
            month=self.monthOfInterest,
        )
        self.DateInput.grid(column=0, row=1, sticky="w", **paddings, **ipaddings)

        """ AMOUNT """
        # Amount Label
        AmountLabel = ttk.Label(
            master=EntryFrame,
            text=f"Price [%s]:" % "zł"
        )
        AmountLabel.grid(column=1, row=0, sticky="w", **paddings)

        # Amount entry
        self.AmountEntry = ttk.Entry(
            master=EntryFrame,
        )
        self.AmountEntry.grid(column=1, row=1, sticky="w", **paddings, **ipaddings)

        """ CATEGORY """
        # Category Label
        CatLabel = ttk.Label(
            master=EntryFrame,
            text="Category:",
        )
        CatLabel.grid(column=2, row=0, sticky="w", **paddings)

        # Category Entry
        self.CatEntry = ttk.Combobox(
            master=EntryFrame,
            state="readonly",
            values=list(Category_Tuple)
        )
        self.CatEntry.grid(column=2, row=1, sticky="w", **paddings, **ipaddings)

        """ DESCRIPTION """
        # Bonus description Label
        BonusLabel = ttk.Label(
            master=EntryFrame,
            text="Description:"
        )
        BonusLabel.grid(column=3, row=0, sticky="w", **paddings)

        # Bonus description Entry
        self.BonusEntry = ttk.Entry(
            master=EntryFrame,
            width=65,
        )
        self.BonusEntry.grid(column=3, row=1, sticky="w", **paddings, **ipaddings)

        # Frame for buttons
        # Frame
        ButtonFrame = ttk.Frame(
            master=self,
        )
        ButtonFrame.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Button - new expense
        AddNewEntryButton = ttk.Button(
            master=ButtonFrame,
            text="Add new expense",
            command=self.add_Expenses
        )
        AddNewEntryButton.pack(side=tk.LEFT, **paddings)

        # Button - modify record
        ModExpenseButton = ttk.Button(
            master=ButtonFrame,
            text="Modify",
            command=self.select_and_update_record,
        )
        ModExpenseButton.pack(side=tk.LEFT, **paddings)

        # Button - delete record
        DeleteButton = ttk.Button(
            master=ButtonFrame,
            text="Delete Entry",
            command=self.select_and_delete_record,
        )
        DeleteButton.pack(side=tk.LEFT, **paddings)

        # Button - Save and close
        SaveButton = ttk.Button(
            master=ButtonFrame,
            text="Save and close",
            command=self.save_and_close,
        )
        SaveButton.pack(side=tk.RIGHT, **paddings)

        # Button - Summary
        SummaryButton = ttk.Button(
            master=ButtonFrame,
            text="Summary",
            command=self.run_summary,
        )
        SummaryButton.pack(side=tk.RIGHT, **paddings)

        """ # Creates pop-up with detail info about selected expense.
        self.tableTreeview.bind("<<TreeviewSelect>>", self.DetailMessagebox) """


        self.mainloop()

    """ FUNCTIONS """

    @classmethod
    def getExpenseEntries(cls, EntryTuple: tuple, yearOfInterest: int, monthOfInterest: int) -> list:
        """Get data from new expenses entry and validates it."""
        EntryDataList = []
        isMandatoryDataOk = True

        # Check for mandatory data in place, Description (BonusEntry) isn't one of them.
        for _entryMandatory in EntryTuple[0:-1]:
            if _entryMandatory.get():
                pass
            else:
                isMandatoryDataOk = False
                showerror(
                    title="Entry error",
                    message="Entry Data is missing.",
                )
                _entryMandatory.focus_set()
                break

        if isMandatoryDataOk:
            """ Gets data from entries and append the list. """
            for _entry in EntryTuple:
                EntryDataList.append(_entry.get())
            # Those entries are always unique.
            # This clears them after the data is extracted. 
            EntryTuple[1].delete(0, tk.END)
            EntryTuple[3].delete(0, tk.END)

            """ Validation """
            # There are no restrictions on Amount entry. 
            # The value is rounded to 2 decimals.
            try:
                EntryDataList[1] = round(float(EntryDataList[1]), 2)
            except ValueError:
                showerror(
                    title="Amount error",
                    message=f"Wrong Amount format! Use only numbers with dot (Comma won't work.)",
                )
                EntryDataList.clear()
            
            ### Validation
            # Validates Entry year.
            if yearOfInterest != datetime.strptime(EntryDataList[0], "%d.%m.%Y").year:
                showerror(
                    title="Year error",
                    message=f"Wrong year in entry. This file year is {yearOfInterest}.",
                )
                EntryDataList.clear()
            else:
            # Validates Entry month.
                if monthOfInterest != datetime.strptime(EntryDataList[0], "%d.%m.%Y").month:
                    showerror(
                        title="Month error",
                        message=f"Wrong month in entry. You are currently working on {month_name[monthOfInterest]}.",
                    )
                    EntryDataList.clear()
                else:
                    # Paste --- in empty description
                    if not EntryDataList[3]:
                        EntryDataList[3] = "---"

        return EntryDataList


    def add_Expenses(self):
        """ Calls getExpenseEntries and use new data to append DataFrame and displayed table. """
        newLine = ExpensesApp.getExpenseEntries(
            (self.DateInput, self.AmountEntry, self.CatEntry, self.BonusEntry),
            self.yearOfInterest,
            self.monthOfInterest,
            )
        if newLine:
            # Append data Frame
            Wydatki_DataOperations.AppendDF_withList(self.expensesDF, newLine)
            # Append displayed table
            newLine.append(self.lastID)
            self.tableTreeview.insert('', tk.END, values=newLine)
            self.lastID += 1
    

    def select_and_update_record(self):
        """ Get selected record and pass data to new window to modify it. """
        # Read current row that are clicked and returns iid.
        selected = self.tableTreeview.focus()
        values = self.tableTreeview.item(selected, 'values')
        # If row is selected, new windows with entries to modify will open.
        if values:
            # Row update is taken care of inside new window's class.
            newWindow = ModifyExpensesWindow(self, selected, values, self.yearOfInterest, self.monthOfInterest)
            newWindow.grab_set()
        else:
            # If no row is selected, simple error message will appear.
            showerror(
                title="Error - no record selected",
                message="Select row to modify."
            )


    def select_and_delete_record(self):
        """ Get selected record and delete it. """
        selected = self.tableTreeview.focus()
        values = self.tableTreeview.item(selected, 'values')
        indexToDelete = values[4]
        if values:
            self.tableTreeview.delete(selected)
            Wydatki_DataOperations.deleteRow_inDF(self.expensesDF, indexToDelete)
        else:
            # If no row is selected, simple error message will appear.
            showerror(
                title="Error - no record selected",
                message="Select row to modify."
            )


    def save_and_close(self):
        Wydatki_DataOperations.saveFile(
            self.FileUser,
            self.monthOfInterest,
            self.yearOfInterest,
            self.expensesDF,
            environ["EXPENSES_PATH"]
        )
        self.destroy()


    def run_summary(self):
        newWindow = SummaryWindow(self)
        Wydatki_DataOperations.plot_summary(self.expensesDF, Category_Tuple, self.yearOfInterest, self.monthOfInterest)


class ModifyExpensesWindow(tk.Toplevel):
    def __init__(self, main, selected, data: tuple, year: int, month: int):
        super().__init__(main)

        # Those arguments are needed to validation and modification.
        # It's because row inside main window is changed inside this TopLevel window.
        self.master = main
        self.selectedRow = selected
        self.rowId = data[4]
        self.year = year
        self.month = month

        self.title("Modify the expense")

        """ Settings """

        ipaddings = {
            "ipady": 1,
            "ipadx": 1,
        }

        paddings = {
            "pady": 5,
            "padx": 5,
        }

        # Frame for entry
        # Frame 
        EntryFrame = ttk.Entry(
            master=self,
        )
        EntryFrame.pack()

        """ DATE """
        # Date Label
        DateLabel = ttk.Label(
            master=EntryFrame,
            text="Date:",
        )
        DateLabel.grid(column=0, row=0, sticky="w", **paddings)

        # Date Entry
        self.DateInput = DateEntry(
            master=EntryFrame,
            date_pattern="dd.mm.yyyy",
            year=self.year,
        )
        self.DateInput.set_date(data[0])
        self.DateInput.grid(column=0, row=1, sticky="w", **paddings, **ipaddings)

        """ AMOUNT """
        # Amount Label
        AmountLabel = ttk.Label(
            master=EntryFrame,
            text=f"Price [%s]:" % "zł"
        )
        AmountLabel.grid(column=1, row=0, sticky="w", **paddings)

        # Amount entry
        self.AmountEntry = ttk.Entry(
            master=EntryFrame,
        )
        self.AmountEntry.insert(0, data[1])
        self.AmountEntry.grid(column=1, row=1, sticky="w", **paddings, **ipaddings)

        """ CATEGORY """
        # Category Label
        CatLabel = ttk.Label(
            master=EntryFrame,
            text="Category:",
        )
        CatLabel.grid(column=2, row=0, sticky="w", **paddings)

        # Category Entry
        self.CatEntry = ttk.Combobox(
            master=EntryFrame,
            state="readonly",
            values=list(Category_Tuple)
        )
        # To set value to combobox instead of inserting the value the id of the value is needed.
        # In this case, index method get id using variable from data list.
        self.CatEntry.current(Category_Tuple.index(data[2]))
        self.CatEntry.grid(column=2, row=1, sticky="w", **paddings, **ipaddings)

        """ DESCRIPTION """
        # Bonus description Label
        BonusLabel = ttk.Label(
            master=EntryFrame,
            text="Description:"
        )
        BonusLabel.grid(column=3, row=0, sticky="w", **paddings)

        # Bonus description Entry
        self.BonusEntry = ttk.Entry(
            master=EntryFrame,
            width=50,
        )
        self.BonusEntry.insert(0, data[3])
        self.BonusEntry.grid(column=3, row=1, sticky="w", **paddings, **ipaddings)


        # Frame for buttons

        ButtonFrame = ttk.Frame(
            master=self
        )
        ButtonFrame.pack()

        # Button - Save and close
        ModifyButton = ttk.Button(
            master=ButtonFrame,
            text="Save and close",
            command=self.get_changed_data
        )
        ModifyButton.pack(side=tk.LEFT)

        # Button - close window without changes
        CloseButton = ttk.Button(
            master=ButtonFrame,
            text="Close without modifications",
            command=self.destroy
        )
        CloseButton.pack(side=tk.LEFT)

        """FUNCTIONS"""

    def get_changed_data(self):
        """ Calls getExpenseEntries from ExpensesApp and use it to extract data from entries and validate them.
        After validation, modifications take place."""
        newLine = ExpensesApp.getExpenseEntries(
            (self.DateInput, self.AmountEntry, self.CatEntry, self.BonusEntry),
            self.year,
            self.month,
            )
        if newLine:
            # If newLine exist (seen as True) The modifications takes place.
            # Change in table
            self.master.tableTreeview.item(self.selectedRow, values=(*newLine, self.rowId))
            # Change in data base
            Wydatki_DataOperations.updateDF_withList(self.master.expensesDF, newLine, self.rowId)
            self.destroy()


class SummaryWindow(tk.Toplevel):
    def __init__(self, main):
        super().__init__(main)

        self.master = main

        self.title("Summary")
        self.resizable = False

        # Getting data for summary
        income = Wydatki_DataOperations.total_income(self.master.expensesDF)
        expenses = Wydatki_DataOperations.total_expenses(self.master.expensesDF)
        balance = round(income - expenses, 2)
        food = Wydatki_DataOperations.Average_foodPerDay(
            self.master.expensesDF,
            self.master.yearOfInterest,
            self.master.monthOfInterest
        )

        # Preparing main string.
        summaryText = f"""
    -----Statistics-----
    Income:   {income} PLN    
    Expenses: {expenses} PLN   
    Balance:  {balance} PLN   
    Food:     {food[0]} PLN   
    Food Summary: {food[1]} PLN   
"""+Wydatki_DataOperations.category_expenses(self.master.expensesDF, Category_Tuple)

        """ WIDGETS """
        """ Settings """

        ipaddings = {
            "ipady": 1,
            "ipadx": 1,
        }

        paddings = {
            "pady": 5,
            "padx": 5,
        }

        ScrollFrame = ttk.Frame(
            master=self
        )
        ScrollFrame.grid()

        SummaryLabel = tk.Text(
            master=ScrollFrame,
            font=("Courier", 14),
            width=40
        )
        SummaryLabel.insert(tk.END, summaryText)
        SummaryLabel.grid(row=0, column=0, sticky="ns", **paddings, **ipaddings) 
        ScrollBar = ttk.Scrollbar(
            master=ScrollFrame,
            orient="vertical",
            command=SummaryLabel.yview
        )
        SummaryLabel.config(yscrollcommand=ScrollBar.set)
        ScrollBar.grid(row=0, column=1,sticky="ns", **paddings, **ipaddings)

if __name__ == "__main__":
    App = PathOpenerApp(environ["EXPENSES_PATH"])
    App.mainloop()
    print(App.filename)
    x = input()
