#############################################################
"""
IT: questo modulo raccoglie le animazione impiegate nel programma
principale, all'avvio ed al momento del salvataggio dei dati su disco;
realizza anche il disegno che mostra il caricamento progressivo del buffer

EN: this module collects the animations used in the main program
at the beginning as presentation and when saving data to disk;
it also implements the drawing showing the progressive loading of the buffer
"""
#############################################################

from sense_hat import SenseHat
from time import sleep

# IT: definiamo i colori che vengono usati in tutti i disegni
# EN: let's define the colors that are used in all the drawings
w=(255, 255, 255)  # bianco / white
n=(  0,   0,   0)  # nero   / black
r=(255,   0,   0)  # rosso  / red
b=(  0,   0, 255)  # blu    / blue
v=(  0, 153,   0)  # verde  / green
g=(190, 190,   0)  # giallo / yellow


# IT: animazione introduttiva: mostra la bandiera italiana e scritta scorrevole col nome del gruppo
# EN: opening animation: it shows the italian flag and a scrolling banner with the name of the team

def intro_video():
    s=SenseHat()
    s.low_light = True

    # bandiera ITA / ITA flag
    sleep(0.2)
    bandiera = [
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
    ]
    s.set_pixels(bandiera)

    # messaggio di presentazione / presentation message
    sleep(1)
    s.show_message("Trentini DOP Team (ITALIA)", scroll_speed=0.04)
    s.set_pixels(bandiera)
    sleep(1)


# IT: animazione mostrata durante il salvataggio dei dati su disco: una freccia mobile che punta all'icona di una cartella
# EN: animation shown when saving data to disk: a moving arrow that points toward a folder icon

def mostra_salvataggio():
    s=SenseHat()
    s.low_light = True

    # freccia mobile / moving arrow
    s.show_message("-->", text_colour=v, scroll_speed=0.04)

    # disegno cartella / folder image
    cartella = [
        n,g,g,n,n,n,n,n,
        g,n,n,g,n,n,n,n,
        g,n,n,g,g,g,g,n,
        g,n,n,n,n,n,n,g,
        g,n,n,n,n,n,n,g,
        g,n,n,n,n,n,n,g,
        g,n,n,n,n,n,n,g,
        n,g,g,g,g,g,g,n,
    ]
    s.set_pixels(cartella)

    sleep(1)


# IT: disegno che mostra il caricamento progressivo del buffer: la funzione viene richiamata 
#     dal programma principale indicando una percentuale di riempimento; al suo interno viene 
#     calcolato quanti dei 64 LED devono venire accesi e quanti vanno spenti
# EN: drawing that shows the progressive loading of the buffer: the function is called by the
#     main program that passes the filling percentage as argument; inside the body it is calculated
#     how many out of the 64 LEDs must be turned on and how many off

def mostra_avanzamento(percentuale):
    s=SenseHat()
    s.low_light = True

    avanzamento = []
    accesi = int(percentuale * 64);
    spenti = 64 - accesi
    for i in range(accesi):
        avanzamento.append(b)
    for i in range(spenti):
        avanzamento.append(n)
    
    s.set_pixels(avanzamento)

    sleep(0.3)
