import numpy as np
import cv2
from matplotlib import pyplot as plt


#--------------------------------------------------------------------------------------------
#     calcola la distanza tra due punti
#--------------------------------------------------------------------------------------------  

def dist(p1,p2):   
    return np.sqrt(np.sum((p1-p2)**2))

#--------------------------------------------------------------------------------------------
#     calcola la matrice omografica a partire da due immagini
#--------------------------------------------------------------------------------------------  

def Homography_Matrix(img1,img2):
    MIN_MATCH_COUNT = 10

    # carica immagini
    img1 = cv2.imread(img1,0)          
    img2 = cv2.imread(img2,0) 

    # Initiate SIFT detector
    sift = cv2.xfeatures2d.SIFT_create()

    # find the keypoints (kp) and calculate descriptors (des) with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    # Matching descriptor vectors using FLANN matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
            if m.distance < 0.7*n.distance:
                    good.append(m)

    #verifica se ci sono almeno MIN_MATCH_COUNT per stabilire se l'oggetto è lo stesso

    if len(good)>MIN_MATCH_COUNT:
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            
            # calculate Homografic Matrix       
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)

            matchesMask = mask.ravel().tolist()
    else:
            dist_a_b = "none"
            print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
            matchesMask = None
            M = None

    return img1,kp1,img2,kp2,good,M,matchesMask

#--------------------------------------------------------------------------------------------
#     trasforma le coordinate del centro dell'immagine in base alla matrice homografica M
#--------------------------------------------------------------------------------------------    
def center_pixel_move(img1,M):
    # calcola lo spostamento del punto centrale dell'immagine 1
    h,w = img1.shape
    pts_center = np.float32([(w-1)/2,(h-1)/2]).reshape(-1,1,2)
    dst_center = cv2.perspectiveTransform(pts_center,M)
    dist_a_b = dist(dst_center,pts_center)
    return dist_a_b, pts_center[0,0,0],pts_center[0,0,1],dst_center[0,0,0],dst_center[0,0,1]
 

#--------------------------------------------------------------------------------------------
#     visualizza le immagini elaborate e i dati ( per debug)
#--------------------------------------------------------------------------------------------  

def plot_homography(img1,kp1,img2,kp2,good,M,matchesMask):

    ###Calcola la trasformazione dei vertici dell'immagine 1 sulll'immagine 2
    h,w = img1.shape
    #pts = coordinate angoli immagine 1
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    #calcola gli angoli dell'img1 sull'img2 
    dst = cv2.perspectiveTransform(pts,M)
    # disegna il contorno di img1 su img2
    img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)

    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                               singlePointColor = None,
                               matchesMask = matchesMask, # draw only inliers
                               flags = 2)
    #traccia la corrispondenza tra i punti
    img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
    #salva l'immagine in un file
    cv2.imwrite('BFMatcher_Homography.jpg',img3)
    #visulalizza l'immagine
    #-plt.imshow(img3, 'gray'),plt.show()
    print("altezza immagine: ",h)
    print("larghezza immagine: ",w)
    print("vertici img1: ",pts)
    print("vertici img1 su img2: ",dst)
    print("Homography Matrix")
    print(M)
    e,eV=np.linalg.eigh(M)
    print("Autovalori")
    print(e)
    print("Autovettori")
    print(eV)
    N = np.linalg.inv(M)
    print("Inverse Homography")
    print(N)

#--------------------------------------------------------------------------------------------
#     Date due immagini restituisce la distanza in pixel percorsa
#-------------------------------------------------------------------------------------------- 

def distanza_percorsa_pixel(img1,img2,verbose):   
    #Calcola la corrispondenza tra le immagini
    img1,kp1,img2,kp2,good,M,matchesMask=Homography_Matrix(img1,img2)

    

    if matchesMask == None:
        distanza = 0
        x1=0
        y1=0
        x2=0
        y2=0
        
    else:
        #Calcola di quanti pixel si è spostato il centro dell'immagine
        print("N. di features matching: ",len(good))
        distanza,x1,y1,x2,y2 = center_pixel_move(img1,M)
        # se ho scelto un output verbose stampa info e foto
        if (verbose==1):
            plot_homography(img1,kp1,img2,kp2,good,M,matchesMask) 
            print("centro img1: ",x1, y1)
            print("centro img1 su img2: ",x2, y2)
            print("spostamento del centro in pixel: ",distanza)

    return matchesMask,distanza,x1,y1,x2,y2


