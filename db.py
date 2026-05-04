import sqlite3

conn = sqlite3.connect('mdb.db')
conn.execute("DROP TABLE IF EXISTS employees")
conn.execute("DROP TABLE IF EXISTS admin")
conn.execute("DROP TABLE IF EXISTS mdbevent")
conn.execute("DROP TABLE IF EXISTS dayoff")
conn.execute('CREATE TABLE employees (name TEXT, ID TEXT, cardID TEXT, itemLimit INT, leftItem INT, status INT)')
conn.execute('CREATE TABLE admin (name TEXT, email TEXT, password TEXT, itemLimit INT)')
conn.execute('CREATE TABLE mdbevent (dailylimit INT, machineStatus INT)')
conn.execute('CREATE TABLE dayoff (date timestamp, machineStatus INT )')
conn.close()
# machinestatus 0-off, 1-on