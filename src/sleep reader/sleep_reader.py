from imutils import face_utils
import random
import queue
import time
import dlib
import cv2

# for video
predictor = dlib.shape_predictor("etc/shape_predictor_68_face_landmarks.dat")
cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
img = cv2.imread("etc/sleep_icon.png", -1)

# sleep is determined by the average of queue values
eyes_meter = queue.Queue()
# eye dots index
eyes = [[37, 38, 40, 41], [43, 44, 46, 47]]
# average of QV
factor = 0.33
# result list
sleep_times = list()

# queue init
for _ in range(50) : eyes_meter.put(factor)

# [2359, 0031, 0033] -> [2359, 2431, 2433]
def calculateNextDay(ary):
    if len(ary) <= 2:
            return
        
    if int(ary[-1])-int(ary[0]) < 0:
        for i in range(len(ary)-1, -1, -1):
            if ary[i] < '2359' : ary[i] = str(int(ary[i]) + 2400)
            else : return

# remove duplicated time
def calculateDupTime(ary, idx):
    if len(ary) <= 2 or idx < 2:
        return

    if int(ary[idx])-int(ary[idx-1]) <= 1:
        ary.pop(idx)
        ary.pop(idx-1)

    calculateDupTime(ary, idx-2)

def timeParsing(ary):
    for i in range(1, len(ary)-1, 2):
        ary[i] = ary[i].replace(ary[i], ary[i] + '/')
    return ''.join(ary)

# img overlay
def transparentOverlay(src, overlay, pos=(0, 0), scale=1):
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

# for debug
debug = 0

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    # If there is a detected face
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        sleep = 0

        for eye in eyes:
            cv2.circle(frame, (int((shape[eye[0]][0]+shape[eye[1]][0])/2),\
                               int((shape[eye[0]][1]+shape[eye[1]][1])/2)), 1, (0, 255, 255), -1)
            cv2.circle(frame, (int((shape[eye[2]][0]+shape[eye[3]][0])/2),\
                               int((shape[eye[2]][1]+shape[eye[3]][1])/2)), 1, (0, 255, 255), -1)
            sleep += ((shape[eye[3]][1]+shape[eye[2]][1])/2 - (shape[eye[1]][1]+shape[eye[0]][1])/2)\
                            / (shape[33][1] - shape[28][1])

        factor -= eyes_meter.get() / (eyes_meter.qsize() + 1) # queue lost size by 1
        eyes_meter.put(sleep)
        factor += sleep / eyes_meter.qsize()

        #if factor <= 0.26: # future features on face
            #transparentOverlay(frame, img, shape[27])

    if len(rects) == 0: # Not detected
        factor -= eyes_meter.get() / (eyes_meter.qsize() + 1)
        eyes_meter.put(0.25)
        factor += 0.25 / eyes_meter.qsize()

    if factor <= 0.26: # sleeing
        h, w, _ = frame.shape
        transparentOverlay(frame, img, (int(w/2)+random.randrange(1, 7), int(h/2)+random.randrange(1, 7)))
        if len(sleep_times)%2 == 0 : sleep_times.append(time.strftime('%H%M', time.localtime(time.time())))
    else:
        if len(sleep_times)%2 : sleep_times.append(time.strftime('%H%M', time.localtime(time.time())))

    print(debug, factor)
    debug += 1

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()
cap.release()

print(sleep_times)
calculateNextDay(sleep_times)
calculateDupTime(sleep_times, len(sleep_times) - 2)
print(sleep_times)
print(timeParsing(sleep_times))
