from Wydatki_tkinter import PathOpenerApp, ExpensesApp
import pandas as pd
from json import load
from os import environ

# getting path for file we want to open
AppOpenPath = PathOpenerApp(environ["EXPENSES_PATH"])

# Opening file and reading to json
with open(AppOpenPath.filename, "r") as file:
    JsonFile = load(file)
# Extracting data from Json file.
# Converting json data to pandas DataFrame
RawData = pd.read_json(JsonFile["data"], convert_dates=False, encoding="utf8")

# Main Expenses app for displaying and working with expenses.
AppExpensesDisplay = ExpensesApp(expenses=RawData, month=JsonFile["month"], year=JsonFile["year"], user=JsonFile["creator"])

