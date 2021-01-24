import numpy as np
import json
import cv2

def getPSNR(image1, image2):
    image1 = image1.astype(np.float64)
    image2 = image2.astype(np.float64)
    dif = np.sum((image1 - image2) ** 2)
    mse = dif / (image1.shape[0] * image2.shape[1]* image2.shape[2])
    psnr = 10 * np.log10((255*255)/mse)
    return psnr

def sendMail(msg):
    print(msg)

try:
    conf = json.load(open("../../conf/config.json"))
except:
    sendMail("Error in JSON file")
    exit()

cap = cv2.VideoCapture(-1) #inicia dispositivo -1 (camara) 0 (webcam)
frameAnt = np.zeros((480,640,3),np.uint8)
while(cap.isOpened()): #continua mientras el dispositivo este disponible
    ret, frame = cap.read() #lee un frame (imagen)
    if ret == True: #revisa si el frame inicio correctamente
        psnr =  getPSNR(frame,frameAnt)  #comparamos frame actual con frame anterior
        if psnr < conf["threshold"]:   #ajustamos sensibilidad del sistema
            sendMail("Movimiento detectado")
        else:
            print("...")
        cv2.imshow('frame',frame) #mostramos frame en pantalla
        frameAnt = np.copy(frame) #copiamos frame a frameAnt
        if cv2.waitKey(1) & 0xFF == ord('q'):  #termina si existe evento en el teclado 'q'
            sendMail("KeyboardInterrupt")
            break
    else:
        sendMail("Something went wrong in cap.read()")
        break
    
cap.release()
cv2.destroyAllWindows()


