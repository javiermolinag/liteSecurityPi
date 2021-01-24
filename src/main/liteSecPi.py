from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

import smtplib
import email
import ssl

import numpy as np
import json
import cv2

conf = json.load(open("../../conf/config.json"))

def getPSNR(image1, image2):
    image1 = image1.astype(np.float64)
    image2 = image2.astype(np.float64)
    dif = np.sum((image1 - image2) ** 2)
    mse = dif / (image1.shape[0] * image2.shape[1]* image2.shape[2])
    psnr = 10 * np.log10((255*255)/mse)
    return psnr

def sendMail(msg, filename):
    subject = "Security Cam"
    body = "This is an email sent from liteSecurityPi \n\n" + msg
    sender_email = conf["sender_email"]
    password = conf["password"]
    receiver_email = conf["receiver_email"]

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    if len(filename) > 0:

        # Open file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        
        # Add header as key/value pair to attachment part
        part.add_header("Content-Disposition","attachment; filename= {0}".format(filename))
        
        # Add attachment to message and convert message to string
        message.attach(part)
        
    text = message.as_string()

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text) 
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 



cap = cv2.VideoCapture(-1) #inicia dispositivo -1 (camara) 0 (webcam)
frameAnt = np.zeros((480,640,3),np.uint8)
while(cap.isOpened()): #continua mientras el dispositivo este disponible
    ret, frame = cap.read() #lee un frame (imagen)
    if ret==True: #revisa si el frame inicio correctamente
        psnr =  getPSNR(frame,frameAnt)  #comparamos frame actual con frame anterior
        if psnr < conf["threshold"]:   #ajustamos sensibilidad del sistema
            cv2.imwrite("image.jpg", frame) 
            sendMail("Movimiento detectado","image.jpg")
        #else:
        #    print("...")
        cv2.imshow('frame',frame) #mostramos frame en pantalla
        frameAnt = np.copy(frame) #copiamos frame a frameAnt
        if cv2.waitKey(1) & 0xFF == ord('q'):  #termina si existe evento en el teclado 'q'
            sendMail("KeyboardInterrupt","")
            break 
    else:
        sendMail("Something went wrong with cap.read()","")
        break
    
cap.release()
out.release()
cv2.destroyAllWindows()
