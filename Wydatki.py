from tkinter import filedialog
import pandas as pd
import tkinter as tk
import datetime
import calendar
import matplotlib.pyplot as plt
from math import isnan


Categories = [
    "Rent",
    "Food",
    "Cosmetics",
    "BonusFood",
    "Parties",
    "Tickets",
    "University",
    "Hobby",
    "Clothes"
]
CatIndexes = ['R', 'F', 'C', 'BF', 'P', 'T', 'U', 'H', 'CL']
CatColors = ['#6C3483', '#21618C', '#A93226', '#138D75',
             '#D68910', '#A6ACAF', '#D2B4DE', '#D5D8DC', '#21618C']


# Getting filepath command
def get_file_path():
    global filename
    filetypes = [('CSV files', '*.csv'),
                 ('TXT files', '*.txt'),
                 ('all files', '*.*')]
    filename = filedialog.askopenfilename(
        title='Open CSV file',
        filetypes=filetypes,
        initialdir='D:\\Wydatki'
    )
    window.destroy()


# Getting summary expenses for each category.
def expenses_by_category():
    expenses = [0 for i in range(len(CatIndexes))]
    for index in range(len(data['Cat'])):
        category = data['Cat'][index]
        for i in range(len(CatIndexes)):
            if category == CatIndexes[i]:
                expenses[i] += data['Amount'][index]
    return expenses


# Getting list of expenses for food for each day in the month
def Food_per_day():
    expenses = [0 for i in range(daysinmonth)]
    for date in AllDaysInTheMonthList:
        for i in range(len(data['Cat'])):
            if date == data['Date'][i] and data['Cat'][i] == 'F':
                expenses[date.day-1] += data['Amount'][i]
    return expenses

# Getting list of expenses for all Categories for each day


def Summary_expenses_per_day():
    expenses = [0 for i in range(daysinmonth)]
    for date in AllDaysInTheMonthList:
        SpendToday = 0
        for i in range(len(data['Cat'])):
            if date == data['Date'][i]:
                if data["Cat"][i] != "INC":
                    SpendToday += data['Amount'][i]
        expenses[date.day-1] = expenses[date.day-2]
        expenses[date.day-1] += SpendToday
    return expenses

# Count total income in month


def Total_income():
    Total_income = 0
    for i in range(len(data['Cat'])):
        if data['Cat'][i] == 'INC':
            Total_income += data['Amount'][i]
    return Total_income


def upper_cat(category):
    return category.upper()

    # Displaying window to get filepath
window = tk.Tk()
window.title('Choose csv file')
window.resizable(True, True)
window['background'] = 'green'
window.geometry('300x150')

open_button = tk.Button(
    window,
    text='Choose CSV file',
    activebackground='green',
    activeforeground='green',
    command=get_file_path
)
open_button.pack(expand=True)
window.mainloop()

# Data reading from chosen CSV file
data = pd.read_csv(filename, sep=';', encoding='utf8', engine='python')
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
data.sort_values('Date', inplace=False)
data['Cat'] = data['Cat'].apply(upper_cat)

# Generating list with all days in the month
firstdatinmonth = datetime.datetime(
    data["Date"][0].year, data["Date"][0].month, 1)
daysinmonth = calendar.monthrange(
    data["Date"][0].year, data["Date"][0].month)[1]
AllDaysInTheMonthList = pd.date_range(firstdatinmonth, periods=daysinmonth)
AllDaysInTheMonthList.strftime("%Y-%m-%d")
Dates = pd.to_datetime(AllDaysInTheMonthList, dayfirst=True)
# return as daysinmonth_foraverage number of all days in the month if the one is other than the current month.
# If file contain current month it will return today's day number.
if datetime.datetime.today().month == data["Date"][0].month:
    daysinmonth_foraverage = datetime.datetime.today().day
else:
    daysinmonth_foraverage = daysinmonth

# Getting length of the longest number in list
longest_length = 0
for i in data['Amount']:
    x = len(str(i))
    if x > longest_length:
        longest_length = x

longest_length_category = 0
for i in Categories:
    x = len(str(i))
    if x > longest_length_category:
        longest_length_category = x

# Using functions to get lists and other calculations
expensesByCategory = expenses_by_category()
expensesForFood = Food_per_day()
expensesPerDay = Summary_expenses_per_day()
average_expenses_for_food_per_day = sum(
    expensesForFood)/daysinmonth_foraverage
