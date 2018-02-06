##### Librerie #####
from datetime import datetime, timedelta
from sense_hat import SenseHat
from time import sleep
from threading import Thread
import subprocess
from Team_Trentini_DOP_support import intro_video, mostra_salvataggio, mostra_avanzamento

##### Configurazione del Logging #####
NOME_TEAM = "Trentini DOP - Space Pressure"
PREFISSO_NOME_FILE = "TDOP"
FREQUENZA_SCRITTURA = 20
INTERVALLO_MISURAZIONI=0.01
INTERVALLO_CAMPIONAMENTO=1

##### Funzioni #####
def preparazione_file(nome_file):
    intestazione = []
    intestazione.append("ora")
    intestazione.append("temperatura_CPU")
    intestazione.append("temperatura")
    intestazione.append("umidità")
    intestazione.append("pressione")
    intestazione.extend(["beccheggio", "rollio", "imbardata"])
    intestazione.extend(["mag_x", "mag_y", "mag_z"])
    intestazione.extend(["accel_x", "accel_y", "accel_z"])
    intestazione.extend(["giro_x", "giro_y", "giro_z"])

    with open(nome_file, "w") as f:
        f.write(",".join(str(colonna) for colonna in intestazione)+ "\n")


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


##### Main Program #####
sense = SenseHat()

#----------------- video introduttivo / opening animation -------------------------------------

print("Animazione introduttiva")
intro_video() # chiamata all'animazione introduttiva / opening animation call

pila_di_dati = []

nome_file_dati = PREFISSO_NOME_FILE+"_"+(datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))+".csv"

preparazione_file(nome_file_dati)

Thread(target = raccolta_temporizzata).start()

try:
    while True:
        if len(pila_di_dati) >= FREQUENZA_SCRITTURA:
            print("Scrivo sul file...")
            with open(nome_file_dati, "a") as f:
                for line in pila_di_dati:
                    f.write(line + "\n")
            pila_di_dati = []
            mostra_salvataggio()
        else:
            mostra_avanzamento(len(pila_di_dati)/FREQUENZA_SCRITTURA)

except KeyboardInterrupt:
    print('Esecuzione interrotta!')
    print("Scrivo gli ultimi dati sul file...")
    with open(nome_file_dati, "a") as f:
        for line in pila_di_dati:
            f.write(line + "\n")
    pila_di_dati = []
    sense.show_message("Bye!", text_colour=[  0, 255, 0])