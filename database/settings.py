#create a home for your RPi to pull its settings from

import mysql.connector

conn = mysql.connector.connect(user='', password='', host='')

#build initial settings

name = 'under-cabinet'
location = 'kitchen'

base = [
    [0, 0],
    [50, 100],
    [0, 50],
    [100,100]
]

c = conn.cursor()

q = "insert into map.device (name, location) VALUES ('{}', '{}');".format(name, location)

c.execute(q)

#get device_id
q = "select max(id) from map.device where name = '{}' and location = '{}'".format(name, location)
c.execute(q)
x=c.fetchall()[0][0]

q= "create database device{};".format(x)
c.execute(q)

q  = '''create table device{}.hours (
        rowid INT NOT NULL AUTO_INCREMENT, 
        h1 int, 
        h2 int, 
        h3 int, 
        PRIMARY KEY (rowid));'''.format(x)


c.execute(q)

hrs = 'insert into device{}.hours (h1, h2, h3) VALUES (6, 17, 24)'.format(x)
c.execute(hrs)

for i in range(0, len(base)+1):
    print(i)
    m = ('create table device{}.mode{} ( rowid INT NOT NULL AUTO_INCREMENT, rest int, high int, PRIMARY KEY (rowid));').format(x, i)
    c.execute(m)

for i in range(0, len(base)+1):
    m = ('insert into device{}.mode{} (rest, high) VALUES ({}, {});').format(x, i, base[i][0], base[i][1])
    c.execute(m)

conn.commit()
conn.close()

