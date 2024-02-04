import base64

import cv2
import numpy as np
import requests
from fastapi import FastAPI

app = FastAPI()


@app.post("/receive_frame")
async def receive_frame(encoded_frame):
    # Decode the frame
    decoded_frame = base64.b64decode(encoded_frame)
    # Convert decoded image data to a NumPy array
    frame_data = np.frombuffer(decoded_frame, dtype=np.uint8)
    # Decode NumPy array to an OpenCV image
    frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

    # AI Process
    # ...

    # Annotate
    # Add text to the image
    text = "Hello, OpenCV!"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255)  # White
    font_thickness = 2
    text_position = (50, 50)  # (x, y) coordinates

    cv2.putText(frame, text, text_position, font, font_scale, font_color, font_thickness)

    # Send the processed frame to SP_IFRAME
    # send_frame(frame)


def send_frame(frame):
    # Encode image data to base64
    encoded_frame = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode('utf-8')

    # Send to SP_AI_FIGHT container
    url = f"http://sp_iframe:8000/receive_frame?encoded_frame={encoded_frame}"
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Successfully Sent")
    else:
        print(f"Error: {response.status_code}")
