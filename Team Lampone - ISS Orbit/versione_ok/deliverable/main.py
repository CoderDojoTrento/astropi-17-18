##################################################################################
#   ASTROPI 2018 - MISSION "SPACE LAB" (Life on Earth): GRUPPO LAMPONI (Italy)   #
##################################################################################
# Abstract IT: Legge i dati dai sensori della Sense Hat e scatta fotografie per
#              poter determinare la velocità a cui si muove la ISS
# Abstract EN: Sense HAT sensor data are read and picture are taken with the camera
#              in order to evaluate the ISS speed 
#
# Gruppo Lamponi 2018 @ CoderDojo Trento, Italy:
# - Giulia Giaffreda
# - Nicola Bortolotti
# - Florian Giaffreda
# - Matteo Bridi
#
# IT: Parametri utilizzati nel programma:
# NOME_FILE             #prefisso nome file CSV
# FREQ_LETTURA_DATI     #frequenza raccolta dati (in sec)
# FREQ_SCRITTURA_DATI   #frequenza scrittura su file (in numero di righe)
# FREQ_FOTO             #frequenza foto in secondi
# DURATA_WARMUP_CAMERA  #durata della preview (per mettere a fuoco la camera e bilanciare la luminosità)
# camera.resolution     #risoluzione foto (v1 max 2592 × 1944) (v2 max 3280 × 2464)
#
# EN: Config parameters used in the code:
# NOME_FILE             #CSV file name prefix
# FREQ_LETTURA_DATI     #data collection frequency (in sec)
# FREQ_SCRITTURA_DATI   #writing to file frequency (in number of lines)
# FREQ_FOTO             #picture take frequency (in sec)
# DURATA_WARMUP_CAMERA  #camera preview span (in order to per focus the image and balance the brightness)
# camera.resolution     #picture resolution (v1 max 2592 × 1944) (v2 max 3280 × 2464)
#
# N.B. IT: Non è necessario trascrivere nel codice le righe TLE della ISS: tutto il processamento è
# fatto dopo il volo; tutto quello di cui ha bisogno il programma è sufficiente spazio disco per salvare
# i dati (meno di 3 GigaBytes stimati per un run di 3 ore) ed un ora di sistema ben regolata (per ricostruire
# posizione ed altezza della ISS a partire dal timestamp delle fotografie).

# N.B. EN: No need to insert updated TLE entries: all processing will be made off-line after the flight;
# all we need is enough disk-space to save data (less than 3 GigaBytes extimated for a 3 hours run)
# and a well-synced system time (in order to reconstruct location and altitude of
# the ISS given the photograph timestamp).
#
###########################################################################


#==========================================================================

##### Import - Moduli / Modules import ####
import intro_video

##### Import - Librerie / Library import ####
from sense_hat import SenseHat
from picamera import PiCamera
from time import sleep
from threading import Thread
from datetime import datetime
import sys

#==========================================================================

##### Parametri di configurazione / Config parameters #####
NOME_FILE = "LamponeSenseLog"   # prefisso nome file CSV / CSV file name prefix
FREQ_LETTURA_DATI= 1            # frequenza raccolta dati / data collection frequency (in sec)
FREQ_SCRITTURA_DATI = 20        # frequenza scrittura su file (in numero di righe) / writing to file frequency (in number of lines)
FREQ_FOTO = 12                  # frequenza foto in secondi (deve essere maggiore di DURATA_WARMUP_CAMERA) / picture take frequency (has to be greater of DURATA_WARMUP_CAMERA)
DURATA_WARMUP_CAMERA = 4        # durata della preview (per mettere a fuoco la camera e bilanciare la luminosità) / camera preview span (in order to per focus the image and balance the brightness)

# costanti per i colori / constants used for colors
w=( 255, 255, 255) # bianco / white
b=(   0,   0,   0) # nero   / black
r=( 255,   0,   0) # rosso  / red
g=(   0, 153,   0) # verde  / green

# IT: array con il disegno del grafico utilizzato nella set_pixels
# EN: color array representing a graph used as set_pixels() argument
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

# IT: array con il disegno della macchina fotografica utilizzato nella set_pixels
# EN: color array representing a camera used as set_pixels() argument
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

#### Funzioni / Functions #####

## IT ---------- crea il file CSV con la riga di intestazione ---------
## EN ---------- create the CSV file with the header line ---------

def preparazione_file(nome_file):
    # crea una lista per l'intestazione / create a list for the header
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
    # crea un nuovo file e vi inserisce la riga di intestazione / create a new file and insert the header
    with open(nome_file,"w", newline='') as f:
        f.write(",".join(str(colonna) for colonna in intestazione)+ "\n")


## IT ---------- legge i dati dei sensori ---------
## EN ---------- read the sensor data -------------

def leggi_dati_sensore():
    # definisce una lista vuota dove mettere i dati / define an empty list to store data
    riga_di_dati=[]
    
    # il primo elemento è l'ora attuale / first element is the timestamp
    riga_di_dati.append(datetime.now())
    
    # aggiunge alla lista i dati letti dai sensori / append read sensor data to the list
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

    # trasforma la lista in stringa / converts the list to a string
    stringa_dati_raccolti = ",".join(str(elemento) for elemento in riga_di_dati)
    
    return stringa_dati_raccolti   


