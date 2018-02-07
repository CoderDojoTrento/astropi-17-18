""" #########################################################################################

    ASTROPI 2018 - MISSION "SPACE LAB" (Life in Space): GRUPPO I TRENTINI DOP (Italy)   

Abstract IT: I sensori del Sense HAT sono monitorati in continuazione, in particolare per
             quanto riguarda i parametri pressione e temperatura dell'aria interna alla ISS
Abstract EN: Sense HAT sensors are monitored continuously, in particular the pressure and
             the temperature of the air inside the ISS

Gruppo 'I Trentini DOP' 2018 @ CoderDojo Trento, Italy:
 - Matteo Nardin
 - Lorenzo Berlanda
 - Mattia Tomasi
 - Stefano Libardi


IT: Parametri utilizzati nel programma:
PREFISSO_NOME_FILE            # prefisso nome file CSV
FREQUENZA_SCRITTURA           # frequenza scrittura su file (in numero di righe)
INTERVALLO_MISURAZIONI        # frequenza consultazione Sense HAT (in sec)
INTERVALLO_CAMPIONAMENTO      # frequenza raccolta dati (in sec)

EN: Config parameters used in the code:
PREFISSO_NOME_FILE            # CSV file name prefix
FREQUENZA_SCRITTURA           # writing to file frequency (in number of lines)
INTERVALLO_MISURAZIONI        # data reading frequency (in sec)
INTERVALLO_CAMPIONAMENTO      # data collection frequency (in sec)


N.B. IT: Non e' necessario trascrivere nel codice le righe TLE della ISS: tutto il processamento e' 
fatto dopo il volo; tutto quello di cui ha bisogno il programma e' un ora di sistema ben regolata
(per ricostruire l'esposizione della ISS al sole dal timestamp dei dati).

N.B. EN: No need to insert updated TLE entries: all processing will be made off-line after the flight;
all we need is a well-synced system time (in order to reconstruct exposure to the sun of the ISS
given the data timestamp).

""" ###########################################################################

####################  Import / Import  ####################

# Librerie esterne / External libraries
from datetime import datetime, timedelta
from sense_hat import SenseHat
from time import sleep
from threading import Thread
import subprocess

# Moduli fatti in casa / Homemade modules
from Team_Trentini_DOP_support import intro_video, mostra_salvataggio, mostra_avanzamento


#################### Configurazione / Configuration ####################

PREFISSO_NOME_FILE = "TDOP"       # prefisso nome file CSV / CSV file name prefix
FREQUENZA_SCRITTURA = 20          # frequenza scrittura su file (in numero di righe) / writing to file frequency (in number of lines)
INTERVALLO_MISURAZIONI = 0.01     # frequenza consultazione Sense HAT (in sec) / data reading frequency (in sec)
INTERVALLO_CAMPIONAMENTO = 1      # frequenza raccolta dati (in sec) / data collection frequency (in sec)


#################### Funzioni / Functions ####################

# crea il file ed aggiunge l'intestazione / create the file and insert the header
def preparazione_file(nome_file):
    intestazione = []
    intestazione.append("ora")
    intestazione.append("temperatura_CPU")
    intestazione.append("temperatura")
    intestazione.append("umidita'")
    intestazione.append("pressione")
    intestazione.extend(["beccheggio", "rollio", "imbardata"])
    intestazione.extend(["mag_x", "mag_y", "mag_z"])
    intestazione.extend(["accel_x", "accel_y", "accel_z"])
    intestazione.extend(["giro_x", "giro_y", "giro_z"])

    with open(nome_file, "w") as f:
        f.write(",".join(str(colonna) for colonna in intestazione)+ "\n")

# legge i dati dal sensore e la temperatura della CPU / read the sensor data and the CPU temperature
def leggi_dati_sensore():
    riga_di_dati = []
    riga_di_dati.append(datetime.now())
    riga_di_dati.append(str(subprocess.check_output("vcgencmd measure_temp", shell=True)).split("=")[1].split("'")[0]) # temp=36.3'C 
    riga_di_dati.append(sense.get_temperature())
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

    return riga_di_dati

# campiona i dati con una frequenza data / samples data with a given frequency
def raccolta_temporizzata():
    ora_ultimo_campionamento = datetime.now()
    while True:
        dati_sensore = leggi_dati_sensore()
        tempo_passato_ultimo_campionamento = dati_sensore[0] - ora_ultimo_campionamento
        if tempo_passato_ultimo_campionamento > timedelta(seconds=INTERVALLO_CAMPIONAMENTO):
            output_string = ",".join(str(elemento) for elemento in dati_sensore)
            pila_di_dati.append(output_string)
            ora_ultimo_campionamento = dati_sensore[0]
        sleep(INTERVALLO_MISURAZIONI)


#################### Programma principale / Main program ####################

sense = SenseHat()
pila_di_dati = [] # buffer utilizzato per raccogliere i dati da scrivere su file / buffer used to collect data that has to be written in the file

# IT: chiamata all'animazione introduttiva
# EN: opening animation call

print("Animazione introduttiva")
intro_video()

# IT: richiama la funzione che crea il file con la riga di intestazione
# EN: call to the function that creates the files with the header
nome_file_dati = PREFISSO_NOME_FILE+"_"+(datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))+".csv"
preparazione_file(nome_file_dati)

# IT: lancio thread per raccolta dati sensori
# EN: start the thread for the sensor data gathering
Thread(target = raccolta_temporizzata).start()

try:
    while True:
        if len(pila_di_dati) >= FREQUENZA_SCRITTURA:
            # IT: se sono state raccolte abbastanza misure, scrive su file
            # EN: when enough measures have been collected, write them to file
            print("Scrivo sul file...")
            with open(nome_file_dati, "a") as f:
                for line in pila_di_dati:
                    f.write(line + "\n")
            pila_di_dati = []
            mostra_salvataggio()
        else:
            # IT: mostra il riempimento del buffer sulla matrice di LED
            # EN: shows the filling of the buffer on the LED matrix
            mostra_avanzamento(len(pila_di_dati)/FREQUENZA_SCRITTURA)

# IT: se premo CTRL+C esce dal programma e svuota il buffer
# EN: when we hit CTRL+C, it terminate the program by emptying the buffer
except KeyboardInterrupt:
    print('Esecuzione interrotta!')
    print("Scrivo gli ultimi dati sul file...")
    with open(nome_file_dati, "a") as f:
        for line in pila_di_dati:
            f.write(line + "\n")
    pila_di_dati = []
    sense.show_message("Bye!", text_colour=[  0, 255, 0])
