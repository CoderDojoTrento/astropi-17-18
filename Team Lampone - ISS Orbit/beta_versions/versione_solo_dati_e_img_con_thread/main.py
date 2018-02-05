############################################################################
#                PROGRAMMA  ASTROPI GRUPPO LAMPONI                         #
############################################################################
# Legge i dati dai sensori della Sense Hat e
# scatta fotografie per poter determinare la
# velocità a cui si muove la ISS
#
#
#
# FILENAME              #nome file CSV
# FREQ_LETTURA_DATI     #frequenza raccolta dati
# FREQ_SCRITTURA_DATI   #frequenza scrittura su file (in numero di righe)
# FREQ_FOTO             #frequqneza foto in secondi
# camera.resolution     #Risoluzione foto (v1 max 2592 × 1944) ( v2 max 3280 × 2464)
#
#
# Gruppo Lamponi:
# - Nome Cognome
# - Nome Cognome
# - Nome Cognome
# - Nome Cognome
#
# @ CoderDojo Trento 2018
###########################################################################


#==========================================================================

##### Moduli ####
import intro_video

#==========================================================================

##### Librerie ####
from sense_hat import SenseHat
from picamera import PiCamera
from time import sleep
from threading import Thread
from datetime import datetime

#==========================================================================

#### Funzioni #####

##----------crea il file CSV con la riga di intestazione---------

def file_setup(filename):
    # crea una lista per l'intestazione
    header =[]
    header.append("temp_h")
    header.append("temp_p")
    header.append("humidity")
    header.append("pressure")
    header.extend(["pitch","roll","yaw"])
    header.extend(["mag_x","mag_y","mag_z"])
    header.extend(["accel_x","accel_y","accel_z"])
    header.extend(["gyro_x","gyro_y","gyro_z"])
    header.append("timestamp")
    # crea un nuovo file e vi inserisce i dati contenuti dellalista della riga di intestazione
    with open(filename,"w", newline='') as f:
        f.write(",".join(str(value) for value in header)+ "\n")


## ------------- legge i sensori ------------------ 

def get_sense_data():
    #definisce una lista vuota dove mettere i dati
    sense_data=[]
    # inserisce nella lista i dati letti dai sensori
    sense_data.append(sense.get_temperature_from_humidity())
    sense_data.append(sense.get_temperature_from_pressure())
    sense_data.append(sense.get_humidity())
    sense_data.append(sense.get_pressure())

    o = sense.get_orientation()
    yaw = o["yaw"]
    pitch = o["pitch"]
    roll = o["roll"]
    sense_data.extend([pitch,roll,yaw])

    mag = sense.get_compass_raw()
    mag_x = mag["x"]
    mag_y = mag["y"]
    mag_z = mag["z"]
    sense_data.extend([mag_x,mag_y,mag_z])
    
    acc = sense.get_accelerometer_raw()
    x = acc["x"]
    y = acc["y"]
    z = acc["z"]
    sense_data.extend([x,y,z])
    
    gyro = sense.get_gyroscope_raw()
    gyro_x = gyro["x"]
    gyro_y = gyro["y"]
    gyro_z = gyro["z"]
    sense_data.extend([gyro_x,gyro_y,gyro_z])

    sense_data.append(datetime.now())

    #trasforma la lista in stringa 
    output_string = ",".join(str(value) for value in sense_data)
    
    return output_string   

##--------polling continuo dei dati di orientamento--------
## richiesto dalla presenza del  filtro di Kalman

#def polling_orientation():
#    while True:
#        sense.get_orientation()

class leggisensori:  
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        #richiama la funzione che crea il file con la riga di intestazione
        batch_data = []
        file_setup(filename)
        while self._running:
            # legge i dati
            output_string = get_sense_data()            
            print("lettura dati sensori")
            sense.set_pixels(immagine_graf1)
            #inserisce la stringa nella lista batch_data (=buffer x scrittura nel file)
            batch_data.append(output_string)

            # se la dimensione del buffer supera la frequenza di scrittura
            if len(batch_data) >= FREQ_SCRITTURA_DATI:
                print("scrittura file..")
                # Aggiunge le righe nel buffer al file
                with open(filename,"a") as f:
                    for line in batch_data:
                        f.write(line + "\n")
                # cancella il buffer
                batch_data = []
            sleep(FREQ_LETTURA_DATI)


            
class scattafoto:  
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        while self._running:
            camera.capture('Foto%s.jpg' % datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))
            print("scatto foto")
            sense.set_pixels(immagine_foto)
            sleep(FREQ_FOTO)

            
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

##### Variabili #####
FILENAME = "SenseLog"           #nome file CSV
FREQ_LETTURA_DATI= 1            #frequenza raccolta dati
FREQ_SCRITTURA_DATI = 5         #frequenza scrittura su file (in numero di righe)
FREQ_FOTO = 12                  #frequqneza foto in secondi

camera = PiCamera()
camera.resolution = (2592,1944) #Risoluzione foto (v1 max 2592×1944) ( v2 max 3280×2464)


w=(255,255,255)
b=(0,0,0)
r=(255,0,0)
g= (0,153,0)
        
immagine_foto =[
    b,b,b,b,b,b,b,b,
    b,b,b,b,b,b,b,b,
    b,b,b,w,w,b,b,b,
    b,w,w,w,w,w,w,b,
    b,w,w,b,b,w,w,b,
    b,w,w,b,b,w,w,b,
    b,w,w,w,w,w,w,b,
    b,b,b,b,b,b,b,b
    ]

immagine_graf1 =[
    w,b,b,b,b,b,b,b,
    w,r,b,b,b,b,b,b,
    w,r,g,b,g,b,b,b,
    w,r,g,r,g,b,b,b,
    w,r,g,r,g,r,b,r,
    w,r,g,r,g,r,g,r,
    w,r,g,r,g,r,g,r,
    w,w,w,w,w,w,w,w,
    ]

sense = SenseHat()
batch_data= []
filename = FILENAME+"-"+str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))+".csv"

#----------------- video introduttivo -------------------------------------

intro_video.intro_video() #animazione introduttiva
print("Animazione introduttiva")

#-----------------lettura dati sensori-------------------------------------

#lancio thread per polling continuo sensore orientamento
#Thread(target= polling_orientation()).start()
#Create Class
PollingOrientation = polling_orientation()
#Create Thread
PollingOrientationThread = Thread(target=PollingOrientation.run) 
#Start Thread 
PollingOrientationThread.start()

#lancio thread per lettura sensori
#Create Class
LeggiSensori = leggisensori()
#Create Thread
LeggiSensoriThread = Thread(target=LeggiSensori.run) 
#Start Thread 
LeggiSensoriThread.start()

#lancio thread per foto
#Create Class
ScattaFoto = scattafoto()
#Create Thread
ScattaFotoThread = Thread(target=ScattaFoto.run) 
#Start Thread 
ScattaFotoThread.start()

try:

    while True:
        dummy = 1

# se premo CTRL+C esce dal programma, svuota il buffer e termina i thread
except KeyboardInterrupt:
    print('interrupted!')

    # termina i thread
    PollingOrientation.terminate()
    LeggiSensori.terminate()
    ScattaFoto.terminate()
    
    print("scrittura file..")
    # Aggiunge le righe nel buffer al file
    with open(filename,"a") as f:
        for line in batch_data:
            f.write(line + "\n")
    # cancella il buffer
    batch_data = []
    # messaggio
    sense.show_message("Bye Bye", text_colour=[255, 0, 0])

    










