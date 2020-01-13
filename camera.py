import cv2, mss, os, os.path, shutil, time, logging, threading, time, sys, atexit, json, argparse, imutils
from multiprocessing import Process
from imutils.video import VideoStream
from os.path import isfile, join
import pyscreenshot as ImageGrab
# from PIL import Image, ImageGrab
import moviepy.editor as mp
from datetime import datetime
import natsort as nt
from datetime import datetime
from send_email import email_picture
from threading import Timer
import main
# captureScreen = IntVar()
captureScreen = False
recording = False
email_pictures = True
faceDetection = True
SMILEY_FACE = False

canvas_height=200
canvas_width=200
START_TIME = 5
SEND_EMAIL_DELAY = 10
TIME = 0
EMAIL_TIME = 0

cascade_files_dir = os.path.dirname(os.path.realpath(__file__)) + '/Data Models'
cascade_files = []
for r, d, f in os.walk(cascade_files_dir):
    for file in f:
        if '.xml' in file: cascade_files.append(os.path.join(r, file))
print(cascade_files)
settings_file = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
settings_json = []

saved_color = []
send_email = []
cap_screen = []
record_video = []
smiley_face = []
dark_mode = []
face_detect = []

email_delay = []
picture_delay = []
selected_data_index = []

cycles_file = os.path.dirname(os.path.realpath(__file__)) + '/cycles.json'
cycles_json = []

OnToList = []
OnFromList = []
OffToList = []
OffFromList = []
alwaysOnList = []
cycles = []

alwaysOn = False
timeToSend = False
currentTime = ''
lastCurrentTime = ''
currentTimeDay = ''
currentTimeHour = 0
currentTimeMinute = 0

red, green, blue = 0, 0, 0
frame = ''
image_folder = 'Pics'
video_name = os.path.dirname(os.path.realpath(__file__)) + '/temp.avi'
numOfPics = 0
cascade = cv2.CascadeClassifier(cascade_files[0])
camera_port = 0
cap = cv2.VideoCapture(camera_port)
frame = []
ret = []
firstFrame = None
vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter(os.path.dirname(os.path.realpath(__file__)) + "/cam_video.mp4", vid_cod, 17, (640,480))
TIME_LIMIT = 100
def removePictures():
    for the_file in os.listdir(image_folder):
        file_path = os.path.join(image_folder, the_file)
        try:
            if os.path.isfile(file_path): os.unlink(file_path)
        except Exception as e:
            print(e)
def makeVideo():
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    if len(images) == 0:
        print('No Images Found')
        return
    else:
        images = nt.natsorted(images)
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape
        video = cv2.VideoWriter(video_name, 0, 17, (width, height))
        for image in images: video.write(cv2.imread(os.path.join(image_folder, image)))
        video.release()
        print(len(images))
def savePicture(num):
    if not captureScreen:
        # CAPTURE WEBCAM
        return_value, image = cap.read()
        cv2.imwrite("Pics/{0}.png".format(num),image)
    else:
        # CAPTURE SCREEN
        with mss.mss() as sct: filename = sct.shot(output=f'Pics/{num}.png')
