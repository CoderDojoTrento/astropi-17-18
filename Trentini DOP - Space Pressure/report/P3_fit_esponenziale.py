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
from matplotlib.patches import Circle

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
ydata = []
xlabels = []
for riga_dati in file_dati:
    progressivo += 1
    # salto la riga di intestazione
    if ((progressivo == 0)): # or (progressivo > 500)):
        continue
    dati = riga_dati.split(",")
    timestamp_dato = datetime.strptime(dati[0], "%Y-%m-%d %H:%M:%S.%f")
    td = timestamp_dato - time_ref
    xdata.append(td.total_seconds()/3600.0)
    ydata.append(float(dati[2]))
    xlabels.append(timestamp_dato.strftime("%H:%M"))
    print("%d,%s,%.4f,%.4f,%s" % (progressivo, timestamp_dato.strftime("%Y-%m-%d %H:%M:%S.%f"), xdata[-1], ydata[-1], xlabels[-1]))
  
ora_fine = time()
print(datetime.fromtimestamp(ora_inizio).strftime("=========================================== Fine analisi: %Y-%m-%d %H:%M:%S.%f"), end='')
print(" [durata secondi: ", ora_fine-ora_inizio, "]")

file_dati.close()

f, axarr = plt.subplots(2, sharex=False)
f.subplots_adjust(hspace=0.3)

axarr[0].set_title("Temperature trend analysis")  # Analisi dell'andamento della temperatura | Temperature trend analysis
axarr[0].plot(xdata, ydata, 'b-', label='gathered temperature') # temperatura misurata | gathered temperature
popt, pcov = curve_fit(func, xdata, ydata)
perr = np.sqrt(np.diag(pcov))
print('popt',popt)
print('perr',perr)
ydata2 = np.apply_along_axis(func, 0, xdata, popt[0], popt[1], popt[2])

# best fit con | best fit with
axarr[0].plot(xdata, ydata2, 'r-', label='best fit with $f(x) = a + b \cdot e^{- c \cdot x}$ $\Longrightarrow$ a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
axarr[0].legend()
axarr[0].set_ylabel('Temperature (°C)') # Temperatura (°C) | Temperature (°C)
axarr[0].set_xlabel("Time (fractions of hours from the beginning of the experiment)") # Tempo (ore a partire dall'inizio dell'esperimento) | Time (fractions of hours from the beginning of the experiment)

axarr[1].plot(xdata, ydata - ydata2, 'g+', label='difference between experimental data and best fit') # differenza tra dati sperimentali e best fit | difference between experimental data and best fit
axarr[1].legend()
axarr[1].set_ylabel("$\Delta$ Temperature (°C)") # $\Delta$ Temperatura (°C) | $\Delta$ Temperature (°C)
axarr[1].set_xlabel('Hours (GMT time)') # Tempo (ora GMT) | Hours (GMT time)
plt.xticks(xdata[::900], xlabels[::900])

plt.show()
