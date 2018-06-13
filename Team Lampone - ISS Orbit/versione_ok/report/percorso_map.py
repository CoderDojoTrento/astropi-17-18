##################################################################################
#   ASTROPI 2018 - MISSION "SPACE LAB" (Life on Earth): GRUPPO LAMPONI (Italy)   #
##################################################################################
# Abstract: Legge i dati dai sensori della Sense Hat e scatta fotografie per
# poter determinare la velocità a cui si muove la ISS
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
from datetime import datetime
import sys
import re
import os
import imutils
import cv2
import numpy as np
from matplotlib import pyplot as plt
import ephem
from math import degrees

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

tle_rec = ephem.readtle(name, line1, line2)

#==========================================================================

#### Funzioni #####

##----------ottiene la lista dei files di immagini---------
def prendi_lista_immagini(folder):
    aspetto_file = re.compile(NOME_FILE_LISTA)
    return [fn for fn in os.listdir(folder)
              if aspetto_file.match(fn)]

def coordinate_su_mappa(lat, long):
    return ( round((long+180.0)/360.0*1920.0), 960-round((lat+90.0)/180.0*960.0))

#=============================================================================

##### Programma principale #####        
img = cv2.imread('percorso_earth-map.jpg')
lista_imgs = prendi_lista_immagini(FOLDER_IMMAGINI)
#print(img.shape) # (960, 1920, 3)

for file_immagine in lista_imgs[:]:
    ora_inizio = time()
    print(datetime.fromtimestamp(ora_inizio).strftime("================================================================================ Inizio analisi: %Y-%m-%d %H:%M:%S.%f"))
    timestamp_img = datetime.strptime(file_immagine, NOME_FILE_ASPETTO)
    print("Analizzo posizione per %s..." % (file_immagine))
    tle_rec.compute(timestamp_img)
    print("sublat=%s   sublong=%s" % (degrees(tle_rec.sublat), degrees(tle_rec.sublong)))
    print("sublat=%s   sublong=%s" % (coordinate_su_mappa(degrees(tle_rec.sublat), degrees(tle_rec.sublong))))
    img = cv2.circle(img, coordinate_su_mappa(degrees(tle_rec.sublat), degrees(tle_rec.sublong)), 10, (0,0,255), 1, cv2.LINE_AA)
    
    # diametro vista oblò: 330 Km

    ora_fine = time()
    print(datetime.fromtimestamp(ora_fine).strftime("================================================================================ Fine analisi: %Y-%m-%d %H:%M:%S.%f"), end='')
    print(" [durata secondi: ", ora_fine-ora_inizio, "]")

cv2.imshow('Draw01', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
