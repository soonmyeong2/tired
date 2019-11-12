from imutils import face_utils
import random
import queue
import time
import dlib
import cv2

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
        while True:
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)

            # If there is a detected face
            for rect in rects:
                shape = self.predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                # Ratio between eyes
                sleep = 0

                for eye in self.eyes:
                    cv2.circle(frame, (int((shape[eye[0]][0]+shape[eye[1]][0])/2),\
                                       int((shape[eye[0]][1]+shape[eye[1]][1])/2)), 1, (0, 255, 255), -1)
                    cv2.circle(frame, (int((shape[eye[2]][0]+shape[eye[3]][0])/2),\
                                       int((shape[eye[2]][1]+shape[eye[3]][1])/2)), 1, (0, 255, 255), -1)
                    sleep += ((shape[eye[3]][1]+shape[eye[2]][1])/2 - (shape[eye[1]][1]+shape[eye[0]][1])/2)\
                                    / (shape[33][1] - shape[28][1])

                self.factor -= self.eyes_meter.get() / (self.eyes_meter.qsize() + 1) # queue lost size by 1
                self.eyes_meter.put(sleep)
                self.factor += sleep / self.eyes_meter.qsize()

                #if factor <= 0.26: # future features on face
                    #transparentOverlay(frame, img, shape[27])

            if len(rects) == 0: # Not detected
                self.factor -= self.eyes_meter.get() / (self.eyes_meter.qsize() + 1)
                self.eyes_meter.put(0.25)
                self.factor += 0.25 / self.eyes_meter.qsize()

            if self.factor <= 0.26: # sleeing
                h, w, _ = frame.shape
                self.transparentOverlay(frame, self.img, (int(w/2)+random.randrange(1, 11), int(h/2)+random.randrange(1, 11)))
                if len(self.sleep_times)%2 == 0 : self.sleep_times.append(time.strftime('%H%M', time.localtime(time.time())))
            else:
                if len(self.sleep_times)%2 : self.sleep_times.append(time.strftime('%H%M', time.localtime(time.time())))

            print(self.debug, self.factor)
            self.debug += 1

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        cv2.destroyAllWindows()
        self.cap.release()


    def getSleepTime(self):
        return self.sleep_times
    
