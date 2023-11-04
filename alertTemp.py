#!/usr/bin/env python
import os
import time
import datetime
import glob
import MySQLdb
import telepot
from time import strftime
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

telegramid = ""

### CTp6 ###
bot = telepot.Bot('')
crplada = ["CRP1", "CRP2", "Lada1", "Lada2", "Lada3", "Lada4", "Lada5", "Lada6", "Refrigerator"]
alertlada = [-10, -10, 5, 5, 50, 5, 60, 50, 3]
############
### CTg ###
# bot = telepot.Bot('')
# crplada = ["Lada1", "Lada2", "Lada3", "Lada4", "Orizontal1", "Orizontal2", "Refrigerator"]
# alertlada = [5, 5, 60, -10, 6, 6, 3]
###########
### Fet ###
# bot = telepot.Bot('')
# crplada = ["Lada1", "Lada2", "Lada3", "Lada4", "Refrigerator"]
# alertlada = [7, 7, 7, 7, 5]
###########

# Variables for MySQL
db = MySQLdb.connect(host="localhost", user="root", passwd="<password>", db="temp_database")
cur = db.cursor()

def chart(vector, crpladacurrent, avgtemp):
        t = np.array(vector)
        s = np.arange(0, 288, 1)
        fig, ax = plt.subplots(1, 1, figsize = (12, 6), dpi = 200)
        ax.plot(s, t)
        ax.set_yscale('linear')
        ax.invert_xaxis()
        ax.set(xlabel = 'last 288 temperatures', ylabel = 'temperature',
               title = crpladacurrent + "\ntemp. medie ultimele 2 ore: " + avgtemp)
        ax.grid()
        fig.savefig('temp.png')

while True:
        for i in range(0, len(crplada)):
                sql = ('SELECT AVG(temperature) FROM (SELECT `temperature` FROM ' + crplada[i] + ' ORDER BY `id` DESC LIMIT 12) t1')
                print "Fetching data from database..."
                # Execute the SQL command
                cur.execute(sql)
                temp=str(cur.fetchone())
                temp=temp[1:-2]
		if float(temp)>=alertlada[i]:
                        sql = ('SELECT `temperature` FROM ' + crplada[i] + ' ORDER BY `id` DESC LIMIT 288')
                        cur.execute(sql)
                        vector = cur.fetchall()
                        chart(vector, crplada[i], temp)
			bot.sendMessage(telegramid, "ALERT: " + crplada[i] + " : " + temp)
			bot.sendPhoto(telegramid, photo = open('temp.png', 'rb'))
                print "Fetching Complete"
                time.sleep(1)
        cur.close()
        db.close()
        break
