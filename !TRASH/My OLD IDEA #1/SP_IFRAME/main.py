import base64

import cv2
import numpy as np
from fastapi import FastAPI

app = FastAPI()


@app.get("/receive_frame")
def receive_frame(encoded_frame):
    # Decode the frame
    decoded_frame = base64.b64decode(encoded_frame)
    # Convert decoded image data to a NumPy array
    frame_data = np.frombuffer(decoded_frame, dtype=np.uint8)
    # Decode NumPy array to an OpenCV image
    frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

    print(f"Received Frame : {len(frame)}")

    # Send to browser
    # ...
