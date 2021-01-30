from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

import datetime

import smtplib
import email
import ssl

import numpy as np
import json
import cv2

conf = json.load(open("../../conf/config.json"))

def getDiffMetric(image1, image2):
    image1 = image1.astype(np.float64)
    image2 = image2.astype(np.float64)
    size = (image1.shape[0] * image1.shape[1]* image1.shape[2])
    mae = np.sum(abs(image1 - image2))/size
    #mse = np.sum((image1 - image2) ** 2) / size
    #psnr = 10 * np.log10((255*255)/mse)
    #return psnr, mse, mae
    return mae

def attachImage(filename):
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read()) 
    encoders.encode_base64(part)
    part.add_header("Content-Disposition","attachment; filename= {0}".format(filename))
    return part

def sendMail(msg, filename=""):
    subject = "Security Cam"
    body = "This is an email sent from liteSecurityPi \n\n" + msg
    message = MIMEMultipart()
    message["From"] = conf["sender_email"]
    message["To"] = conf["receiver_email"]
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    if len(filename) > 0:
        message.attach(attachImage(filename))
    text = message.as_string()
    context = ssl.create_default_context()
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(message["From"], conf["password"])
        server.sendmail(message["From"], message["To"], text)

def main():
    cap = cv2.VideoCapture(-1)
    cap.set(3,1280)
    cap.set(4,720)
    #frameAnt = np.zeros((480,640,3),np.uint8)
    frameAnt = np.zeros((720,1280,3),np.uint8)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            #psnr,mse,mae = getDiffMetric(frame,frameAnt) ##
            #print(psnr, " --- ", mse, " --- ", mae) ##
            diff = getDiffMetric(frame,frameAnt)
            print(diff)
            if diff > conf["threshold"]:
                timeNow = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                cv2.imwrite("../../data/img_" + str(timeNow) + ".jpg", frame)
                #sendMail("Movimiento detectado..." + str(psnr),"image.jpg")
            #cv2.imshow('frame',frame) ##
            frameAnt = np.copy(frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    sendMail("KeyboardInterrupt")
            #    break
        else:
            sendMail("Something went wrong with camera()")
            break
    cap.release()
    cv2.destroyAllWindows() ##

if __name__ == "__main__":
    main()