def findFaceInImage(num):
    global TIME, EMAIL_TIME, numOfPics, captureScreen, recording, email_pictures, SMILEY_FACE, SEND_EMAIL_DELAY, START_TIME, cascade
    global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, red, green, blue
    saved_color.clear()
    send_email.clear()
    cap_screen.clear()
    record_video.clear()
    smiley_face.clear()
    dark_mode.clear()
    email_delay.clear()
    picture_delay.clear()
    face_detect.clear()
    selected_data_index.clear()
    with open(settings_file) as file:
        settings_json = json.load(file)
        for info in settings_json:
            for color in info['saved color']: saved_color.append(color)
            for screen in info['capture screen']: cap_screen.append(screen)
            for video in info['record video']: record_video.append(video)
            for email in info['send email']: send_email.append(email)
            for smile in info['smiley face']: smiley_face.append(smile)
            for dark in info['dark mode']: dark_mode.append(dark)
            for email_d in info['email delay']: email_delay.append(email_d)
            for picture in info['picture delay']: picture_delay.append(picture)
            for ind in info['selected data index']: selected_data_index.append(ind)
            for face in info['face detect']: face_detect.append(face)
    START_TIME = int(picture_delay[0])
    SEND_EMAIL_DELAY = int(email_delay[0])
    SMILEY_FACE = (True if smiley_face[0] == 'True' else False)
    captureScreen = (True if cap_screen[0] == 'True' else False)
    recording = (True if record_video[0] == 'True' else False)
    email_pictures = (True if send_email[0] == 'True' else False)
    faceDetection = (True if face_detect[0] == 'True' else False)
    cascade = cv2.CascadeClassifier(cascade_files[int(selected_data_index[0])])
    eye_cascade = cv2.CascadeClassifier(cascade_files[0])
    mouth_cascade = cv2.CascadeClassifier(cascade_files[17])
    eyes = []
    mouth = []
    red, green, blue = int(saved_color[2]), int(saved_color[1]), int(saved_color[0])
    try:
        cropped_image_name = 'Cropped Image.png'
        image_name = 'Image.png'
        img = cv2.imread(f'Pics/{num}.png')
        if img.any() or img.all():
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            if len(faces) >= 1 and faceDetection:
                # Draw a rectangle around the faces
                for (x, y, w, h) in faces:
                    if SMILEY_FACE and faceDetection:
                        d = int(w / 2)
                        # HEAD
                        cv2.circle(img, (int(x + w / 2), int(y + h / 2)), d, (red, green, blue), 2)
                        # MOUTH
                        roi_gray_mouth = gray[y+(int(h/2)):y+h, x:x+w]
                        roi_color_mouth = img[y+(int(h/2)):y+h, x:x+w]
                        mouth = mouth_cascade.detectMultiScale(roi_gray_mouth)
                        # EYES
                        roi_gray_eye = gray[y-(int(h/2)):y+h, x:x+w]
                        roi_color_eye = img[y-(int(h/2)):y+h, x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_gray_eye)
                        for (ex,ey,ew,eh) in eyes:
                            d = int(ew / 2)
                            cv2.circle(roi_color_eye, (int(ex + ew / 4) + int(d / 2), int(ey + eh / 4) + int(d / 2)), int(d) ,(blue,green,red),2)
                        for (ex,ey,ew,eh) in mouth: cv2.ellipse(roi_color_mouth, (int(ex + ew / 2), int(ey + eh / 8)), (int(ex), int(ey)), 0, 25, 155, (blue,green,red), 2)
                    else:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (red, green, blue), 2)
                img_cropped = cv2.imread(f'Pics/{num}.png')
                crop_img = img_cropped[y:y+h, x:x+w]
                cv2.putText(img, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (red, green, blue), 1)
                cv2.imwrite(f'Pics/{image_name}', img)
                if faceDetection: cv2.imwrite(f'Pics/{cropped_image_name}', crop_img)
                print('Image Processed')
                if faceDetection and SMILEY_FACE:           threading.Thread(target=email_picture, args=([image_name, cropped_image_name],f'Found {len(faces)} face/s!\n Found {len(eyes)} eye/s!\n Found {len(mouth)} mouth/s!',)).start()
                elif faceDetection and not SMILEY_FACE:     threading.Thread(target=email_picture, args=([image_name, cropped_image_name],f'Found {len(faces)} face/s!',)).start()
                elif not faceDetection and not SMILEY_FACE: threading.Thread(target=email_picture, args=([image_name, cropped_image_name],f'Motion detected!\n Found {len(faces)} face/s',)).start()
                elif not faceDetection and SMILEY_FACE:     threading.Thread(target=email_picture, args=([image_name, cropped_image_name],f'Motion detected!\n Found {len(faces)} face/s!\n Found {len(eyes)} eye/s!\n Found {len(mouth)} mouth/s!',)).start()
            elif not faceDetection:
                cv2.putText(img, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (red, green, blue), 1)
                cv2.imwrite(f'Pics/{image_name}', img)
                print('Image Processed')
                if faceDetection: threading.Thread(target=email_picture, args=([image_name, cropped_image_name],f'Motion detected!',)).start()
                else: threading.Thread(target=email_picture, args=([image_name],f'Motion detected!',)).start()
            print ("Found {0} faces!".format(len(faces)))
            print ("Found {0} eyes!".format(len(eyes)))
            print ("Found {0} mouths!".format(len(mouth)))
    except Exception as e: print(e)
def btnStop():
    if recording:
        makeVideo()
        clip = mp.VideoFileClip(video_name)
        clip_resized = clip.resize(height=260)
        clip_resized.write_videofile(os.path.dirname(os.path.realpath(__file__)) + "/output.mp4")
        os.remove(video_name)
        print("Deleted: {0}".format(video_name))
    removePictures()
    cap.release()
    cv2.destroyAllWindows()
    # sys.exit()
