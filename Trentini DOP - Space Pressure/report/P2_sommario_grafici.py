######################################################################################
#   ASTROPI 2018 - MISSION "SPACE LAB" (Life inSpace): GRUPPO TRENTINI DOP (Italy)   #
######################################################################################

#==========================================================================

##### Import - Librerie ####
from time import sleep,time
from datetime import datetime,timedelta
import sys
import re
import os
import imutils
import cv2
import numpy as np
from matplotlib import pyplot as plt
import ephem
from math import degrees
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Circle,Patch
import matplotlib.lines as mlines
from matplotlib.ticker import NullFormatter  # useful for `logit` scale

from scipy.optimize import curve_fit

def func(x, a, b, c):
    return a + b * np.exp(-1.0 * c * x)

#==========================================================================

# Formato del file CSV:
#ora,temperatura_CPU,temperatura,umidita',pressione,beccheggio,rollio,imbardata,mag_x,mag_y,mag_z,accel_x,accel_y,accel_z,giro_x,giro_y,giro_z
#2018-04-27 08:36:58.948717,36.3,32.026214599609375,33.42070007324219,1001.752685546875,12.662729320228529,15.489296386532525,32.580562416472766,27.436603546142578,-11.285003662109375,58.11085510253906,-0.0024683563970029354,0.0019423406338319182,0.01803356595337391,0.17663809657096863,0.14376232028007507,0.06413397938013077

##### Programma principale #####        
file_dati = open("TDOP_2018-04-27_08.36.57.csv", "r")
time_ref = datetime.strptime("2018-04-27 08:36:58.948717", "%Y-%m-%d %H:%M:%S.%f")

ora_inizio = time()
print(datetime.fromtimestamp(ora_inizio).strftime("=========================================== Inizio analisi: %Y-%m-%d %H:%M:%S.%f"))
progressivo = -1
xdata = []
xlabels = []
y01 = []
y02 = []
y03 = []
y04 = []
y05 = []
y06 = []
y07 = []
y08 = []
y09 = []
y10 = []
y11 = []
y12 = []
y13 = []
y14 = []
y15 = []
y16 = []
for riga_dati in file_dati:
    progressivo += 1
    # salto la riga di intestazione
    if ((progressivo == 0)): # or (progressivo > 500)):
        continue
    dati = riga_dati.split(",")
    timestamp_dato = datetime.strptime(dati[0], "%Y-%m-%d %H:%M:%S.%f")
    td = timestamp_dato - time_ref
    xdata.append(td.total_seconds()/3600.0)
    xlabels.append(timestamp_dato.strftime("%H:%M"))
    
    y01.append(float(dati[1])) # temperatura_CPU
    y02.append(float(dati[2])) # temperatura
    y03.append(float(dati[3])) # umidita'
    y04.append(float(dati[4])) # pressione
    y05.append(float(dati[5])) # beccheggio / 
    y06.append(float(dati[6])) # rollio /
    y07.append(float(dati[7])) # imbardata /
    y08.append(float(dati[8])) # mag_x
    y09.append(float(dati[9])) # mag_y
    y10.append(float(dati[10])) # mag_z
    y11.append(float(dati[11])) # accel_x
    y12.append(float(dati[12])) # accel_y
    y13.append(float(dati[13])) # accel_z
    y14.append(float(dati[14])) # giro_x
    y15.append(float(dati[15])) # giro_y
    y16.append(float(dati[16])) # giro_z
    #print("%d,%s,%.4f,%.4f,%s" % (progressivo, timestamp_dato.strftime("%Y-%m-%d %H:%M:%S.%f"), xdata[-1], ydata[-1], xlabels[-1]))
  
ora_fine = time()
print(datetime.fromtimestamp(ora_inizio).strftime("=========================================== Fine analisi: %Y-%m-%d %H:%M:%S.%f"), end='')
print(" [durata secondi: ", ora_fine-ora_inizio, "]")

file_dati.close()

plt.figure(1)
#f.subplots_adjust(hspace=0.3)

