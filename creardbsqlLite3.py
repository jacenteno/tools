import sqlite3
conn = sqlite3.connect('datacollect.db')
print ("Opened database successfully")
conn.execute('''CREATE TABLE TIENDA
         (ID INT PRIMARY KEY     NOT NULL,
         NAME            TEXT    NOT NULL,
         ADDRESS         CHAR(50));''')
print ("Table created successfully")
conn.close()