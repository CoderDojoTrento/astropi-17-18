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

##### Import - Moduli ####
from opencv_stitcher import MyStitcher

##### Import - Librerie ####
from time import sleep
from datetime import datetime
import sys
import re
import os
import imutils
import cv2
import numpy as np
from matplotlib import pyplot as plt

#==========================================================================

##### Parametri di configurazione #####
FOLDER_IMMAGINI = "file_esempio"
NOME_FILE_LISTA = "EnviroPi_.*"   # pattern nome file delle immagini per listato folder
NOME_FILE_ASPETTO = "EnviroPi_%Y%m%d_%H%M%S.jpg"   # pattern nome file delle immagini per parsing timestamp
SALVA_IMMAGINI_INCOLLATE = False
SALVA_IMMAGINI_PUNTI_CHIAVE = False
INTERATTIVO = False # mostrare o meno i plot interattivi
# parametri PiCamera
focale=3.60  # lunghezza focale (mm)  (v1: 3.60;  v2: 3.04)
sensx=3.76   # dimensione sensore asse x (mm) (v1: 3.76;  v2:3.68)
resx=640     # risoluzione img x (v1: 2592 x 1944 pixels; v2: 3280 x 2464 pixels)
# per fare delle prove veloci, conviene ridurre le immagini: serve tenere traccia del
# fattore di scala e dell'orientazione originale per sapere su quale dimensione scalare
DIMENSIONE_RIDOTTA = 800 # misura massima in pixel (per ridurre il tempo di elaborazione)
fattore_di_scala = 1.0 # se si riduce l'immagine, bisogna correggere il calcolo delle distanze
orientazione = "LANDSCAPE" # "LANDSCAPE" oppure "PORTRAIT"

#==========================================================================

#### Funzioni #####

##----------ottiene la lista dei files di immagini---------
def prendi_lista_immagini(folder):
    aspetto_file = re.compile(NOME_FILE_LISTA)
    return [fn for fn in os.listdir(folder)
              if aspetto_file.match(fn)]

def calcola_fattore_di_riduzione(immagine_campione):
    scala = 1.0
    orientaz = "LANDSCAPE"
    imageAaltezzaPx, imageAlarghezzaPx = immagine_campione.shape[:2]
    if ((imageAlarghezzaPx > DIMENSIONE_RIDOTTA) or (imageAaltezzaPx > DIMENSIONE_RIDOTTA)):
        if (imageAlarghezzaPx > imageAaltezzaPx):
            orientaz = "LANDSCAPE"
            scala = imageAlarghezzaPx / DIMENSIONE_RIDOTTA
        else:
            orientaz = "PORTRAIT"
            scala = imageAaltezzaPx / DIMENSIONE_RIDOTTA
    print(imageAlarghezzaPx, imageAaltezzaPx)
    return scala, orientaz

def riduci_immagine(immagine):
    if (fattore_di_scala > 1.0):
        if (orientazione == "LANDSCAPE"):
            immagine = imutils.resize(immagine, width=DIMENSIONE_RIDOTTA)
        else:
            immagine = imutils.resize(immagine, height=DIMENSIONE_RIDOTTA)
    return immagine


#=============================================================================

##### Programma principale #####        

lista_imgs = prendi_lista_immagini(FOLDER_IMMAGINI)

immagine_1 = lista_imgs[0]
timestamp_1 = datetime.strptime(immagine_1,NOME_FILE_ASPETTO)
imageA = cv2.imread(os.path.join(FOLDER_IMMAGINI, immagine_1))
fattore_di_scala, orientazione = calcola_fattore_di_riduzione(imageA)
print("fattore_di_scala", fattore_di_scala)
print("orientazione", orientazione)
imageA = riduci_immagine(imageA)
for file_immagine in lista_imgs[1:-1]:
    immagine_2 = file_immagine
    timestamp_2 = datetime.strptime(immagine_2,NOME_FILE_ASPETTO)
    delta_t = timestamp_2 - timestamp_1
    delta_t_sec = delta_t.seconds + delta_t.microseconds / 1000000
    print("Confronto %s e %s (Dt = %f s)..." % (immagine_1, immagine_2, delta_t_sec))
    imageB = cv2.imread(os.path.join(FOLDER_IMMAGINI, immagine_2))
    imageB = riduci_immagine(imageB)

    # stitch the images together to create a panorama
    stitcher = MyStitcher()
    if SALVA_IMMAGINI_PUNTI_CHIAVE:
        (result, vis) = stitcher.stitch([imageA, imageB], showMatches=True)
    else:
        result = stitcher.stitch([imageA, imageB], showMatches=False)

    if SALVA_IMMAGINI_PUNTI_CHIAVE:
        cv2.imwrite(os.path.splitext(immagine_2)[0] + "_keypoints.jpg", vis)
    if SALVA_IMMAGINI_INCOLLATE:
        cv2.imwrite(os.path.splitext(immagine_2)[0] + "_stitch.jpg", result)

    M = stitcher.getHomography()
    print("Trasformazione che assicura la sovrapposizione:")
    print(M)

    print("Distanza espressa in pixel:")
    sx=M[0][2]
    sy=M[1][2]
    distanza_px=np.sqrt(sx**2 + sy**2)
    print(distanza_px)
    
    print("Distanza espressa in metri:")
    altezzaiss = 408*1000 #altezza ISS (m) TODO: da calcolare con PyEphem
#    distanza = (1/focale*(distanza_px*(sensx/resx/1000))*altezzaiss)/1000
    distanza = (sensx*altezzaiss/focale)*(distanza_px/resx)*fattore_di_scala
    print(distanza)
    
    # stima velocità: teo, circa 27563 Km/h
    v_iss = distanza / delta_t_sec
    print("Stima velocità: %.3f m/s (ovvero %.3f Km/h)" % (v_iss, v_iss*3.6))
    
    if INTERATTIVO:
        plt.subplot2grid((2,2),(0,0)),plt.imshow(imageA,'gray'),plt.title('foto 1')
        plt.subplot2grid((2,2),(0,1)),plt.imshow(imageB,'gray'),plt.title('foto 2')
        if SALVA_IMMAGINI_PUNTI_CHIAVE:
            plt.subplot2grid((2,2),(1,0)),plt.imshow(vis,'gray'),plt.title('Keypoint Matches')
            plt.subplot2grid((2,2),(1,1)),plt.imshow(result,'gray'),plt.title('stitch')
        else:
            plt.subplot2grid((2,2),(1,0),colspan=2),plt.imshow(result,'gray'),plt.title('stitch')
        plt.show()
        
    imageA = imageB
    immagine_1 = immagine_2
    timestamp_1 = timestamp_2
