import base64
import pickle

import cv2
import requests
from fastapi import FastAPI

app = FastAPI()


@app.get("/receive_frame")
async def receive_frame(video_source: str):
    cap = cv2.VideoCapture(video_source)
    ret, frame = cap.read()

    # _, img_buffer = cv2.imencode('.jpg', frame)
    # img_b64 = base64.b64encode(img_buffer).decode('utf-8')

    data_to_send = pickle.dumps(frame)

    # return data_to_send
    send_frame(data_to_send)


def send_frame(frame):
    # Convert frame to Base64
    # _, img_buffer = cv2.imencode('.jpg', frame)
    # img_b64 = base64.b64encode(img_buffer).decode('utf-8')

    # Send Base64-encoded frame to sp_ai FastAPI service
    url = 'http://127.0.0.1:8002/receive_frame'
    payload = {'encoded_frame': frame}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print("Frame processed successfully by sp_ai")
        else:
            print(f"Error processing frame. Status code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request to sp_ai failed: {e}")
