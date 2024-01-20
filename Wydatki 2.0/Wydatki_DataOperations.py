import pandas as pd
import json
from calendar import month_name, monthrange
import datetime
import matplotlib.pyplot as plt


""" Data manage """

def AppendDF_withList(DF: pd.DataFrame, NewRowList: list):
    DF.loc[DF.shape[0]] = NewRowList


def updateDF_withList(DF: pd.DataFrame, ModRowList: list, iRow: int):
    """ Modify data frame record with new entry """
    # In case iRow is string, not integer.
    DF.iloc[int(iRow)] = ModRowList


def deleteRow_inDF(DF: pd.DataFrame, iRow: int):
    DF.drop(int(iRow), inplace=True)


def refreshDF(DF):
    DF.sort_values(by="Date", inplace=True)
    DF.reset_index(inplace=True)
    DF.drop("index", axis=1, inplace=True)


def saveFile(User: str, month: int, year: int, data: pd.DataFrame, fileLocalization: str):
    refreshDF(data)
    dataJson = data.to_json()
    metadata = {
            "creator": User,
            "month": month,
            "year": year,
            "data": dataJson 
        }

    with open(fileLocalization+f"\\{year}_{month_name[month]}.txt", 'w') as file:
        file.write(json.dumps(metadata))


""" Plots calculations """

def expenses_per_day_Summary(DF: pd.DataFrame, year: int, month: int):
    """ Returns tuple that contains list of dates in month and list of Expenses in month, summed day by day. """
    daysInMonth, DF_date, ExpensesPerDay_List = daysInMonth_List(year, month)
    # Loops for every date in month, creates filter and sum Expenses from each day.
    for iday_ in range(daysInMonth):
        filt_ = (DF["Date"] == DF_date[iday_]) & (DF["Cat"] != "Income")
        # Assign value from last day to current day.
        # On the first day, index is equal -1, so the last element from list is assign to first day.
        # Because in this loop, index -1 exist and last element is 0, no error is rised and value is valid.
        ExpensesPerDay_List[iday_] = ExpensesPerDay_List[iday_-1]
        # Using filter, extract and sums expenses for current date
        ExpensesPerDay_List[iday_] += DF[filt_]["Amount"].sum()
        # Float after math operations have to be rounded to avoid too much digits after comma. 
        ExpensesPerDay_List[iday_] = round(ExpensesPerDay_List[iday_], 2)
    return (DF_date.to_list(), ExpensesPerDay_List)


def food_per_day(DF: pd.DataFrame, year: int, month: int):
    daysInMonth, DF_date, FoodPerDay_List = daysInMonth_List(year, month)
    for iday_ in range(daysInMonth):
        filt_ = (DF["Date"] == DF_date[iday_]) & (DF["Cat"] == "Food")
        # Works similar to loop in expenses_per_day_Summary, but different filter is used  
        FoodPerDay_List[iday_] = DF[filt_]["Amount"].sum()
        FoodPerDay_List[iday_] = round(FoodPerDay_List[iday_], 2)
    return (DF_date.to_list(), FoodPerDay_List)


def expenses_per_Category(DF: pd.DataFrame, categoryList: list):
    categoryList.remove("Income")
    ExpensesPerCategory_List = [0 for _ in range(len(categoryList))]
    for iCat_ in range(len(categoryList)):
        filt_ = (DF["Cat"] == categoryList[iCat_])
        ExpensesPerCategory_List[iCat_] = round(DF[filt_]["Amount"].sum(), 2)
    return (categoryList, ExpensesPerCategory_List)


""" Other calculations """

def daysInMonth_List(year, month):
    """ Creates tuple with number of days in month, DataFrame with dates in this month and list size-fitted to previous DataFrame. """
     # extract number of days in month.
    daysInMonth = monthrange(year, month)[1]
    # Creates pd.Series with date for every day in the month.
    DF_date = pd.date_range(datetime.datetime(year, month, 1), periods=daysInMonth).strftime("%d.%m.%Y")
    # Defines list for expenses
    ExpensesPerDay_List = [0 for i in range(daysInMonth)]
    return (daysInMonth, DF_date, ExpensesPerDay_List)


def total_income(DF: pd.DataFrame):
    """ Returns total income in this month"""
    filt_ = (DF["Cat"] == "Income")
    return round(DF[filt_]["Amount"].sum(), 2)


def total_expenses(DF: pd.DataFrame):
    """ Returns total expenses in this month """
    filt_ = (DF["Cat"] != "Income")
    return round(DF[filt_]["Amount"].sum(), 2)


