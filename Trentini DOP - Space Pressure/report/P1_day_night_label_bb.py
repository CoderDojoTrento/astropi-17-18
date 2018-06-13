##################################################################################
#   ASTROPI 2018 - MISSION "SPACE LAB" (Life inSpace): GRUPPO TRENTINI DOP (Italy)   #
##################################################################################

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

#==========================================================================

# Formato del file CSV:
#ora,temperatura_CPU,temperatura,umidita',pressione,beccheggio,rollio,imbardata,mag_x,mag_y,mag_z,accel_x,accel_y,accel_z,giro_x,giro_y,giro_z
#2018-04-27 08:36:58.948717,36.3,32.026214599609375,33.42070007324219,1001.752685546875,12.662729320228529,15.489296386532525,32.580562416472766,27.436603546142578,-11.285003662109375,58.11085510253906,-0.0024683563970029354,0.0019423406338319182,0.01803356595337391,0.17663809657096863,0.14376232028007507,0.06413397938013077


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

#=============================================================================

##### Programma principale #####        
file_dati = open("TDOP_2018-04-27_08.36.57.csv", "r")

# miller projection
map = Basemap(projection='mill', lon_0=0, resolution='l')
# plot coastlines, draw label meridians and parallels.
map.drawcoastlines()
map.drawparallels(np.arange(-90,90,15),labels=[1,0,0,0])
map.drawmeridians(np.arange(map.lonmin,map.lonmax+30,30),labels=[0,0,0,1])
# fill continents 'coral' (with zorder=0), color wet areas 'aqua'
map.drawmapboundary(fill_color='aqua')
map.fillcontinents(color='coral',lake_color='aqua')
map.drawcountries()
# shade the night areas, with alpha transparency so the
# map shows through. Use current time in UTC.
date = datetime.strptime("2018-04-27_10-00", "%Y-%m-%d_%H-%M") #datetime.utcnow()
CS=map.nightshade(date)
cmap = plt.get_cmap('hot')

sole = ephem.Sun()

ora_inizio = time()
print(datetime.fromtimestamp(ora_inizio).strftime("=========================================== Inizio analisi: %Y-%m-%d %H:%M:%S.%f"))
progressivo = -1
Longs = []
Lats = []
Altezze = []
for riga_dati in file_dati:
    progressivo += 1
    # salto la riga di intestazione
    if ((progressivo == 0)): #or(progressivo > 500)):
        continue
    dati = riga_dati.split(",")
    timestamp_dato = datetime.strptime(dati[0], "%Y-%m-%d %H:%M:%S.%f")
    #print("Analizzo posizione per il %d-mo dato..." % (progressivo), end='')
    ISS.compute(timestamp_dato)
    Longs.append(degrees(ISS.sublong))
    Lats.append(degrees(ISS.sublat))
    # altezza del Sole rispetto all'osservatore sotto la ISS
    osservatore = ephem.Observer()
    osservatore.elevation = 0 # sulla Terra, sotto la ISS
    osservatore.lat = ISS.sublat
    osservatore.long = ISS.sublong
    osservatore.date = timestamp_dato
    sole.compute(osservatore)
    angolo_sole = degrees(sole.alt)
    Altezze.append(angolo_sole)
    print("%d,%s,%s,%s,%s" % (progressivo, timestamp_dato.strftime("%Y-%m-%d %H:%M:%S.%f"), degrees(ISS.sublat), degrees(ISS.sublong), angolo_sole))
    
    if ( (progressivo % 10) == 0 ):
        (x,y)=map(degrees(ISS.sublong),degrees(ISS.sublat))
        etichetta = timestamp_dato.strftime("%H:%M")
        map.plot(x, y, 'o', color='black' if (angolo_sole<0) else cmap(angolo_sole/70.0), markersize=10, label = etichetta if ((progressivo % 400) == 0 ) else "")
        if ( (progressivo % 400) == 0 ):
            etichetta = timestamp_dato.strftime("%H:%M")
            plt.gca().annotate(etichetta,(x,y-200000),(x,y-220000), ha="center", va="center",
                    size=6,
                    bbox=dict(boxstyle="square", fc="w"))
    
ora_fine = time()
print(datetime.fromtimestamp(ora_inizio).strftime("=========================================== Fine analisi: %Y-%m-%d %H:%M:%S.%f"), end='')
print(" [durata secondi: ", ora_fine-ora_inizio, "]")

# add colorbar
#fig, ax = plt.subplots()
#heatmap = ax.pcolor(Altezze, cmap='hot')                  
#plt.colorbar(mappable=heatmap)
#cbar = plt.colorbar(cmap, location='bottom', vmin=0.5, vmax=0.99, ax=plt.gca())
#cbar.set_label('° altezza Sole')
##img = ax.imshow(image_file)
##plt.colorbar(img, ax=ax)

#plt.title('Mappa giorno/notte per %s (UTC)' % date.strftime("%d %b %Y %H:%M:%S"))
plt.title('Day and night map for %s (UTC)' % date.strftime("%d %b %Y %H:%M:%S"))
plt.show()
file_dati.close()