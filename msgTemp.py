#!/usr/bin/env python
import os
import time
import glob
import MySQLdb
import telepot
from telepot.loop import MessageLoop
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

### CTp6 ###
bot = telepot.Bot('')
temp_sensor = ["28-0114535371aa", "28-01144f3b3daa", "28-01145346eeaa", "28-0114534e88aa", "28-0114533d0daa", "28-011453479caa", "28-01144f52d5aa", "28-01144f3cb6aa", "28-0301a279fb44"]
crplada = ["CRP1", "CRP2", "Lada1", "Lada2", "Lada3", "Lada4", "Lada5", "Lada6", "Refrigerator"]
offset = [0, 0, 0, 0, 0, 0, -0.7, 1.4, 0]
############
### CTg ###
# bot = telepot.Bot('')
# temp_sensor = ["28-01144f4794aa", "28-01144f51f9aa", "28-01144f5062aa", "28-0114535388aa", "28-011937c7f1ec", "28-011937d38394", "28-0301a2793b45"]
# crplada = ["Lada1", "Lada2", "Lada3", "Lada4", "Orizontal1", "Orizontal2", "Refrigerator"]
# offset = [-0.3, -0.5, 0.8, 0.2, 0.2, 2.7, 0]
###########
### Fet ###
# bot = telepot.Bot('')
# temp_sensor = ["28-0301a279238a", "28-3c01a8169ad6", "28-01193811282b", "28-011937aa85f3", "28-3c01a816d398"]
# crplada = ["Lada1", "Lada2", "Lada3", "Lada4", "Refrigerator"]
# offset = [0, 0, 0, 0, 3]
###########

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

def cpu_temp():
        cputemp = os.popen("vcgencmd measure_temp").readline()
        return cputemp.replace('temp=','')

def tempRead(selector):
    t = open("/sys/bus/w1/devices/" + temp_sensor[selector] + "/w1_slave", 'r')
    lines = t.readlines()
    t.close()
    temp_output = lines[1].find('t=')
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string)/1000.0
    return round(temp_c, 1)

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
    fig.savefig('temp2.png')

def querydb(chat_id):
    # Variables for MySQL
    db = MySQLdb.connect(host = "localhost", user = "root", passwd = "<password>", db = "temp_database")
    cur = db.cursor()
    for i in range(0, len(crplada)):
        sql = ('SELECT AVG(temperature) FROM (SELECT `temperature` FROM ' + crplada[i] + ' ORDER BY `id` DESC LIMIT 12) t1')
        print "Fetching data from database..."
        # Execute the SQL command
        cur.execute(sql)
        temp = str(cur.fetchone())
        temp=temp[1:-2]
        sql = ('SELECT `temperature` FROM ' + crplada[i] + ' ORDER BY `id` DESC LIMIT 288')
        cur.execute(sql)
        vector = cur.fetchall()
        chart(vector, crplada[i], temp)
        bot.sendPhoto(chat_id, photo = open('temp2.png', 'rb'))
        print "Fetching Complete"
        time.sleep(1)
    cur.close()
    db.close()

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    if command == '/help':
        bot.sendMessage(chat_id, "List of commands:\n/temp\n/grafic")
    elif command == '/temp':
        for i in range(0, len(crplada)):
		if os.path.isdir("/sys/bus/w1/devices/" + temp_sensor[i])==1:
                        temp = tempRead(i) + offset[i]
                else:
                        temp = 99
                print temp
                bot.sendMessage(chat_id, crplada[i] + " : " + str(temp))
    elif command == '/grafic':
        querydb(chat_id)

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while True:
	time.sleep(10)
	cputemp=int(cpu_temp()[:-5])
        if cputemp > 60:
		bot.sendMessage("", "CPU TEMP > 60 = " + str(cputemp))
