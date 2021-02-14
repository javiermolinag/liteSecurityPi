import numpy as np
import sendMail
import datetime
import json
import time
import cv2


conf = json.load(open("../../conf/config.json"))

def motionDetection(diff,frame):
    if diff >= conf["threshold"]:
        timeNow = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
        fileName = "img_" + str(timeNow) + ".jpg"
        cv2.imwrite("../../data/img/" + fileName, frame)
        with open("../../data/txt/files", 'a') as files:
            files.write(fileName + ",")
        return True
    return False

def getDiffMetric(image1, image2):
    image1 = image1.astype(np.float64)
    image2 = image2.astype(np.float64)
    size = (image1.shape[0] * image1.shape[1]* image1.shape[2])
    mae = np.sum(abs(image1 - image2))/size
    #mse = np.sum((image1 - image2) ** 2) / size
    #psnr = 10 * np.log10((255*255)/mse)
    #return psnr, mse, mae
    return mae

def main():
    capture_duration = 10
    cap = cv2.VideoCapture(-1)
    cap.set(3,1280)
    cap.set(4,720)
    #frameAnt = np.zeros((480,640,3),np.uint8)
    frameAnt = np.zeros((720,1280,3),np.uint8)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            diff = getDiffMetric(frame,frameAnt)
            print(diff)
            flag = motionDetection(diff,frame)
            #cv2.imshow('frame',frame) ##
            
            if flag:
                start_time = time.time()
                timeNow = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
                while( int(time.time() - start_time) < capture_duration ):
                    time.sleep(0.5)
                    ret, frame = cap.read()
                    if ret == True:
                        motionDetection(conf["threshold"],frame)
                        
            frameAnt = np.copy(frame)
            
            ''' write video not working yet
            if flag:
                start_time = time.time()
                timeNow = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
                out = cv2.VideoWriter("../../data/img/" + "outpy_" + timeNow + ".avi",cv2.VideoWriter_fourcc(*'XVID'), 10, (640,480))
                while( int(time.time() - start_time) < capture_duration ):
                    if cap.isOpened():
                        ret, frame = cap.read()
                        frameAnt = np.copy(frame)
                        if ret == True:
                            frame = cv2.flip(frame,0)
                            print("writing video...")
                            out.write(frame)
                out.release()
                cap.release()
            '''

        else:
            sendMail("Something went wrong with camera()")
            break
    cap.release()
    #cv2.destroyAllWindows() ##

if __name__ == "__main__":
    main()