"""
f, axarr = plt.subplots(231)
plt.title('Analisi della temperatura')
plt.plot(xdata, y01, 'b-', label='temperatura CPU')
plt.plot(xdata, y02, 'r-', label='temperatura misurata')
plt.legend()
#axarr[0].set_ylabel('Temperatura (°C)')
#axarr[0].set_xlabel('Tempo (ore a partire dall\'inizio dell\'esperimento)')

f, axarr = plt.subplots(232)
plt.title("Analisi dell'umidità")
plt.plot(xdata, y03, 'g+', label='umidità')
plt.legend()
#axarr[1].set_ylabel("Umidità (%)")
#axarr[1].set_xlabel('Tempo (ora GMT)')

f, axarr = plt.subplots(233)
plt.title("Analisi della pressione")
plt.plot(xdata, y04, 'g+', label='pressione')
plt.legend()
#axarr[2].set_ylabel("Pressione (mBar)")
#axarr[2].set_xlabel('Tempo (ora GMT)')

f, axarr = plt.subplots(234)
plt.title("Analisi del giroscopio")
plt.plot(xdata, y05, 'g+', label='beccheggio')
plt.plot(xdata, y06, 'r>', label='rollio')
plt.plot(xdata, y07, 'bx', label='imbardata')
plt.legend()
#axarr[3].set_ylabel("Pressione (mBar)")
#axarr[3].set_xlabel('Tempo (ora GMT)')

f, axarr = plt.subplots(235)
plt.title("Analisi del magnetometro")
plt.plot(xdata, y08, 'g+', label='mag_x')
plt.plot(xdata, y09, 'r>', label='mag_y')
plt.plot(xdata, y10, 'bx', label='mag_z')
plt.legend()
#axarr[4].set_ylabel("Pressione (mBar)")
#axarr[4].set_xlabel('Tempo (ora GMT)')

f, axarr = plt.subplots(236)
plt.title("Analisi dell'accelerometro")
plt.plot(xdata, y11, 'g+', label='accel_x')
plt.plot(xdata, y12, 'r>', label='accel_y')
plt.plot(xdata, y13, 'bx', label='accel_x')
plt.legend()
#axarr[5].set_ylabel("Pressione (mBar)")
#axarr[5].set_xlabel('Tempo (ora GMT)')

#giro_x,giro_y,giro_z

plt.xticks(xdata[::900], xlabels[::900])
plt.show()
"""


# plot with various axes scales
plt.figure(1)
plt.figure(1).tight_layout()  # otherwise the right y-label is slightly clipped

# Temperatura
plt.subplot(231)
plt.title('Temperatures') # Temperature | Temperatures
plt.plot(xdata, y01, 'b-', label='CPU temperature (°C)') # temperatura CPU (°C) | CPU temperature (°C)
plt.plot(xdata, y02, 'r-', label='gathered temperature (°C)') # temperatura misurata (°C) | gathered temperature (°C)
plt.ylim((28,42))
plt.legend()
#plt.grid(True)

"""
# Pressione ed umidità' (sullo stesso grafico, con assi distinti)
ax1 = plt.figure(1).add_subplot(2, 3, 2)
plt.title('Pressione ed umidità')
color = 'tab:red'
serie1, = ax1.plot(xdata, y04, '.', markersize=0.5, color=color)
label1 = mlines.Line2D([], [], color=color, marker='.', markersize=10, label='Pressione (mbar)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim((1000,1002.5))
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:blue'
serie2, = ax2.plot(xdata, y03, '.', markersize=0.5, color=color)
label2 = mlines.Line2D([], [], color=color, marker='.', markersize=10, label='Umidità (%)')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim((30,45))
plt.legend(handles=[label1, label2], loc=2)
"""

# Pressione
plt.subplot(232)
plt.title('Pressure') # Pressione | Pressure
color = 'tab:red'
plt.plot(xdata,  y04, '.', markersize=0.5, color=color)
label1 = mlines.Line2D([], [], color=color, marker='.', markersize=10, label='gathered pressure (mbar)') # pressione misurata (mbar) | gathered pressure (mbar)
plt.ylim((1001,1003))
plt.legend(handles=[label1], loc=0)

# Umidità
plt.subplot(233)
plt.title('Humidity') # Umidità | Humidity
color = 'tab:blue'
plt.plot(xdata,  y03, '.', markersize=0.5, color=color)
label2 = mlines.Line2D([], [], color=color, marker='.', markersize=10, label='gathered humidity (%)') # umidità misurata (%) | gathered humidity (%)
plt.ylim((30,42))
plt.legend(handles=[label2], loc=0)

# Accelerometro
plt.subplot(234)
plt.title('Accelerometer') # Accelerometro | Accelerometer
plt.plot(xdata, y11, label='x (Gs)')
plt.plot(xdata, y12, label='y (Gs)')
plt.plot(xdata, y13, label='z (Gs)')
plt.legend(bbox_to_anchor=(1.0, 0.67), loc=1)


# Orientazione
plt.subplot(235)
plt.title('Gyroscope') # Giroscopio | Gyroscope
plt.plot(xdata, y05, label='pitch (°)') # beccheggio (°) | pitch (°)
plt.plot(xdata, y06, label='roll (°)')  # rollio (°)     | roll (°)
plt.plot(xdata, y07, label='yaw (°)')   # imbardata (°)  | yaw (°)
plt.ylim((0,260))
plt.legend(loc=1)


# Magnetometro
plt.subplot(236)
plt.title('Magnetometer') # Magnetometro | Magnetometer 
plt.plot(xdata, y08, label='x ($\mu$T)')
plt.plot(xdata, y09, label='y ($\mu$T)')
plt.plot(xdata, y10, label='z ($\mu$T)')
plt.legend(loc=1)


# Format the minor tick labels of the y-axis into empty strings with
# `NullFormatter`, to avoid cumbering the axis with too many labels.
plt.gca().yaxis.set_minor_formatter(NullFormatter())
# Adjust the subplot layout, because the logit one may take more space
# than usual, due to y-tick labels like "1 - 10^{-3}"
plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25, wspace=0.35)
plt.show()
