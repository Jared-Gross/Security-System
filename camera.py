import cv2, mss, os, os.path, shutil, time, logging, threading, time, sys, atexit, json
from multiprocessing import Process
from os.path import isfile, join
from PIL import Image, ImageGrab
import moviepy.editor as mp
from datetime import datetime
import natsort as nt
from datetime import datetime
from send_email import email_picture
from threading import Timer
import Controll_Panel
# captureScreen = IntVar()
captureScreen = False
recording = False
email_pictures = True

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
        if '.xml' in file:
            cascade_files.append(os.path.join(r, file))

settings_file = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
settings_json = []

saved_color = []
send_email = []
cap_screen = []
record_video = []
smiley_face = []
dark_mode = []

email_delay = []
picture_delay = []
selected_data_index = []

red, green, blue = 0, 0, 0

image_folder = 'Face Detection/Pics'
video_name = os.path.dirname(os.path.realpath(__file__)) + '/temp.avi'
numOfPics = 0
cascade = cv2.CascadeClassifier(cascade_files[0])
cap = cv2.VideoCapture(0)
vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter(os.path.dirname(os.path.realpath(__file__)) + "/cam_video.mp4", vid_cod, 17, (640,480))
TIME_LIMIT = 100
def removePictures():
    for the_file in os.listdir(image_folder):
        file_path = os.path.join(image_folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
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
        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))
        video.release()
        print(len(images))
def savePicture(num):
    if not captureScreen:
        # CAPTURE WEBCAM
        return_value, image = cap.read()
        cv2.imwrite("Face Detection/Pics/{0}.png".format(num),image)
    else:
        # CAPTURE SCREEN
        with mss.mss() as sct:
            filename = sct.shot(output=f'Face Detection/Pics/{num}.png')
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
    with open(settings_file) as file:
        settings_json = json.load(file)
        for info in settings_json:
            for color in info['saved color']:
                saved_color.append(color)
            for screen in info['capture screen']:
                cap_screen.append(screen)
            for video in info['record video']:
                record_video.append(video)
            for email in info['send email']:
                send_email.append(email)
            for smile in info['smiley face']:
                smiley_face.append(smile)
            for dark in info['dark mode']:
                dark_mode.append(dark)
            for email_d in info['email delay']:
                email_delay.append(email_d)
            for picture in info['picture delay']:
                picture_delay.append(picture)
            for ind in info['selected data index']:
                selected_data_index.append(ind)
    print("Starting..")
    print(isRunning)
    START_TIME = int(picture_delay[0])
    SEND_EMAIL_DELAY = int(email_delay[0])
    SMILEY_FACE = (True if smiley_face[0] == 'True' else False)
    captureScreen = (True if cap_screen[0] == 'True' else False)
    recording = (True if record_video[0] == 'True' else False)
    email_pictures = (True if send_email[0] == 'True' else False)
    print(cascade_files[selected_data_index[0]])
    cascade = cv2.CascadeClassifier(cascade_files[selected_data_index[0]])
    eye_cascade = cv2.CascadeClassifier(cascade_files[0])
    mouth_cascade = cv2.CascadeClassifier(cascade_files[17])
    red, green, blue = int(saved_color[2]), int(saved_color[1]), int(saved_color[0])
    try:
        cropped_image_name = 'Cropped Image.png'
        image_name = 'Image.png'
        img = cv2.imread(f'Face Detection/Pics/{num}.png')
        if img.any() or img.all():
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            if len(faces) >= 1:
                # Draw a rectangle around the faces
                for (x, y, w, h) in faces:
                    if SMILEY_FACE:
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
                        for (ex,ey,ew,eh) in mouth:
                            cv2.ellipse(roi_color_mouth, (int(ex + ew / 2), int(ey + eh / 2)), (int(ew / 3), int(ew / 12)), 0, 25, 155, (blue,green,red), 2)
                    else:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (red, green, blue), 2)
                img_cropped = cv2.imread(f'Face Detection/Pics/{num}.png')
                crop_img = img_cropped[y:y+h, x:x+w]
                cv2.imwrite(f'Face Detection/Pics/{image_name}', img)
                cv2.imwrite(f'Face Detection/Pics/{cropped_image_name}', crop_img)
                print('Image Processed')
                threading.Thread(target=email_picture, args=([image_name, cropped_image_name],)).start()
            print ("Found {0} faces!".format(len(faces)))
            print ("Found {0} eyes!".format(len(eyes)))
            print ("Found {0} mouths!".format(len(mouth)))
    except Exception as e:
        print(e)
