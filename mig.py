import socket
import struct
import errno
import csv
import cv2
import os
import numpy as np
from datetime import datetime, timedelta, timezone

# General config
UDP_IP = "10.42.57.126"
UDP_PORT = 8888
MESSAGE_LENGTH = 13  # one sensor data frame has 13 bytes
BASE_FOLDER_PATH = r'C:\Users\falcon\Desktop\iitm\bravo\Sync\jag\Formal_it'
ACCEL_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, '1. Accelerations')
PICS_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, 'pics')

# Define IST (Indian Standard Time) timezone
IST = timezone(timedelta(hours=5, minutes=30))

# Prepare UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)
sock.bind((UDP_IP, UDP_PORT))

def accel_fit(x_input, m_x, b):
    return (m_x * x_input) + b  # fit equation for accel calibration

def get_accel():
    try:
        data, fromAddr = sock.recvfrom(MESSAGE_LENGTH)
        if data:
            x = struct.unpack_from('<f', data, 1)[0]
            y = struct.unpack_from('<f', data, 5)[0]
            z = struct.unpack_from('<f', data, 9)[0]
            return x, y, z
    except socket.error as why:
        if why.args[0] == errno.EWOULDBLOCK:
            return None
        else:
            raise why

# Load calibration coefficients
accel_coeffs = np.load('calibration_coeffs.npy')

# Create the accelerations folder if it doesn't exist
if not os.path.exists(ACCEL_FOLDER_PATH):
    os.makedirs(ACCEL_FOLDER_PATH)

# Create the pictures folder if it doesn't exist
if not os.path.exists(PICS_FOLDER_PATH):
    os.makedirs(PICS_FOLDER_PATH)

# Initialize camera using the phone's camera stream URL
cap = cv2.VideoCapture(0)

# List to hold acceleration data
accel_data_list = []

# Read data forever until user decides to stop
print("Press Ctrl+C to stop data collection.")
try:
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

            # Apply calibration
            x_cal = accel_fit(x, *accel_coeffs[0])
            y_cal = accel_fit(y, *accel_coeffs[1])
            z_cal = accel_fit(z, *accel_coeffs[2])

            # Capture frame from camera
            ret, frame = cap.read()
            if ret:
                # Save frame with timestamp as filename
                frame_name = timestamp_ist.replace(':', '-') + '.jpg'
                frame_path = os.path.join(PICS_FOLDER_PATH, frame_name)
                cv2.imwrite(frame_path, frame)

                # Append data to list
                accel_data_list.append([timestamp_ist, x_cal, y_cal, z_cal, frame_name])
                print("Collected data:", timestamp_ist, x_cal, y_cal, z_cal, frame_name)

except KeyboardInterrupt:
    # Stop the collection and save data
    stop_time = datetime.now(IST).strftime('%Y-%m-%d %H-%M-%S')
    accel_file_name = f'accel_data_{stop_time}.csv'
    accel_file_path = os.path.join(ACCEL_FOLDER_PATH, accel_file_name)
    
    # Write data to CSV file
    with open(accel_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp (IST)', 'X', 'Y', 'Z', 'Frame Name'])  # Write header row
        writer.writerows(accel_data_list)
    
    print(f"Data collection stopped. Data saved to {accel_file_path}")

# Release camera
cap.release()
