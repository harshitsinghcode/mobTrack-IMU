import socket
import struct
import csv
import errno
import cv2
import os
from datetime import datetime, timedelta, timezone

UDP_IP = ""
UDP_PORT = 8888
MESSAGE_LENGTH = 13  
BASE_FOLDER_PATH = r'your-path'
ACCEL_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, '1. Accelerations')
PICS_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, 'pics')

IST = timezone(timedelta(hours=5, minutes=30))

if not os.path.exists(ACCEL_FOLDER_PATH):
    os.makedirs(ACCEL_FOLDER_PATH)
if not os.path.exists(PICS_FOLDER_PATH):
    os.makedirs(PICS_FOLDER_PATH)

print("This PC's IP: ", UDP_IP)
print("Listening on Port: ", UDP_PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)
sock.bind((UDP_IP, UDP_PORT))

cap = cv2.VideoCapture(0)

try:
    while True:
        # Create a new CSV file for each iteration
        timestamp_now = datetime.now(IST).strftime('%Y-%m-%d_%H-%M-%S')
        csv_file_path = os.path.join(ACCEL_FOLDER_PATH, f'accelerometer_data_{timestamp_now}.csv')

        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp (IST)', 'X', 'Y', 'Z', 'Frame Name'])  

            print(f"Started new iteration, saving to {csv_file_path}")
            
            while True:
                newestData = None
                while True:
                    try:
                        data, fromAddr = sock.recvfrom(MESSAGE_LENGTH)
                        if data:
                            newestData = data
                    except socket.error as why:
                        if why.args[0] == errno.EWOULDBLOCK:
                            break
                        else:
                            raise why

                if newestData is not None:
                    timestamp_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                    x = struct.unpack_from('<f', newestData, 1)[0]
                    y = struct.unpack_from('<f', newestData, 5)[0]
                    z = struct.unpack_from('<f', newestData, 9)[0]

                    # Capture frame from camera
                    ret, frame = cap.read()
                    if ret:
                        # Save frame with timestamp as filename
                        frame_name = timestamp_ist.replace(':', '-') + '.jpg'
                        frame_path = os.path.join(PICS_FOLDER_PATH, frame_name)
                        cv2.imwrite(frame_path, frame)

                        # Write data to CSV
                        writer.writerow([timestamp_ist, x, y, z, frame_name])
                        print("Received data:", timestamp_ist, x, y, z, frame_name)
except KeyboardInterrupt:
    print("\nData collection stopped.")

# Release camera
cap.release()