def btnStop():
    if recording:
        makeVideo()
        # When everything done, release the capture
        clip = mp.VideoFileClip(video_name)
        # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
        clip_resized = clip.resize(height=360)
        clip_resized.write_videofile(os.path.dirname(os.path.realpath(__file__)) + "/output.mp4")
        os.remove(video_name)
        print("Deleted: {0}".format(video_name))
    removePictures()
    cap.release()
    cv2.destroyAllWindows()
    # sys.exit()
def camRun():
    global TIME, EMAIL_TIME, numOfPics, captureScreen, recording, email_pictures, SMILEY_FACE, SEND_EMAIL_DELAY, START_TIME, cascade
    global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, red, green, blue
    print("Starting..")
    threading.Thread(target = update_variables).start()
    eye_cascade = cv2.CascadeClassifier(cascade_files[0])
    mouth_cascade = cv2.CascadeClassifier(cascade_files[17])
    while isRunning:
        # Capture frame-by-frame
        ret, frame = cap.read()
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
                    for (ex,ey,ew,eh) in mouth:
                        # LIPS
                        cv2.ellipse(roi_color_mouth, (int(ex + ew / 2), int(ey + eh / 2)), (int(ew / 3), int(ew / 12)), 0, 25, 155, (blue,green,red), 2)
                else:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (red, green, blue), 2)
            # Display the resulting frame
            cv2.imshow('Camera', frame)
            output.write(frame)

            # If theres a face detected then save a picture of it
            if len(faces) >= 1:
                TIME = START_TIME
            TIME -= 0.2
            EMAIL_TIME += 0.2

            if TIME >= 0 and recording:
                numOfPics += 1
                savePicture(numOfPics)
            if EMAIL_TIME >= SEND_EMAIL_DELAY and len(faces) >= 1 and not recording and email_pictures:
                numOfPics += 1
                EMAIL_TIME = 0
                print(f'Found {len(faces)} faces! Pictures taken: {numOfPics}')
                savePicture(numOfPics)
                PROCESS_IMAGE = threading.Thread(target=findFaceInImage, args=(numOfPics,))
                PROCESS_IMAGE.start()
                # WAIT FOR PROCCESS TO FINISH:
                # PROCESS_IMAGE.join()

        if isRunning == False:
            cap.release()
            cv2.destroyAllWindows()
            print('Quit by isRunning')
            # break
            btnStop()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            btnStop()
def exit_handler():
    print('Closing.. please wait.')
    btnStop()
def update_variables():
    while isRunning:
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
        selected_data_index.clear()
        with open(settings_file) as file:
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email in info['send email']:
                    send_email.append(email)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
            START_TIME = int(picture_delay[0])
            SEND_EMAIL_DELAY = int(email_delay[0])
            SMILEY_FACE = (True if smiley_face[0] == 'True' else False)
            captureScreen = (True if cap_screen[0] == 'True' else False)
            recording = (True if record_video[0] == 'True' else False)
            email_pictures = (True if send_email[0] == 'True' else False)
            cascade = cv2.CascadeClassifier(cascade_files[int(selected_data_index[0])])
            # print(cascade_files[int(selected_data_index[0])])
            red, green, blue = int(saved_color[2]), int(saved_color[1]), int(saved_color[0])
            time.sleep(1)
def start_cam():
    global isRunning, cap
    cap = cv2.VideoCapture(0)
    isRunning = True
    print('start_cam')
    print(f'is Running:{isRunning}')
    atexit.register(exit_handler)
    # START_CAMERA = threading.Thread(target=camRun).start()
    # Process(target=camRun).start()
    camRun()
def end_cam():
    global isRunning
    isRunning = False
    print('End_cam')
    print(f'is Running:{isRunning}')
    btnStop()
