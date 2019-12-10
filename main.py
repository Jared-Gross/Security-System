import cv2, mss, os, os.path, shutil, time, logging, threading, time, sys, atexit
from multiprocessing import Process
from os.path import isfile, join
from PIL import Image, ImageGrab
import moviepy.editor as mpq
from datetime import datetime
import natsort as nt
from datetime import datetime
from send_email import email_picture
from threading import Timer
# captureScreen = IntVar()
captureScreen = False
record_video = False
email_pictures = True

SMILEY_FACE = False

canvas_height=200
canvas_width=200
START_TIME = 5
SEND_EMAIL_DELAY = 10
TIME = 0
EMAIL_TIME = 0
cascadeLocationFolder = "Face Detection/"
cascadeLists = [
    "{0}haarcascade_frontalface_default.xml".format(cascadeLocationFolder),
    "{0}haarcascade_eye.xml".format(cascadeLocationFolder),
    "{0}haarcascade_fullbody.xml".format(cascadeLocationFolder)
]
selectedCascade = ""
image_folder = 'Face Detection/Pics'
video_name = 'temp.avi'
numOfPics = 0
cascade = cv2.CascadeClassifier(cascadeLists[0])
cap = cv2.VideoCapture(0)
vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter("cam_video.mp4", vid_cod, 17.0, (640,480))
TIME_LIMIT = 100
def removePictures():
    for the_file in os.listdir(image_folder):
        file_path = os.path.join(image_folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
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
        video = cv2.VideoWriter(video_name, 0, 10, (width, height))
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
    cropped_image_name = 'Cropped Image.png'
    image_name = 'Image.png'
    img = cv2.imread(f'Face Detection/Pics/{num}.png')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
    )
    print ("Found {0} faces!".format(len(faces)))

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    img_cropped = cv2.imread(f'Face Detection/Pics/{num}.png')
    crop_img = img_cropped[y:y+h, x:x+w]
    cv2.imwrite(f'Face Detection/Pics/{image_name}', img)
    cv2.imwrite(f'Face Detection/Pics/{cropped_image_name}', crop_img)
    threading.Thread(target=email_picture, args=([image_name, cropped_image_name],)).start()

def btnStop():
    if record_video:
        makeVideo()
        # When everything done, release the capture
        clip = mp.VideoFileClip(video_name)
        # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
        clip_resized = clip.resize(height=360)
        clip_resized.write_videofile("output.mp4")
        os.remove(video_name)
        print("Deleted: {0}".format(video_name))
    removePictures()
    cap.release()
    print('closed capture')
    cv2.destroyAllWindows()
    print('closed all windows')
    sys.exit()
def camRun():
    print("Starting..")
    global TIME, EMAIL_TIME
    while True:
        global numOfPics
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces in the image
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(30, 30)
            )
            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                if SMILEY_FACE:
                    d = int(w / 2)
                    # HEAD
                    cv2.circle(frame, (int(x + w / 2), int(y + h / 2)), d, (int(x), int(d / 2), int(w)), 2)
                    # LEFT EYE
                    cv2.circle(frame, (int(x + w / 4) + 5, int(y + h / 4) + 15), int(d / 4), (int(x), int(d / 2), int(w)), 2)
                    # RIGHT EYE
                    cv2.circle(frame, (int(x + w / 1.5) + 5, int(y + h / 4) + 15), int(d / 4), (int(x), int(d / 2), int(w)), 2)
                    # LIPS
                    cv2.ellipse(frame, (int(x + w / 2), int(y + h / 1.9)), (int(w / 3), int(w / 3)), 0, 25, 155, (int(x), int(d / 2), int(w)), 2)
                else:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # Display the resulting frame
            cv2.imshow('Camera', frame)
            output.write(frame)

            # If theres a face detected then save a picture of it
            if len(faces) >= 1:
                TIME = START_TIME
            TIME -= 0.2
            EMAIL_TIME += 0.2

            if TIME >= 0 and record_video:
                numOfPics += 1
                savePicture(numOfPics)
            if EMAIL_TIME >= SEND_EMAIL_DELAY and len(faces) >= 1 and not record_video and email_pictures:
                numOfPics += 1
                EMAIL_TIME = 0
                print(f'Found {len(faces)} faces! Pictures taken: {numOfPics}')
                savePicture(numOfPics)
                PROCESS_IMAGE = threading.Thread(target=findFaceInImage, args=(numOfPics,))
                PROCESS_IMAGE.start()
                # WAIT FOR PROCCESS TO FINISH:
                # PROCESS_IMAGE.join()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            btnStop()
def exit_handler():
    print('Closing.. please wait.')
    btnStop()

if __name__ == '__main__':
    atexit.register(exit_handler)
    # START_CAMERA = threading.Thread(target=camRun).start()
    START_CAMERA = Process(target=camRun).start()
