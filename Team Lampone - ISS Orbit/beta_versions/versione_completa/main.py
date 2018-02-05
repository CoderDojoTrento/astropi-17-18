############################################################################
#                PROGRAMMA  ASTROPI GRUPPO LAMPONI                         #
############################################################################
# Legge i dati dai sensori della Sense Hat e
# scatta fotografie per poter determinare la
# velocità a cui si muove la ISS
#
# Prerequisiti:
# sudo pip3 install matplotlib
# sudo pip3 install numpy
# sudo pip3 install cairocffi
# sudo pip3 install ephem
#
# opencv
# opencv-contrib
#
# FILENAME              #nome file CSV
# FREQ_LETTURA_DATI     #frequenza raccolta dati
# FREQ_SCRITTURA_DATI   #frequenza scrittura su file (in numero di righe)
# FREQ_FOTO             #frequqneza foto in secondi
# camera.resolution     #Risoluzione foto (v1 max 2592 × 1944) ( v2 max 3280 × 2464)
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

import features_matching_homography
import ephem
import geometria



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

    return sense_data


## ---- trasforma la lista con i dati in una stringa

def log_data():
    #trasforma la lista in stringa 
    output_string = ",".join(str(value) for value in sense_data)
    #inserisce la stringa nella lista batch_data (=buffer x scrittura nel file)
    batch_data.append(output_string)
    

##--------polling continuo dei dati di orientamento--------
## richiesto dalla presenza del  filtro di Kalman

#def polling_orientation():
#    while True:
#        sense.get_orientation()


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
FREQ_FOTO = 10                  #frequqneza foto in secondi

verbose=0                     #se a 1 aumenta i log a console
camera = PiCamera()
camera.resolution = (640,480) #Risoluzione foto (v1 max 2592 × 1944) ( v2 max 3280 × 2464)

focale=3.60       #lunghezza focale (mm)  (piCam v2: 3.04 - piCam v1: 3.60)
sensx=3760   #dimensione sensore asse x (in pixel) (v1: 3760, v2:3680)
resx=640    #risoluzione img x

altezzaiss=400000000  #altezza ISS (mm)

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

print("Animazione introduttiva")
intro_video.intro_video() #animazione introduttiva

#-----------------lettura dati sensori-------------------------------------

#richiama la funzione che crea il file con la riga di intestazione
file_setup(filename)

#lancio thread per polling continuo sensore orientamento
#Thread(target= polling_orientation()).start()
#Create Class
PollingOrientation = polling_orientation()
#Create Thread
PollingOrientationThread = Thread(target=PollingOrientation.run) 
#Start Thread 
PollingOrientationThread.start()


tempo_ultima_lettura = datetime.now()
tempo_ultima_foto = datetime.now()
#foto_numero = 0
foto1 = ''
try:
    while True:
        # legge i dati
        sense_data = get_sense_data()
        
        # tempo trascorso dall'ultima lettura dati
        tempo_dall_ultima_lettura = sense_data[-1] - tempo_ultima_lettura

        # se il tempo trascorso > della frequenza di lettura impostata 
        if tempo_dall_ultima_lettura.seconds > FREQ_LETTURA_DATI:

            # scrive i dati in una lista buffer di scrittura
            log_data()
            tempo_ultima_lettura = sense_data[-1]
            print("lettura dati sensori")
            sense.set_pixels(immagine_graf1)
          
            
        # se la dimensione del buffer supera la frequenza di scrittura
        if len(batch_data) >= FREQ_SCRITTURA_DATI:
            print("scrive il file..")
            # Aggiunge le righe nel buffer al file
            with open(filename,"a") as f:
                for line in batch_data:
                    f.write(line + "\n")
            # cancella il buffer
            batch_data = []

        #-----------------cattura immagini-------------------------------------
        #tempo trascorso dall'ultima foto
        tempo_dall_ultima_foto = datetime.now() - tempo_ultima_foto
        #se il tempo trascorso > della frequenza di scatto foto 
        if tempo_dall_ultima_foto.seconds > FREQ_FOTO:
            tempo_ultima_foto = datetime.now()
            camera.capture('Foto%s.jpg' % tempo_ultima_foto.strftime('%Y-%m-%d_%H-%M-%S.%f'))
            print("scatto foto")
            sense.set_pixels(immagine_foto)



            #-----------------calcola spostamento e velocità-------------------------------------
            #foto1 = foto_nome
            foto2 = 'Foto%s.jpg' % tempo_ultima_foto.strftime('%Y-%m-%d_%H-%M-%S.%f')
            #foto_numero = foto_numero + 1
            #foto_nome[foto_numero] = 'Foto%s.jpg' % tempo_ultima_foto
            #foto_nome.append('Foto%s.jpg' % tempo_ultima_foto.strftime('%Y-%m-%d_%H-%M-%S.%f'))
            #foto1 = foto_nome[foto_numero-1]
            #foto2 = foto_nome[foto_numero]
            #calcola spostamento immagini
           
            if foto1 != '':
                print("Analisi immagini", foto1, foto2)
                matchesMask,distanza,x1,y1,x2,y2=features_matching_homography.distanza_percorsa_pixel(foto1,foto2,verbose)
                
                # se c'è corrispondenza nelle immagini calcola la velocità
                if matchesMask != None:
                    iss = ephem.readtle('ISS (ZARYA)',
                        '1 25544U 98067A   18027.96608769  .00002138  00000-0  39404-4 0  9997',
                        '2 25544  51.6452 357.7352 0003803  57.4957 343.4832 15.54226828 96711'
                    )
                    iss.compute(datetime.utcnow())
                    altezzaiss = iss.elevation*1000
                    print("altezza ISS=",altezzaiss)

                    intervallo_foto = tempo_ultima_foto.seconds - tempo_dall_ultima_foto.seconds
                    dist=geometria.main(distanza,x1,y1,x2,y2,focale, sensx, resx,altezzaiss,intervallo_foto,verbose)
                    vel=dist/FREQ_FOTO/1000*3600
                    print ("velocita' km/h",vel)
                    messaggio = "vel = %s Km/h" % round(vel,0)
                    sense.show_message(messaggio , scroll_speed=0.04)
            foto1 = foto2

except KeyboardInterrupt:
    print('interrupted!')
    # termina il thread
    PollingOrientation.terminate()    
    print("scrittura file..")
    # Aggiunge le righe nel buffer al file
    with open(filename,"a") as f:
        for line in batch_data:
            f.write(line + "\n")
    # cancella il buffer
    batch_data = []
    sense.show_message("Bye Bye", text_colour=[255, 0, 0])












