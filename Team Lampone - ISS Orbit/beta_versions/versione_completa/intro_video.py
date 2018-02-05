####################################################################
# animazioni introduttiva con conto alla rovescia e partenza Shuttle
####################################################################

from sense_hat import SenseHat
from time import sleep
def intro_video():
        s=SenseHat()
        w=(255,255,255)
        n=(0,0,0)
        r=(255,0,0)
        b=(0,0,255)
        v= (0,153,0)

        #countdown
        p=[
        r,r,r,n,n,b,n,n,
        n,n,r,n,n,w,n,n,
        r,r,r,n,w,b,w,n,
        n,n,r,n,w,w,w,n,
        r,r,r,n,w,w,w,n,
        n,n,n,n,w,w,w,n,
        n,n,n,n,w,w,w,n,
        n,n,n,w,b,b,b,w
        ]
        s.set_pixels(p)
        sleep(1)
        s.set_pixel(2,3,n)
        s.set_pixel(0,3,r)
        sleep(1)
        for y in range(0,5):
                s.set_pixel(0,y,n)
                s.set_pixel(1,y,r)
                s.set_pixel(2,y,n)
        sleep(1)

        # frame shuttle
        p=[
        n,n,n,n,n,w,n,n,
        n,n,n,n,w,b,w,n,
        n,n,n,n,w,w,w,n,
        n,n,n,n,w,w,w,n,
        n,n,n,n,w,w,w,n,
        n,n,n,n,w,w,w,n,
        n,n,n,w,b,b,b,w,
        n,n,n,r,r,n,r,r
        ]
        s.set_pixels(p)



        #animazione Shuttle: sposta una riga in alto e aggiunge riga nera in fondo
        for u in range(0,7):
          sleep(0.2)
          p2=p
          for q in range(8,64):
            p2[q-8]=p[q]
          for q in range(0,8):
            p2[q+56]=n
          s.set_pixels(p2)

        #Bandiera ITA

        sleep(0.2)
        p = [
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        v,v,v,w,w,r,r,r,
        ]
        s.set_pixels(p)

        #Messaggio
        sleep(1)
        s.show_message("Lamponi Group (ITALIA)" , scroll_speed=0.04)




