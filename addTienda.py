import sqlite3

def getDeveloperInfo(id):
    try:
        sqliteConnection = sqlite3.connect('datacollect.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sql_select_query = """select * from tienda where id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()
        print("Printing ID ", id)
        for row in records:
            print("Name = ", row[1])
            print("Address  = ", row[2])
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")


def insertIntoSucurale(id, name, address):
    try:
        sqliteConnection = sqlite3.connect('datacollect.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_insert_with_param = """INSERT INTO tienda
                          (id, name, address) 
                          VALUES (?, ?, ?);"""

        data_tuple = (id, name, address)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        print("Python Variables inserted successfully into datacollect table")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")


def readLimitedRows(rowSize):
    try:
        sqliteConnection = sqlite3.connect('datacollect.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = """SELECT * from tienda"""
        cursor.execute(sqlite_select_query)
        print("Reading ", rowSize, " rows")
        records = cursor.fetchmany(rowSize)
        print("Printing each row \n")
        for row in records:
            print("Id: ", row[0])
            print("Name: ", row[1])
            print("address: ", row[2])
          
            print("\n")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

readLimitedRows(2)
getDeveloperInfo(1)
# insertIntoSucurale(3, 'Super Centro', 'santiago')
# insertIntoSucurale(4, 'Calobre', 'Calobre')
# recordsToInsert = [(4, 'Jos', 'jos@gmail.com', '2019-01-14', 9500),
 