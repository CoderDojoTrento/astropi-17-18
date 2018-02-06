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
# FREQ_LETTURA_DATI     #frequenza raccolta dati
# FREQ_SCRITTURA_DATI   #frequenza scrittura su file (in numero di righe)
# FREQ_FOTO             #frequenza foto in secondi
# DURATA_WARMUP_CAMERA  #durata della preview per mettere a fuoco la camera)
# camera.resolution     #Risoluzione foto (v1 max 2592 × 1944) (v2 max 3280 × 2464)
#
# N.B. No need to insert updated TLE entries: all processing will be made off-line;
# all we need is enough disk-space to save data (2 Gigs extimated for a 3 hours run)
# and a well-synced system time (in order to reconstruct location and altitude of
# the ISS given the photograph timestamp).
#
###########################################################################


#==========================================================================

##### Import - Moduli ####
import intro_video

##### Import - Librerie ####
from sense_hat import SenseHat
from picamera import PiCamera
from time import sleep
from threading import Thread
from datetime import datetime
import sys

#==========================================================================

##### Parametri di configurazione #####
NOME_FILE = "LamponeSenseLog"   # prefisso nome file CSV
FREQ_LETTURA_DATI= 1            # frequenza raccolta dati
FREQ_SCRITTURA_DATI = 20        # frequenza scrittura su file (in numero di righe)
FREQ_FOTO = 12                  # frequenza foto in secondi (deve essere maggiore di DURATA_WARMUP_CAMERA)
DURATA_WARMUP_CAMERA = 4        # durata della preview per mettere a fuoco la camera)

# costanti per i colori
w=( 255, 255, 255) # bianco
b=(   0,   0,   0) # nero
r=( 255,   0,   0) # rosso
g=(   0, 153,   0) # verde

# array con il disegno del grafico utilizzato nella set_pixels
immagine_graf = [
    w,b,b,b,b,b,b,b,
    w,r,b,b,b,b,g,b,
    w,r,b,r,b,b,g,b,
    w,r,g,r,b,b,g,b,
    w,r,g,r,g,r,g,r,
    w,r,g,r,g,r,g,r,
    w,r,g,r,g,r,g,r,
    w,w,w,w,w,w,w,w
    ]

# array con il disegno della macchina fotografica utilizzato nella set_pixels
immagine_foto = [
    b,b,b,b,b,b,b,b,
    b,b,b,b,b,b,b,b,
    b,b,b,w,w,b,b,b,
    b,w,w,w,w,w,w,b,
    b,w,w,b,b,w,w,b,
    b,w,w,b,b,w,w,b,
    b,w,w,w,w,w,w,b,
    b,b,b,b,b,b,b,b
    ]

#==========================================================================

#### Funzioni #####

##----------crea il file CSV con la riga di intestazione---------

def preparazione_file(nome_file):
    # crea una lista per l'intestazione
    intestazione = []
    intestazione.append("ora")
    intestazione.append("temperatura_u")
    intestazione.append("temperatura_p")
    intestazione.append("umidità")
    intestazione.append("pressione")
    intestazione.extend(["beccheggio","rollio","imbardata"])
    intestazione.extend(["mag_x","mag_y","mag_z"])
    intestazione.extend(["accel_x","accel_y","accel_z"])
    intestazione.extend(["giro_x","giro_y","giro_z"])
    # crea un nuovo file e vi inserisce la riga di intestazione
    with open(nome_file,"w", newline='') as f:
        f.write(",".join(str(colonna) for colonna in intestazione)+ "\n")


## ------------- legge i sensori ------------------ 

def leggi_dati_sensore():
    #definisce una lista vuota dove mettere i dati
    riga_di_dati=[]
    
    # il primo elemento è l'ora attuale
    riga_di_dati.append(datetime.now())
    
    # inserisce nella lista i dati letti dai sensori
    riga_di_dati.append(sense.get_temperature_from_humidity())
    riga_di_dati.append(sense.get_temperature_from_pressure())
    riga_di_dati.append(sense.get_humidity())
    riga_di_dati.append(sense.get_pressure())

    orientazione = sense.get_orientation()
    beccheggio = orientazione["pitch"]
    rollio = orientazione["roll"]
    imbardata = orientazione["yaw"]
    riga_di_dati.extend([beccheggio, rollio, imbardata])

    mag = sense.get_compass_raw()
    mag_x = mag["x"]
    mag_y = mag["y"]
    mag_z = mag["z"]
    riga_di_dati.extend([mag_x, mag_y, mag_z])

    acc = sense.get_accelerometer_raw()
    acc_x = acc["x"]
    acc_y = acc["y"]
    acc_z = acc["z"]
    riga_di_dati.extend([acc_x, acc_y, acc_z])
    
    giro = sense.get_gyroscope_raw()
    giro_x = giro["x"]
    giro_y = giro["y"]
    giro_z = giro["z"]
    riga_di_dati.extend([giro_x, giro_y, giro_z])

    #trasforma la lista in stringa 
    stringa_dati_raccolti = ",".join(str(elemento) for elemento in riga_di_dati)
    
    return stringa_dati_raccolti   

