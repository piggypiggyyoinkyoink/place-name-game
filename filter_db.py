import sqlite3
con = sqlite3.connect("data.db")
cur = con.cursor()
cur.execute("DELETE FROM data WHERE descnm IN ('CTY', 'CTYHIST', 'WD', 'CED', 'NMD', 'NPARK', 'CA', 'MD', 'UA', 'BUA', 'CTYLT')")
cur.execute("DELETE FROM data WHERE descnm = 'PAR' AND placesort LIKE '%and%'")
cur.execute("DELETE FROM data WHERE descnm = 'PAR' AND placesort LIKE '%with%'")
cur.execute("DELETE FROM data WHERE descnm = 'PAR' AND placesort LIKE '%unparished%'")
con.commit()
con.close()