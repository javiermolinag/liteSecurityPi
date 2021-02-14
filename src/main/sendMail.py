from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

import datetime
import smtplib
import email

import time
import json
import ssl
import os

conf = json.load(open("../../conf/config.json"))

def removeFile(path):
    file = "../../data/img/" + path
    try:
        if os.path.exists(file):
            os.remove(file)
            print("File deleted..." + path)
    except OSError as error:
        print("There was an error.", error)

def attachImage(filename):
    with open("../../data/img/" + filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    removeFile(filename)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition","attachment; filename= {0}".format(filename))
    return part

def sendMail(msg, filename = []):
    timeNow = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    subject = "Security Cam - " + timeNow
    body = "This is an email sent from liteSecurityPi \n\n" + msg
    message = MIMEMultipart()
    message["From"] = conf["sender_email"]
    message["To"] = conf["receiver_email"]
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    if len(filename) > 0:
        for file in filename:
            message.attach(attachImage(file))
    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(message["From"], conf["password"])
        server.sendmail(message["From"], message["To"], text)

def follow(file):
    file.seek(0,2)
    while(True):
        line = file.readline()
        if not line:
            time.sleep(0.01)
            continue
        yield line

def main():
    name = "../../data/txt/files"
    file = open(name,'r')
    lines = follow(file)
    for line in lines:
        print("Movimiento detectado...",line.split(",")[:-1])
        sendMail("Movimiento detectado...",line.split(",")[:-1])
        #for file in line.split(",")[:-1]:
            #removeFile(file)
    
if __name__ == "__main__":
    main()