def camRun():
    global isRunning, cap, frame, ret, firstFrame
    global TIME, EMAIL_TIME, numOfPics, captureScreen, recording, email_pictures, SMILEY_FACE, SEND_EMAIL_DELAY, START_TIME, cascade, faceDetection
    global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, red, green, blue, face_detect
    isRunning = True
    for i, j in enumerate(cascade_files):
        if j == '/home/jared/Documents/Github Clones/Security-System/Data Models/haarcascade_eye.xml': eye_cascade = cv2.CascadeClassifier(cascade_files[i])
        if j == '/home/jared/Documents/Github Clones/Security-System/Data Models/haarcascade_smile.xml': mouth_cascade = cv2.CascadeClassifier(cascade_files[i])
    eyes = []
    mouth = []
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
    args = vars(ap.parse_args())
    # while True:
    ret, frame = cap.read()
    if faceDetection and isRunning:
        # Capture frame-by-frame
        text = "No face/s detected"
        if ret:
            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces in the image
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                text = f"Found {len(faces)} faces"
                if SMILEY_FACE:
                    d = int(w / 2)
                    # HEAD
                    cv2.circle(frame, (int(x + w / 2), int(y + h / 2)), d, (red, green, blue), 2)
                    # EYES
                    roi_gray_mouth = gray[y+(int(h/2)):y+h, x:x+w]
                    roi_color_mouth = frame[y+(int(h/2)):y+h, x:x+w]
                    roi_gray_eye = gray[y-(int(h/2)):y+h, x:x+w]
                    roi_color_eye = frame[y-(int(h/2)):y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(roi_gray_eye)
                    mouth = mouth_cascade.detectMultiScale(roi_gray_mouth)
                    for (ex,ey,ew,eh) in eyes:
                        d = int(ew / 2)
                        cv2.circle(roi_color_eye, (int(ex + ew / 4) + int(d / 2), int(ey + eh / 4) + int(d / 2)), int(d) ,(blue,green,red),2)
                    for (ex,ey,ew,eh) in mouth: cv2.ellipse(roi_color_mouth, (int(ex + ew / 2), int(ey + eh / 8)), (int(ex), int(ey)), 0, 25, 155, (blue,green,red), 2)
                else: cv2.rectangle(frame, (x, y), (x+w, y+h), (red, green, blue), 2)
            output.write(frame)
            if len(faces) >= 1: TIME = START_TIME
            TIME -= 0.2
            EMAIL_TIME += 0.2

            if TIME >= 0 and recording:
                numOfPics += 1
                savePicture(numOfPics)
            if EMAIL_TIME >= SEND_EMAIL_DELAY and len(faces) >= 1 and not recording and email_pictures and timeToSend:
                numOfPics += 1
                EMAIL_TIME = 0
                print(f'Found {len(faces)} faces! Pictures taken: {numOfPics}')
                savePicture(numOfPics)
                threading.Thread(target=findFaceInImage, args=(numOfPics,)).start()
            cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (red, green, blue), 1)
        if SMILEY_FACE: cv2.putText(frame, f"Found {len(faces)} face/s!  Found {len(eyes)} eye/s!  Found {len(mouth)} mouth/s!", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (red, green, blue), 1)
        else: cv2.putText(frame, "{}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (red, green, blue), 2)
    else:
        text = "No Movement"
        if frame is None: return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        if firstFrame is None: firstFrame = gray
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 7, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=4)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        for c in cnts:
            if cv2.contourArea(c) < args["min_area"]:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (red, green, blue), 2)
            text = "Movement"
            if len(cnts) >= 1: TIME = START_TIME
            TIME -= 0.2
            EMAIL_TIME += 0.2

            if TIME >= 0 and recording:
                numOfPics += 1
                savePicture(numOfPics)
            if EMAIL_TIME >= SEND_EMAIL_DELAY and len(cnts) >= 1 and not recording and email_pictures and timeToSend:
                numOfPics += 1
                EMAIL_TIME = 0
                print(f'Found {len(cnts)} faces! Pictures taken: {numOfPics}')
                savePicture(numOfPics)
                threading.Thread(target=findFaceInImage, args=(numOfPics,)).start()
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (red, green, blue), 2)
        cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (red, green, blue), 1)
        # show the frame and record if the user presses a key
        # cv2.imshow("Thresh", thresh)
        # cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"): return
        firstFrame = gray
        time.sleep(0.03)
    if isRunning == False: btnStop()
    if cv2.waitKey(1) & 0xFF == ord('q'): btnStop()
    if ret:
        return ret, frame
        # cv2.imshow('Camera', frame)
        # main.frame = frame
        # main.rets = ret
