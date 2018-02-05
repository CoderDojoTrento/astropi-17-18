import numpy as np
def main(distanza,x1,y1,x2,y2,f,sensx,resx,Z,t,verbose):
    #calcolo dimensione pixel (mm)
    dimensione_pixel=sensx/resx/1000
    
    dist = (-1/f*(distanza*dimensione_pixel)*Z)/1000
    if (verbose==1):
        print("spostamento in mm su immagine",distanza*dimensione_pixel)
        print("spostamento reale in m",(-1/f*(distanza*dimensione_pixel)*Z)/1000)
    return dist
    
