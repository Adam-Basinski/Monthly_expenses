from datetime import date
import os.path
from os import getlogin
from calendar import month_name
from tkinter.messagebox import showerror
import json

""" Use to create new file that will be used in  """

if __name__ == "__main__":
    exit()

today = date.today()
newFileName = f"{today.year}_{month_name[today.month]}"
folderLoc = f"D:\\Wydatki\\{newFileName}.txt"

isFile = os.path.isfile(folderLoc)

if not isFile:
    with open(folderLoc, "w") as file:
        data = {
            "creator": getlogin(),
            "month": today.month,
            "year": today.year,
            "data": '' 
        }
        file.write(json.dumps(data))
        print(f"New Folder is created")

else:
    showerror(
        title="This file already exist.",
        message=f"{newFileName} already exist."
    )