def exit_handler():
    print('Closing.. please wait.')
    btnStop()
def update_variables():
    while True:
        global TIME, EMAIL_TIME, currentTime, lastCurrentTime, numOfPics, captureScreen, recording, email_pictures, SMILEY_FACE, SEND_EMAIL_DELAY, START_TIME, cascade, faceDetection
        global saved_color, alwaysOnList, alwaysOn, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, red, green, blue, face_detect
        saved_color.clear()
        send_email.clear()
        cap_screen.clear()
        record_video.clear()
        smiley_face.clear()
        dark_mode.clear()
        email_delay.clear()
        picture_delay.clear()
        selected_data_index.clear()
        face_detect.clear()
        alwaysOnList.clear()
        with open(settings_file) as file:
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']: saved_color.append(color)
                for screen in info['capture screen']: cap_screen.append(screen)
                for video in info['record video']: record_video.append(video)
                for email in info['send email']: send_email.append(email)
                for smile in info['smiley face']: smiley_face.append(smile)
                for dark in info['dark mode']: dark_mode.append(dark)
                for email_d in info['email delay']: email_delay.append(email_d)
                for picture in info['picture delay']: picture_delay.append(picture)
                for ind in info['selected data index']: selected_data_index.append(ind)
                for face in info['face detect']: face_detect.append(face)
            with open(cycles_file) as file:
                cycles_json = json.load(file)
                for info in cycles_json:
                    for on in info['always on']: alwaysOnList.append(on)
            alwaysOn = (True if alwaysOnList[0] == "True" else False)
            currentTime = str(datetime.now().strftime("%I:%M%p"))
            if not currentTime in lastCurrentTime:
                lastCurrentTime = currentTime
                isTimeToSend()
            START_TIME = int(picture_delay[0])
            SEND_EMAIL_DELAY = int(email_delay[0])
            SMILEY_FACE = (True if smiley_face[0] == 'True' else False)
            captureScreen = (True if cap_screen[0] == 'True' else False)
            recording = (True if record_video[0] == 'True' else False)
            email_pictures = (True if send_email[0] == 'True' else False)
            faceDetection = (True if face_detect[0] == 'True' else False)
            cascade = cv2.CascadeClassifier(cascade_files[int(selected_data_index[0])])
            red, green, blue = int(saved_color[2]), int(saved_color[1]), int(saved_color[0])
        time.sleep(1)
