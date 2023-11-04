#!/usr/bin/env python
import sys
import os
import time
import datetime
import glob
import MySQLdb
from time import strftime

### CTp6 ###
temp_sensor = ["28-0114535371aa", "28-01144f3b3daa", "28-01145346eeaa", "28-0114534e88aa", "28-0114533d0daa", "28-011453479caa", "28-01144f52d5aa", "28-01144f3cb6aa", "28-0301a279fb44"]
crplada = ["CRP1", "CRP2", "Lada1", "Lada2", "Lada3", "Lada4", "Lada5", "Lada6", "Refrigerator"]
offset = [0, 0, 0, 0, 0, 0, -0.7, 1.4, 0]
############
### CTg ###
# temp_sensor = ["28-01144f4794aa", "28-01144f51f9aa", "28-01144f5062aa", "28-0114535388aa", "28-011937c7f1ec", "28-011937d38394", "28-0301a2793b45"]
# crplada = ["Lada1", "Lada2", "Lada3", "Lada4", "Orizontal1", "Orizontal2", "Refrigerator"]
# offset = [-0.3, -0.5, 0.8, 0.2, 0.2, 2.7, 0]
###########
### Fet ###
# temp_sensor = ["28-0301a279238a", "28-3c01a8169ad6", "28-01193811282b", "28-011937aa85f3", "28-3c01a816d398"]
# crplada = ["Lada1", "Lada2", "Lada3", "Lada4", "Refrigerator"]
# offset = [0, 0, 0, 0, 3]
###########

# Get first argument to see what Database it's changing
dbname = sys.argv[1]    # readTempSQL.py - temp_database ; readTempTwo.py - temperaturi

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Variables for MySQL
db = MySQLdb.connect(host = "localhost", user = "root", passwd = "<password>", db = dbname)
cur = db.cursor()

def tempRead(selector):
    t = open("/sys/bus/w1/devices/" + temp_sensor[selector] + "/w1_slave", 'r')
    lines = t.readlines()
    t.close()
    temp_output = lines[1].find('t=')
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string)/1000.0
    return round(temp_c, 1)

while True:
        dateWrite = time.strftime("%Y-%m-%d")
        timeWrite = time.strftime("%H:%M")
        for i in range(0, len(crplada)):
            if os.path.isdir("/sys/bus/w1/devices/" + temp_sensor[i]) == 1:
                temp = tempRead(i) + offset[i]
            else:
                temp = 99
            print temp
            sql = ('INSERT INTO ' + crplada[i] + ' (date,time,temperature) VALUES (%s,%s,%s)',(dateWrite, timeWrite, temp))
            try:
                print "Writing to database..."
                # Execute the SQL command
                cur.execute(*sql)
                # Commit your changes in the database
                db.commit()
                print "Write Complete"
            except:
                # Rollback in case there is any error
                db.rollback()
                print "Failed writing to database"
        cur.close()
        db.close()
        break
