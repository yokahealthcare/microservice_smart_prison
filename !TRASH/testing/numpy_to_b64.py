import sys
import base64

import cv2
import numpy as np

cap = cv2.VideoCapture("../../SAMPLE/wallpaper-bishop.jpg")
ret, frame = cap.read()

_, img_buffer = cv2.imencode('.jpg', frame)
img_b64 = base64.b64encode(img_buffer).decode('utf-8')

print("Image BASE64 Data")
print(len(img_b64))
print(sys.getsizeof(img_b64))

# Decode the frame
decoded_frame = base64.b64decode(img_b64)
# Convert decoded image data to a NumPy array
frame_data = np.frombuffer(decoded_frame, dtype=np.uint8)
# Decode NumPy array to an OpenCV image
frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

# cv2.imshow("webcam", frame)
print(frame)
print(frame.shape)


print(img_b64)
input("kkk")
