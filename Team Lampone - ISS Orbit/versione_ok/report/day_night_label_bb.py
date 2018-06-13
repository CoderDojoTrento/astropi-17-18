##################################################################################
#   ASTROPI 2018 - MISSION "SPACE LAB" (Life on Earth): GRUPPO LAMPONI (Italy)   #
##################################################################################
# Abstract: Legge i dati dai sensori della Sense Hat e scatta fotografie per
# poter determinare la velocitÃ  a cui si muove la ISS
#
# Gruppo Lamponi 2018 @ CoderDojo Trento, Italy:
# - Giulia Giaffreda
# - Nicola Bortolotti
# - Florian Giaffreda
# - Matteo Bridi
#
# Parametri utilizzati nel programma:
# NOME_FILE             #prefisso nome file CSV
#
#
###########################################################################


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

##### Parametri di configurazione #####
FOLDER_IMMAGINI = "3475_Team_Lampone" # "enviro-pi" # "file_esempio"
NOME_FILE_LISTA = "Foto_.*"   # pattern nome file delle immagini per listato folder
NOME_FILE_ASPETTO = "Foto_%Y-%m-%d_%H-%M-%S.%f.jpg"   # pattern nome file delle immagini per parsing timestamp

# Vedi: https://www.celestrak.com/NORAD/elements/ per i dati aggiornati;
# per lo storico, calcola il timestamp della data d'interesse;
# pi@rpimbra0:~ $ date -d "38 days ago"
# Sun 22 Apr 00:11:02 CEST 2018
# pi@rpimbra0:~ $ date -d "38 days ago" +%s
# 1524348853
# https://api.wheretheiss.at/v1/satellites/25544/tles?format=text&timestamp=1524348853
name = "ISS (ZARYA)";            
line1 = "1 25544U 98067A   18112.02627541  .00002222  00000-0  40779-4 0  9999"
line2 = "2 25544  51.6417 298.6811 0002464   7.3195 137.0833 15.54139945109788"

ISS = ephem.readtle(name, line1, line2)

#==========================================================================

#### Funzioni #####

##----------ottiene la lista dei files di immagini---------
def prendi_lista_immagini(folder):
    aspetto_file = re.compile(NOME_FILE_LISTA)
    return [fn for fn in os.listdir(folder)
              if aspetto_file.match(fn)]

#=============================================================================

##### Programma principale #####        
lista_imgs = prendi_lista_immagini(FOLDER_IMMAGINI)

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
date = datetime.strptime("2018-04-22_09-00", "%Y-%m-%d_%H-%M") #datetime.utcnow()
CS=map.nightshade(date)

sole = ephem.Sun()

progressivo = 0
Longs = []
Lats = []
for file_immagine in lista_imgs[:]:
    ora_inizio = time()
    print(datetime.fromtimestamp(ora_inizio).strftime("================================================================================ Inizio analisi: %Y-%m-%d %H:%M:%S.%f"))
    timestamp_img = datetime.strptime(file_immagine, NOME_FILE_ASPETTO)
    print("Analizzo posizione per %s..." % (file_immagine))
    timestamp_img += timedelta(seconds=3) # aggiustamento del tempo, per centrare meglio le immagini: clock sbagliato o TLE non accurate?
    ISS.compute(timestamp_img)
    Longs.append(degrees(ISS.sublong))
    Lats.append(degrees(ISS.sublat))
    # altezza del Sole rispetto all'osservatore sotto la ISS
    osservatore = ephem.Observer()
    osservatore.elevation = 0 # sulla Terra, sotto la ISS
    osservatore.lat = ISS.sublat
    osservatore.long = ISS.sublong
    osservatore.date = timestamp_img
    sole.compute(osservatore)
    angolo_sole = degrees(sole.alt)
    print("sublat=%s   sublong=%s   altezza_sole=%s" % (degrees(ISS.sublat), degrees(ISS.sublong), angolo_sole))
    progressivo += 1
    
    ## diametro vista oblo':400 Km 
    (x,y)=map(degrees(ISS.sublong),degrees(ISS.sublat))
    circle = Circle(xy=(x,y),radius=400000/2, fill=False, color='b' if (angolo_sole<0) else 'r')
    if ( (progressivo % 20) == 0 ):
        plt.gca().annotate(file_immagine[16:21],(x,y-200000),(x,y-220000), ha="center", va="center",
                size=6,
                arrowprops=dict(arrowstyle='->',
                                patchB=circle,
                                shrinkA=5,
                                shrinkB=5,
                                fc="k", ec="k",
                                connectionstyle="arc3,rad=-0.05",
                                ),
                bbox=dict(boxstyle="square", fc="w"))
    plt.gca().add_patch(circle)
    
    ora_fine = time()
    print(datetime.fromtimestamp(ora_fine).strftime("================================================================================ Fine analisi: %Y-%m-%d %H:%M:%S.%f"), end='')
    print(" [durata secondi: ", ora_fine-ora_inizio, "]")

plt.title('Mappa giorno/notte per %s (UTC)' % date.strftime("%d %b %Y %H:%M:%S"))
plt.show()
