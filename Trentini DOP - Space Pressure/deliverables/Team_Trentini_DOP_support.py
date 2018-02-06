#############################################################
# IT: animazioni introduttiva con bandiera e scritta mobile #
# EN: opening animation with flag and scrolling banner      #
#############################################################

from sense_hat import SenseHat
from time import sleep

w=(255, 255, 255)  # bianco / white
n=(  0,   0,   0)  # nero   / black
r=(255,   0,   0)  # rosso  / red
b=(  0,   0, 255)  # blu    / blue
v=(  0, 153,   0)  # verde  / green
g=(190, 190,   0)  # giallo / yellow

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


def mostra_salvataggio():
    s=SenseHat()
    s.low_light = True

    # messaggio di presentazione / presentation message
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

def mostra_avanzamento(percentuale):
    s=SenseHat()
    s.low_light = True

    avanzamento = []
    pieni = int(percentuale * 64);
    for i in range(pieni):
        avanzamento.append(b)
    for i in range(64 - pieni):
        avanzamento.append(n)
    
    s.set_pixels(avanzamento)

    sleep(0.3)