def Average_foodPerDay(DF: pd.DataFrame, year: int, month: int):
    today = datetime.datetime.today()
    if today.month == month and today.year == year:
        dayNumber = today.day
    else:
        dayNumber = monthrange(year, month)[1]

    filt_ = (DF["Cat"] == "Food")
    FoodPerDay = DF[filt_]["Amount"].sum()/dayNumber
    filt_ = (DF["Cat"] == "Food") | (DF["Cat"] == "EatingOutside")
    EveryFoodPerDay = DF[filt_]["Amount"].sum()/dayNumber
    return (round(FoodPerDay, 2), round(EveryFoodPerDay, 2))


""" Plots """

def plot_summary(DF: pd.DataFrame, categoryTuple: tuple, year: int, month: int):
    """ Print plots """
    #Style
    plt.style.use("dark_background")
    CatColors = {"Income": '#6C3483',
                "Bill": '#21618C',
                "SelfCare": '#A93226',
                "Household": '#138D75',
                "Food": '#D68910',
                "EatingOutside": '#A6ACAF',
                "Party": '#D2B4DE',
                "Ticket": '#D5D8DC',
                "Clothes": '#21618C',
                "Hobby": '#FFFFFF',
    }

    # Create plot matrix
    fig, ax = plt.subplots(nrows=2, ncols=2, sharex=False)
    fig.suptitle("Expenses")

    # Left top - pie chart (expenses per category)
    cat_exp = expenses_per_Category(DF, list(categoryTuple))
    ax[0, 0].pie(
        cat_exp[1],
        labels=cat_exp[0],
        rotatelabels=True,
        labeldistance=1,
        colors=CatColors.values()
    )

    # Right top - bar chart (expenses per category)
    ax[0, 1].bar(
        cat_exp[0],
        cat_exp[1],
        label=cat_exp[0],
        color=CatColors.values()
    )
    ax[0, 1].tick_params(
        axis="x",
        rotation=15
    )
    ax[0, 1].spines["top"].set_visible(False)
    ax[0, 1].spines["right"].set_visible(False)
    ax[0, 1].set_ylabel("Expenses [PLN]")

    # Left bottom - bar chart (food per day)
    fPD = food_per_day(DF, year, month)
    ax[1, 0].bar(
        range(1, len(fPD[0])+1),
        fPD[1],
        color="#0DFA10",
        edgecolor="#000000",
        width=1
    )
    ax[1, 0].spines['top'].set_visible(False)
    ax[1, 0].spines['right'].set_visible(False)
    ax[1, 0].set_ylabel('expenses [PLN]')
    ax[1, 0].set_xlabel('Day int the Month')
    # average expenses for food per day line
    avrF, _ =  Average_foodPerDay(DF, year, month)
    ax[1, 0].axhline(y=avrF)
    ax[1, 0].text(
        30,
        avrF,
        "Average",
        bbox=dict(boxstyle='round', facecolor='#000000', edgecolor='#0DFA10')
    )

    # Right bottom - plot (expenses per day)
    day_exp = expenses_per_day_Summary(DF, year, month)
    dates = pd.to_datetime(day_exp[0], format="%d.%m.%Y")
    ax[1, 1].plot_date(
        x=dates,
        y=day_exp[1],
        linestyle="solid",
        color="#0DFA10"
    )
    ax[1, 1].tick_params(axis='x', rotation=25)
    ax[1, 1].set_xlim(dates[0], dates[-1])
    ax[1, 1].spines['top'].set_visible(False)
    ax[1, 1].spines['right'].set_visible(False)
    ax[1, 1].set_ylabel("Expenses [PLN]")
    ax[1, 1].grid()

    plt.tight_layout()
    plt.show()


""" Summary """

def category_expenses(DF: pd.DataFrame, categoryTuple: tuple) -> str:
    string_ = f"""
    By Category:\n
"""
    for cat_ in categoryTuple:
        filt_ = (DF["Cat"] == cat_)
        DF_ = DF[filt_]
        string_ += f"""
    ### {cat_} ###"""
        for i in range(DF_.shape[0]):
            string_ += f"""
    - {round(DF_.iloc[i]["Amount"], 2)}  {DF_.iloc[i]["BonusDesc"]}"""
        string_ += f"""
    ----Summary for {cat_}----
    {round(DF_["Amount"].sum(), 2)} PLN
"""
    return string_