## IT ---------- sezione che si occupa di raccogliere i dati dal Sense HAT ---------
## EN ---------- this section handles the Sense HAT data gathering -----------------

class leggisensori:
    
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        # IT: richiama la funzione che crea il file con la riga di intestazione
        # EN: call to the function that creates the files with the header
        serie_di_dati = []
        preparazione_file(nome_file_completo)
        while self._running:
            try:
                # legge i dati / read data
                dati_raccolti = leggi_dati_sensore()            
                print("lettura dati sensori")
                sense.set_pixels(immagine_graf)
                # IT: inserisce i dati raccolti nella lista serie_di_dati (buffer x scrittura nel file)
                # EN: gathered data are inserted in the list called serie_di_dati (it's a buffer for file writing)
                serie_di_dati.append(dati_raccolti)
            except:
                print("Eccezione raccolta misure: ", (sys.exc_info()[0], sys.exc_info()[1]))

            # IT: se la dimensione del buffer raggiunge il valore indicato per la frequenza di scrittura ...
            # EN: when the buffer dimension reaches the value specified for file writing ...
            if len(serie_di_dati) >= FREQ_SCRITTURA_DATI:
                print("scrittura file..")
                try:
                    # Aggiunge le righe nel buffer al file / add all the buffer rows to the file 
                    with open(nome_file_completo,"a") as f:
                        for riga_di_dati in serie_di_dati:
                            f.write(riga_di_dati + "\n")
                    # IT: dopo aver travasato tutto su file, cancella il buffer
                    # EN: after pouring off all in the file, erase the buffer
                    serie_di_dati = []
                except:
                    print("Eccezione scrittura file: ", (sys.exc_info()[0], sys.exc_info()[1]))
            # attesa prima della prossima misura / waiting before the next measure
            sleep(FREQ_LETTURA_DATI)


## IT ---------- sezione che si occupa di scattare le foto ---------
## Tiene conto del tempo di attesa tra una foto e l'altra (FREQ_FOTO) ma anche
## del tempo necessario per il warm-up e la messa a fuoco (DURATA_WARMUP_CAMERA)
## EN ---------- this section handles the picture taking -----------------
## The picture taking frequency (FREQ_FOTO) is taken into account, but also the
## time required for camera warm-up and focusing (DURATA_WARMUP_CAMERA)
            
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
            


## IT ---------- sezione che si occupa del polling continuo dei dati di orientamento ---------
## richiesto dalla presenza del filtro di Kalman
## IT ---------- this section handles the continuos polling of the orientation data ---------
## required by the presence of the Kalman filter

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

##### Programma principale / Main program #####        

camera = PiCamera()
camera.resolution = (2592,1944) # risoluzione foto / picture resolution (v1 max 2592×1944) (v2 max 3280×2464)

sense = SenseHat()
        
serie_di_dati= []   # buffer utilizzato per raccogliere i dati da scrivere su file / buffer used to collect data that has to be written in the file
nome_file_completo = NOME_FILE+"_"+str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))+".csv"

#----------------- video introduttivo / opening animation -------------------------------------

print("Animazione introduttiva")
intro_video.intro_video() # chiamata all'animazione introduttiva / opening animation call

#----------------- lettura dati sensori / sensors reading -------------------------------------

# IT: lancio thread per polling continuo sensore orientamento
# EN: start the thread for the continuos polling of the orientation data
print("Attendo 2 secondi e faccio partire il thread 'polling_orientation'")
sleep(2)
# Crea la classe, quindi il thread e lo fa partire / Create the class, then the thread and start it
PollingOrientation = polling_orientation()
PollingOrientationThread = Thread(target=PollingOrientation.run) 
PollingOrientationThread.start()

# IT: lancio thread per lettura sensori
# EN: start the thread for the sensor reading
print("Attendo 2 secondi e faccio partire il thread 'leggisensori'")
sleep(2)
# Crea la classe, quindi il thread e lo fa partire / Create the class, then the thread and start it
LeggiSensori = leggisensori()
LeggiSensoriThread = Thread(target=LeggiSensori.run) 
LeggiSensoriThread.start()

# IT: lancio thread per scattare le foto
# EN: start the thread for the picture taking
print("Attendo 2 secondi e faccio partire il thread 'scattafoto'")
sleep(2)
# Crea la classe, quindi il thread e lo fa partire / Create the class, then the thread and start it
ScattaFoto = scattafoto()
ScattaFotoThread = Thread(target=ScattaFoto.run) 
ScattaFotoThread.start()

try:
    while True:
        dummy = 1
        sleep(1) # TODO: verifica se serve

# IT: se premo CTRL+C esce dal programma, svuota il buffer e termina i thread
# EN: when we hit CTRL+C, it terminate the program, by emptying the buffer and stopping the threads
except KeyboardInterrupt:
    print('Esecuzione interrotta!')

    # termina i thread / terminate the threads
    PollingOrientation.terminate()
    LeggiSensori.terminate()
    ScattaFoto.terminate()
    
    # aggiunge al file le righe ancora presenti nel buffer / append to the file the rows left in the buffer
    print("scrittura file..")
    with open(nome_file_completo,"a") as f:
        for riga_di_dati in serie_di_dati:
            f.write(riga_di_dati + "\n")

    # cancella il buffer / clean the buffer
    serie_di_dati = []
    
    # messaggio conclusivo / final message
    sense.show_message("Bye bye!", text_colour=[255, 0, 0])
    