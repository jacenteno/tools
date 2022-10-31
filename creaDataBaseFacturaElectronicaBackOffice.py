import sqlite3
conn = sqlite3.connect('FeDataCollect.db')
print ("Opened database successfully")
conn.execute('''CREATE TABLE FELECTRONICA
         (ID INT PRIMARY KEY     NOT NULL,
         TIENDA            TEXT    NOT NULL,
         ADDRESS         CHAR(50));''')
print ("Table created successfully")
conn.close()