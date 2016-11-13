#build initial settings 

import sqlite3
import os

if os.path.exists('settings.db'):
    os.remove('settings.db')


conn = sqlite3.connect('settings.db')
c = conn.cursor()

base = [
    [0, 0],
    [50, 100],
    [0, 50],
    [100,100]
]

q  = '''create table hours (ROWID INTEGER PRIMARY KEY, h1 int, h2 int, h3 int);'''
c.execute(q)
conn.commit()
hrs = '''insert into hours (h1, h2, h3) VALUES (6, 17, 24)''';
c.execute(hrs)
conn.commit()


for i in range(1,5):
    print(i)
    m = ('create table mode{} ( ROWID INTEGER PRIMARY KEY, rest int, high int);').format(i)
    c.execute(m)
    conn.commit()

for i in range(0, 4):
    m = ('insert into mode{} (rest, high) VALUES ({}, {});').format(i+1, base[i][0], base[i][1])
    c.execute(m)
    conn.commit()



conn.close()

# conn.execute('''select name from sqlite_master where type='table';''')
#
# base[getIndex()][highTrig]
#
# ('select rest, high from mode{} where rowid = (select max(rowid) from mode{});').format(1,1)
