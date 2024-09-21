from datetime import datetime
import pandas as pd
from tkinter.filedialog import askopenfilename

def valTime(data):
    test_date = data.split("+")[0]
    if (len(test_date) == 19):
        test_date = test_date + ".000000"
    return datetime.strptime(test_date, "%Y-%m-%d %H:%M:%S.%f")

filename = askopenfilename()
df = pd.read_csv(filename)

df["fuel_psi_time"] = df["time"].apply(lambda x: valTime(x))
df["lox_psi_time"] = df["time"].apply(lambda x: valTime(x))
df = df.drop('time', axis=1)

df = df[["fuel_psi_time", "fuel_psi", "lox_psi_time", "lox_psi"]]

df.to_csv(filename[0:-4] + "_processed.csv", index=False)
