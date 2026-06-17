import sqlite3, pandas as pd
file = open("IPN_GB_2022.csv", "r")
df = pd.read_csv(file)
df.to_sql("data", sqlite3.connect("data.db"), if_exists="replace", index=False)