from imutils import face_utils
import random
import queue
import time
import dlib
import cv2
from realtime_graph import MakeGraph


class SleepReader:
    def __init__(self):
        # for video
        self.predictor = dlib.shape_predictor("etc/shape_predictor_68_face_landmarks.dat")
        self.cap = cv2.VideoCapture(0)
        self.detector = dlib.get_frontal_face_detector()
        self.img = cv2.imread("etc/sleep_icon.png", -1)

        # sleep is determined by the average of queue values
        self.eyes_meter = queue.Queue()
        # eye dots index
        self.eyes = [[37, 38, 40, 41], [43, 44, 46, 47]]
        # average of QV
        self.factor = 0.33
        # result list
        self.sleep_times = list()
        # queue init
        for _ in range(50) : self.eyes_meter.put(self.factor)
        # for debug
        self.debug = 0
        
        # for graph
        #self.graph = MakeGraph([x for x in range(50)], [self.factor]*50, self.factor)
        

    # img overlay
    def transparentOverlay(self, src, overlay, pos=(0, 0), scale=1):
        overlay = cv2.resize(overlay, (0, 0), fx=scale, fy=scale)
        h, w, _ = overlay.shape  # foreground
        rows, cols, _ = src.shape  # background
        y, x = pos[0] - int(w/2), pos[1] - int(h/2)  # Position

        for i in range(h):
            for j in range(w):
                if x + i >= rows or y + j >= cols:  # over index
                    continue
                alpha = float(overlay[i][j][3] / 255.0) * 0.7 #transparency
                src[x + i][y + j] = alpha * overlay[i][j][:3] + (1 - alpha) * src[x + i][y + j]
        return src


    def run(self):
        sleep = 0
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        while True:
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)
            h, w, _ = frame.shape  # foreground
        

            # If there is a detected face
            for rect in rects:
                shape = self.predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                # Ratio between eyes
                sleep = 0
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]

		
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                for eye in self.eyes:
                    sleep += ((shape[eye[3]][1]+shape[eye[2]][1])/2 - (shape[eye[1]][1]+shape[eye[0]][1])/2)\
                                    / (shape[33][1] - shape[28][1])
                    
                self.factor -= self.eyes_meter.get() / (self.eyes_meter.qsize() + 1) # queue lost size by 1
                self.eyes_meter.put(sleep)
                self.factor += sleep / self.eyes_meter.qsize()

                
                # factor 출력
                cv2.putText(frame, "Factor: {:.2f}".format(self.factor), (w-200, 30),\
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                #if factor <= 0.26: # future features on face
                    #transparentOverlay(frame, img, shape[27])

            if len(rects) == 0: # Not detected
                self.factor -= self.eyes_meter.get() / (self.eyes_meter.qsize() + 1)
                self.eyes_meter.put(0.25)
                self.factor += 0.25 / self.eyes_meter.qsize()
                sleep = 0

            if self.factor <= 0.26: # sleeing
                # 존다는 메세지 출력
                cv2.putText(frame, "Sleep !", (100, 30),\
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if len(self.sleep_times)%2 == 0 : self.sleep_times.append(time.strftime('%H%M', time.localtime(time.time())))
            else:
                if len(self.sleep_times)%2 : self.sleep_times.append(time.strftime('%H%M', time.localtime(time.time())))

            ## visual code
            #print(self.debug, self.factor)
            #self.debug += 1
            #self.graph.makeDraw(sleep, self.factor)
            
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        cv2.destroyAllWindows()
        self.cap.release()


    def getSleepTime(self):
        return self.sleep_times
    
