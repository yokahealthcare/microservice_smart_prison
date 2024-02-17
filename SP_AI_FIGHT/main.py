import os
import threading
import time

import cv2
import imutils
import torch
from flask import Flask, request, redirect
from flask import Response
from dotenv import load_dotenv
import requests

import fight_module

# Load environment variable
load_dotenv()

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__)


@app.route("/")
def index():
    return "This is testing page. It tell you this is working :)"


@app.route("/gpu")
def gpu():
    gpu_info = ""
    if torch.cuda.is_available():
        gpu_info += "CUDA is available. Showing GPU information:\n"
        for i in range(torch.cuda.device_count()):
            gpu = torch.cuda.get_device_properties(i)
            gpu_info += f"> GPU {i} - {gpu.name}\n"

    return f"\n{gpu_info}\n"


@app.route("/raw")
def raw():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/start")
def start():
    video_input = request.args.get("video_input")

    # Start a thread that will perform motion detection
    t = threading.Thread(target=detect, args=(video_input,))
    t.daemon = True
    t.start()

    return redirect("/raw")


def detect(video_input):
    # grab global references to the video stream, output frame, and
    # lock variables
    global outputFrame, lock
    YOLO_MODEL = os.getenv("YOLO_MODEL")
    FIGHT_MODEL = os.getenv("FIGHT_MODEL")
    FIGHT_ON = False
    FIGHT_ON_THRESHOLD = int(os.getenv("FIGHT_ON_THRESHOLD"))
    FIGHT_ON_TIMEOUT = int(os.getenv("FIGHT_ON_TIMEOUT"))  # seconds
    # Initialize the time when the fight flag was last set
    FIGHT_FLAG_LAST_TIME = None

    fdet = fight_module.FightDetector(FIGHT_MODEL)
    yolo = fight_module.YoloPoseEstimation(YOLO_MODEL)

    # Open a video source (provide the video path)
    cap = cv2.VideoCapture(video_input)

    while True:
        # Read a frame from the video source
        ret, frame = cap.read()
        # Check if the frame is successfully read
        if not ret:
            print("Error: Failed to read frame.")
            break

        h, w = frame.shape[0], frame.shape[1]
        if h > 720:
            frame = imutils.resize(frame, width=1280)

        result = yolo.estimate(frame)[0]

        try:
            boxes = result.boxes.xyxy.tolist()
            xyn = result.keypoints.xyn.tolist()
            confs = result.keypoints.conf
            confs = [] if confs is None else confs.tolist()

            # Processing interaction box
            interaction_boxes = fight_module.get_interaction_box(boxes, xyn, confs)

            # Initialize a counter for people inside the interaction box
            for inter_box, num_person, xyn_group, conf_group in interaction_boxes:
                cv2.rectangle(frame, (int(inter_box[0]), int(inter_box[1])), (int(inter_box[2]), int(inter_box[3])),
                              (0, 255, 0), 2)

                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 0.3
                color = (255, 255, 255)
                thickness = 1
                cv2.putText(frame, f"SUBJECT : {num_person}", (int(inter_box[0]) + 10, int(inter_box[3]) - 10), font,
                            fontScale, color, thickness)

                if num_person >= 2:
                    both_fighting = []
                    for xyn, conf in zip(xyn_group, conf_group):
                        is_it_fighting = fdet.detect(conf, xyn)
                        both_fighting.append(is_it_fighting)

                    if all(both_fighting) and not FIGHT_ON:
                        # Decrease by 1 if it detected the valid fight
                        FIGHT_ON_THRESHOLD -= 1
                        if FIGHT_ON_THRESHOLD == 0:
                            # Set the fight flag and update the time when it was last set
                            FIGHT_ON = True
                            FIGHT_FLAG_LAST_TIME = time.time()
                            FIGHT_ON_THRESHOLD = int(os.getenv("FIGHT_ON_THRESHOLD"))

        except TypeError as te:
            pass
        except IndexError as ie:
            pass
        # Check if the fight flag was set more than FIGHT_ON_TIMEOUT seconds ago
        if FIGHT_ON and time.time() - FIGHT_FLAG_LAST_TIME > FIGHT_ON_TIMEOUT:
            FIGHT_ON = False
            # Start process on VOD container
            url = 'http://data/'
            response = requests.get(url)

        # RING THE ALARM
        if FIGHT_ON:
            cv2.putText(frame, "FIGHTING", (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

            countdown = FIGHT_ON_TIMEOUT - int(time.time() - FIGHT_FLAG_LAST_TIME)
            cv2.putText(frame, f"{countdown} seconds to alarm termination", (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 0), 1, cv2.LINE_AA)

            # Write to outgoing_frame folder
            cv2.imwrite("outgoing_frame/", frame)

        # acquire the lock, set the output frame, and release the lock
        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    while True:
        # check if the output frame is available, otherwise skip
        # the iteration of the loop
        if outputFrame is None:
            continue

        # encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
        # ensure the frame was successfully encoded
        if not flag:
            continue

        # yield the output frame in the byte format
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'


# check to see if this is the main thread of execution
if __name__ == '__main__':
    """
        host : 0.0.0.0 
        - this is a must, cannot be changed to 127.0.0.1 
        - or it will cannot be accessed after been forwarded by docker to host IP
        
        port : 80 (up to you)
    """
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True, use_reloader=False)