average_expenses_for_every_food_per_day = (
    sum(expensesForFood)+expensesByCategory[3])/daysinmonth_foraverage
Income = Total_income()

# Plots
plt.style.use('dark_background')

fig, ax = plt.subplots(nrows=2, ncols=2, sharex=False)

# Left top pie chart
ax[0, 0].pie(expensesByCategory, labels=Categories,
             rotatelabels=True, labeldistance=1, colors=CatColors)

# Right top bar chart
ax[0, 1].bar(Categories, expensesByCategory, label=Categories, color=CatColors)
ax[0, 1].tick_params(axis='x', rotation=15)
ax[0, 1].spines['top'].set_visible(False)
ax[0, 1].spines['right'].set_visible(False)
ax[0, 1].set_ylabel('expenses [PLN]')

# Left bottom bar chart
ax[1, 0].bar(range(1, daysinmonth+1), expensesForFood,
             color='#0DFA10', edgecolor='#000000', width=1)
ax[1, 0].spines['top'].set_visible(False)
ax[1, 0].spines['right'].set_visible(False)
ax[1, 0].set_ylabel('expenses [PLN]')
ax[1, 0].set_xlabel('Day int the Month')
ax[1, 0].axhline(y=average_expenses_for_food_per_day)
ax[1, 0].text(daysinmonth-3, average_expenses_for_food_per_day-4, "Average",
              bbox=dict(boxstyle='round', facecolor='#000000', edgecolor='#0DFA10'))

# Right bottom plot
ax[1, 1].plot_date(Dates, expensesPerDay, linestyle='solid', color='#0DFA10')
ax[1, 1].tick_params(axis='x', rotation=25)
ax[1, 1].set_xlim(Dates[0], Dates[-1])
ax[1, 1].spines['top'].set_visible(False)
ax[1, 1].spines['right'].set_visible(False)
ax[1, 1].set_ylabel('expenses [PLN]')
ax[1, 1].grid()

# Adding main title
fig.suptitle('My Expenses')

# Printing report
spacer = ' '
print("---My Expenses---")
print('-'*40)

# Printing every expenses sorted and with description if needed.
for Category in range(len(CatIndexes)):
    print(' # ', Categories[Category]+':')
    for i in range(len(data['Cat'])):
        if CatIndexes[Category] == data['Cat'][i]:
            if type(data['BonusDesc'][i]) == type('-'):
                pass
            else:
                if isnan(data['BonusDesc'][i]):
                    data.loc[i] = [data['Date'][i],
                                   data['Amount'][i], data['Cat'][i], '---']
            # length correction
            length_correction = longest_length - len(str(data['Amount'][i]))
            print(spacer, round(data['Amount'][i], 2), 'PLN',
                  '   ', ' '*length_correction, data['BonusDesc'][i])
    print('-'*40)

# Printing rest data
print("---Statistic---")
print(spacer, 'Total Incomes:           ', Income, 'PLN')
print(spacer, 'Total Expenses:          ',
      round(sum(expensesByCategory), 2), 'PLN')
print(spacer, 'Balance:                 ', Income -
      round(sum(expensesByCategory), 2), 'PLN')
print(spacer, 'Average Expenses for food:', round(
    average_expenses_for_food_per_day, 2), 'PLN')
print(spacer, 'Average Expenses for every food:', round(
    average_expenses_for_every_food_per_day, 2), 'PLN')
print(spacer, 'Expenses by category:')
for i in range(len(Categories)):
    length_correction_categories = longest_length_category - \
        len(str(Categories[i]))
    print(Categories[i], ' '*length_correction_categories,
          round(expensesByCategory[i], 2), ' PLN')
print('-'*40)

# If unknown categories
if_unknown_category = ~data['Cat'].isin(CatIndexes)
for i in range(len(if_unknown_category)):
    if if_unknown_category[i] == True:
        if data.loc[i, 'Cat'] != 'INC':
            print(spacer, str(data.loc[i, 'Date'].day) + "'th of the month",
                  data.loc[i, 'Amount'], 'PLN', "Unknown category:", data.loc[i, 'Cat'])


# Showing SubPlot
plt.tight_layout()
plt.show()
