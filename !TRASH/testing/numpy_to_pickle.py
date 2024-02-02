import cv2
import pickle

cap = cv2.VideoCapture("../../SAMPLE/wallpaper-bishop.jpg")
ret, frame = cap.read()

# Sender side
data_to_send = pickle.dumps(frame)
# send data_to_send over the network

# print("DATA TO SEND")
# print(data_to_send)

# Receiver side
received_data = data_to_send  # receive data over the network
numpy_array_received = pickle.loads(received_data)

print("NUMPY ARRAY RECEIVED")
print(numpy_array_received)