def isTimeToSend():
    global timeToSend, cycles, OnToList, OnFromList, OffToList, OffFromList
    OnToList.clear()
    OnFromList.clear()
    OffToList.clear()
    OffFromList.clear()
    # currentTime = '03:17PM'
    print(list(currentTime))
    if list(currentTime[3]) == ['0']: currentTimeMinute = list(currentTime[4])
    elif not list(currentTime[3]) == ['0']: currentTimeMinute = list(currentTime[3]) + list(currentTime[4])
    if list(currentTime[0]) == ['0']: currentTimeHour = list(currentTime[1])
    elif not list(currentTime[0]) == ['0']: currentTimeHour = list(currentTime[0]) + list(currentTime[1])
    
    currentTimeDay = list(currentTime[-2])
    currentTimeDay = "".join(currentTimeDay)
    
    currentTimeHour = "".join(currentTimeHour)
    if currentTimeDay == 'P':
        currentTimeHour = int(currentTimeHour)
        currentTimeHour += 12
    currentTimeMinute = "".join(currentTimeMinute)
    
    print("currentTimeHour: " + str(currentTimeHour) + ':' + str(currentTimeMinute))
    with open(cycles_file) as file:
        cycles_json = json.load(file)
        for info in cycles_json:
            for c in info['cycles']: cycles = int(c)
            for OnTo in info['OnTo']: OnToList.append(OnTo)
            for OnFrom in info['OnFrom']: OnFromList.append(OnFrom)
            for OffTo in info['OffTo']: OffToList.append(OffTo)
            for OffFrom in info['OffFrom']: OffFromList.append(OffFrom)
    if not alwaysOn:
        for i in range(cycles):
            
            if OnToList[i][0] == '0': OnToNumHour = OnToList[i][1]
            else: OnToNumHour = str(OnToList[i][0] + OnToList[i][1])
            if OnFromList[i][0] == '0': OnFromNumHour = (OnFromList[i][1])
            else: OnFromNumHour = str(OnFromList[i][0] + OnFromList[i][1])
            OnToNumHour = "".join(OnToNumHour)
            OnFromNumHour = "".join(OnFromNumHour)
            
            if OnToList[i][3] == '0': OnToNumMinute = OnToList[i][4]
            else: OnToNumMinute = str(OnToList[i][3] + OnToList[i][4])
            if OnFromList[i][3] == '0': OnFromNumMinute = (OnFromList[i][4])
            else: OnFromNumMinute = str(OnFromList[i][3] + OnFromList[i][4])
            OnToNumMinute = "".join(OnToNumMinute)
            OnFromNumMinute = "".join(OnFromNumMinute)
            
            if OffToList[i][0] == '0': OffToNumHour = OffToList[i][1]
            else: OffToNumHour = str(OffToList[i][0] + OffToList[i][1])
            if OffFromList[i][0] == '0': OffFromNumHour = (OffFromList[i][1])
            else: OffFromNumHour = str(OffFromList[i][0] + OffFromList[i][1])
            OffToNumHour = "".join(OffToNumHour)
            OffFromNumHour = "".join(OffFromNumHour)

            if OffToList[i][3] == '0': OffToNumMinute = OffToList[i][4]
            else: OffToNumMinute = str(OffToList[i][3] + OffToList[i][4])
            if OffFromList[i][3] == '0': OffFromNumMinute = (OffFromList[i][4])
            else: OffFromNumMinute = str(OffFromList[i][3] + OffFromList[i][4])
            OffToNumMinute = "".join(OffToNumMinute)
            OffFromNumMinute = "".join(OffFromNumMinute)
            
            if int(OnToNumHour) <= int(currentTimeHour) and int(OnFromNumHour) >= int(currentTimeHour):
                print ('HOUR On: OnToNumHour: ' + str(OnToNumHour) + ' <= currentTimeHour: ' + str(currentTimeHour) + ' and OnFromNumHour: ' + str(OnFromNumHour) + ' >= currentTimeHour: ' + str(currentTimeHour))
                if int(OnToNumMinute) <= int(currentTimeMinute):
                    timeToSend = True
                    print ('MINUTE On: OnTo: ' + str(OnToList[i]) + ' >= ' + "currentTimeHour: " + str(currentTimeHour) + ':' + str(currentTimeMinute))
                else:
                    if int(OnFromNumMinute) <= int(currentTimeMinute):
                        timeToSend = False
                        print ('MINUTE On: OnFromNumMinute: ' + str(OnFromNumMinute) + ' <= CurrentTimeMinute: ' + str(currentTimeMinute))
                    else:
                        timeToSend = True
                        print ('MINUTE On: OnFromNumMinute: ' + str(OnFromNumMinute) + ' >= CurrentTimeMinute: ' + str(currentTimeMinute))
                print(timeToSend)
                return
            if int(OffToNumHour) <= int(currentTimeHour) and int(OffFromNumHour) >= int(currentTimeHour):
                print ('HOUR Off: OffToNumHour: ' + str(OffToNumHour) + ' <= currentTimeHour: ' + str(currentTimeHour) + ' and OffFromNumHour: ' + str(OffFromNumHour) + ' >= currentTimeHour: ' + str(currentTimeHour))
                if int(OffToNumMinute) <= int(currentTimeMinute):
                    timeToSend = False
                    print ('MINUTE Off: OffToNumMinute: ' + str(OffToNumMinute) + ' <= CurrentTimeMinute: ' + str(currentTimeMinute))
                else:
                    if int(OffFromNumMinute) <= int(currentTimeMinute):
                        timeToSend = True
                        print ('MINUTE Off: OffFromNumMinute: ' + str(OffFromNumMinute) + ' <= CurrentTimeMinute: ' + str(currentTimeMinute))
                    else:
                        timeToSend = False
                        print ('MINUTE Off: OffFromNumMinute: ' + str(OffFromNumMinute) + ' >= CurrentTimeMinute: ' + str(currentTimeMinute))
                print(timeToSend)
                return
        return
    else:
        timeToSend = True
        print(timeToSend)
        return
    
def start_cam():
    global isRunning
    isRunning = True
    atexit.register(exit_handler)
    threading.Thread(target = update_variables).start()
    # threading.Thread(target=camRun).start()
    # camRun()
def end_cam():
    global isRunning
    isRunning = False
    threading.Thread(target=btnStop).start()
    # btnStop()
