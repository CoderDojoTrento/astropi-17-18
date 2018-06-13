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

from scipy.optimize import curve_fit

def func(x, a, b, c):
    return a + b * np.exp(-1.0 * c * x)

def oscillazione(x, d, e, f):
    return d * np.sin(e * x + f)

# Vedi: https://www.celestrak.com/NORAD/elements/ per i dati aggiornati;
# per lo storico, calcola il timestamp della data d'interesse (dati raccolti il 27 aprile);
# $ date -d "37 days ago"
#ven 27 apr 2018 10.55.59
#$ date -d "37 days ago" +%s
#1524819410
# https://api.wheretheiss.at/v1/satellites/25544/tles?format=text&timestamp=1524348853
name = "ISS (ZARYA)";            
line1 = "1 25544U 98067A   18116.90063980  .00002062  00000-0  38334-4 0  9997"
line2 = "2 25544  51.6421 274.3807 0002753  23.4906  50.8634 15.54167550110549"

ISS = ephem.readtle(name, line1, line2)
sole = ephem.Sun()

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
Altezze = []
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
    #print("Analizzo posizione per il %d-mo dato..." % (progressivo), end='')
    ISS.compute(timestamp_dato)
    # altezza del Sole rispetto all'osservatore sotto la ISS
    osservatore = ephem.Observer()
    osservatore.elevation = 0 # sulla Terra, sotto la ISS
    osservatore.lat = ISS.sublat
    osservatore.long = ISS.sublong
    osservatore.date = timestamp_dato
    sole.compute(osservatore)
    angolo_sole = degrees(sole.alt)
    Altezze.append(angolo_sole)
    print("%d,%s,%.4f,%.4f,%s,%s,%s,%s" % (progressivo, timestamp_dato.strftime("%Y-%m-%d %H:%M:%S.%f"), xdata[-1], ydata[-1], xlabels[-1], degrees(ISS.sublat), degrees(ISS.sublong), angolo_sole))
  
ora_fine = time()
print(datetime.fromtimestamp(ora_inizio).strftime("=========================================== Fine analisi: %Y-%m-%d %H:%M:%S.%f"), end='')
print(" [durata secondi: ", ora_fine-ora_inizio, "]")

file_dati.close()

f, axarr = plt.subplots(2, sharex=False)
f.subplots_adjust(hspace=0.5)

axarr[0].set_title("Temperature oscillating trend analysis")  # Analisi della parte oscillante | Temperature oscillating trend analysis
popt, pcov = curve_fit(func, xdata, ydata)
perr = np.sqrt(np.diag(pcov))
print('popt',popt)
print('perr',perr)
ydata2 = np.apply_along_axis(func, 0, xdata, popt[0], popt[1], popt[2])

ydata3 = ydata - ydata2
poptO, pcovO = curve_fit(oscillazione, xdata, ydata3, bounds=((0., 2.0, -np.inf), (1., 4.0, np.inf)))
perrO = np.sqrt(np.diag(pcovO))
print('popt',poptO)
print('perr',perrO)
ydata4 = np.apply_along_axis(oscillazione, 0, xdata, poptO[0], poptO[1], poptO[2])

# best fit con | best fit with
axarr[0].plot(xdata, ydata3, 'g+', label='difference between experimental data and best exponential fit for the cooling curve') # differenza tra dati sperimentali e best fit per la curva esponenziale di raffreddamento | difference between experimental data and best exponential fit for the cooling curve
axarr[0].plot(xdata, ydata4, 'r-', label='best fit with $f(x) = d \cdot sin(e \cdot x + f)$ $\Longrightarrow$ d=%5.3f, e=%5.3f, f=%5.3f' % tuple(poptO), linewidth=4.0)
axarr[0].legend()
axarr[0].set_ylabel('Temperature (°C)') # Temperatura (°C) | Temperature (°C)
axarr[0].set_xlabel("Time (fractions of hours from the beginning of the experiment)") # Tempo (ore a partire dall'inizio dell'esperimento) | Time (fractions of hours from the beginning of the experiment)
axarr[0].set_ylabel("$\Delta$ Temperature (°C)") # $\Delta$ Temperatura (°C) | $\Delta$ Temperature (°C)

ydata5 = np.apply_along_axis(oscillazione, 0, xdata, poptO[0], poptO[1], poptO[2])
# Best fit sinusoidale e altezza Sole (sullo stesso grafico, con assi distinti)
axarr[1].set_title('Comparison between superheating cycle and exposure to the Sun') # Confronto tra ciclo di surriscaldamento ed esposizione al Sole | Comparison between superheating cycle and exposure to the Sun
color = 'tab:red'
axarr[1].plot(xdata, ydata5, color=color)
axarr[1].set_ylim((-0.06,0.06))
label1 = mlines.Line2D([], [], color=color, label='best sinusoidal fit') # differenza tra dati sperimentali e best fit | difference between experimental data and best fit
axarr[1].tick_params(axis='y', labelcolor=color)
ax2 = axarr[1].twinx()  # instantiate a second axes that shares the same x-axis
axarr[1].set_ylabel("$\Delta$ Temperature (°C)", color=color) # $\Delta$ Temperatura (°C) | $\Delta$ Temperature (°C)
axarr[1].set_xlabel('Hours (GMT time)') # Tempo (ora GMT) | Hours (GMT time)
color = 'tab:blue'
# np.array(Altezze).clip(0)
ax2.plot(xdata, Altezze, color=color)
ax2.set_ylim((-90,90))
ax2.tick_params(axis='y', labelcolor=color)
label2 = mlines.Line2D([], [], color=color, label='Sun altitude above Earth local horizon') # Altezza del Sole sull'orizzonte locale terrestre | Sun altitude above Earth local horizon
ax2.set_ylabel("Sun altitude (°)", color=color) # Altezza del Sole (°) | Sun altitude (°)
ax2.set_yticks(np.arange(-60,61,30))
ombra = np.zeros(len(Altezze))
ombra[np.array(Altezze)<0] = True
ax2.fill_between(xdata, 0, 1, where=(ombra==True), color='grey', alpha=0.3, transform=ax2.get_xaxis_transform())
plt.xticks(xdata[::900], xlabels[::900])
label3 = Patch(color='grey', alpha=0.3, label='ISS eclipsed')
plt.legend(handles=[label1, label2, label3], loc=3)

plt.show()