##--------sezione che si occupa di raccogliere i dati dal Sense HAT--------

class leggisensori:
    
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        #richiama la funzione che crea il file con la riga di intestazione
        serie_di_dati = []
        preparazione_file(nome_file_completo)
        while self._running:
            try:
                # legge i dati
                dati_raccolti = leggi_dati_sensore()            
                print("lettura dati sensori")
                sense.set_pixels(immagine_graf)
                #inserisce i dati raccolti nella lista serie_di_dati (buffer x scrittura nel file)
                serie_di_dati.append(dati_raccolti)
            except:
                print("Eccezione raccolta misure: ", (sys.exc_info()[0], sys.exc_info()[1]))

            # se la dimensione del buffer supera la frequenza di scrittura
            if len(serie_di_dati) >= FREQ_SCRITTURA_DATI:
                print("scrittura file..")
                try:
                    # Aggiunge le righe nel buffer al file
                    with open(nome_file_completo,"a") as f:
                        for riga_di_dati in serie_di_dati:
                            f.write(riga_di_dati + "\n")
                    # dopo aver travasato tutto su file, cancella il buffer
                    serie_di_dati = []
                except:
                    print("Eccezione scrittura file: ", (sys.exc_info()[0], sys.exc_info()[1]))
            # attesa prima della prossima misura
            sleep(FREQ_LETTURA_DATI)


##--------sezione che si occupa di scattare le foto--------
## Tiene conto del tempo di attesa tra una foto e l'altra (FREQ_FOTO) ma anche
## del tempo necessario per il warm-up e la messa a fuoco (DURATA_WARMUP_CAMERA)
            
class scattafoto:

    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        while self._running:
            try:
                camera.start_preview(alpha=200)
                sleep(DURATA_WARMUP_CAMERA)
                camera.capture('Foto_%s.jpg' % datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))
                camera.stop_preview()
                print("scatto foto")
                sense.set_pixels(immagine_foto)
            except:
                print("Eccezione scatta foto: ", (sys.exc_info()[0], sys.exc_info()[1]))
            sleep(FREQ_FOTO - DURATA_WARMUP_CAMERA)
            


##--------polling continuo dei dati di orientamento--------
## richiesto dalla presenza del filtro di Kalman

class polling_orientation:  
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        while self._running:
            sense.get_orientation()
            #print "polling"
            
#=============================================================================

##### Programma principale #####        

camera = PiCamera()
camera.resolution = (2592,1944) #Risoluzione foto (v1 max 2592×1944) (v2 max 3280×2464)

sense = SenseHat()
        
serie_di_dati= []   # buffer utilizzato per raccogliere i dati da scrivere su file
nome_file_completo = NOME_FILE+"_"+str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))+".csv"

#----------------- video introduttivo -------------------------------------

print("Animazione introduttiva")
intro_video.intro_video() #animazione introduttiva

#-----------------lettura dati sensori-------------------------------------

#lancio thread per polling continuo sensore orientamento
#Thread(target= polling_orientation()).start()
print("Attendo 2 secondi e faccio partire il thread 'polling_orientation'")
sleep(2)
#Crea la classe, quindi il thread e lo fa partire
PollingOrientation = polling_orientation()
PollingOrientationThread = Thread(target=PollingOrientation.run) 
PollingOrientationThread.start()

#lancio thread per lettura sensori
print("Attendo 2 secondi e faccio partire il thread 'leggisensori'")
sleep(2)
#Crea la classe, quindi il thread e lo fa partire
LeggiSensori = leggisensori()
LeggiSensoriThread = Thread(target=LeggiSensori.run) 
LeggiSensoriThread.start()

#lancio thread per foto
print("Attendo 2 secondi e faccio partire il thread 'scattafoto'")
sleep(2)
#Crea la classe, quindi il thread e lo fa partire
ScattaFoto = scattafoto()
ScattaFotoThread = Thread(target=ScattaFoto.run) 
ScattaFotoThread.start()

try:
    while True:
        dummy = 1
        sleep(1) # TODO: verifica se serve

# se premo CTRL+C esce dal programma, svuota il buffer e termina i thread
except KeyboardInterrupt:
    print('Esecuzione interrotta!')

    # termina i thread
    PollingOrientation.terminate()
    LeggiSensori.terminate()
    ScattaFoto.terminate()
    
    # Aggiunge al file le righe ancora presenti nel buffer
    print("scrittura file..")
    with open(nome_file_completo,"a") as f:
        for riga_di_dati in serie_di_dati:
            f.write(riga_di_dati + "\n")

    # cancella il buffer
    serie_di_dati = []
    
    # messaggio conclusivo
    sense.show_message("Bye bye!", text_colour=[255, 0, 0])
    