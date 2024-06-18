import socket
import json
import csv
import os

def listen_on_udp(ip, port, file_path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ip, port)
    sock.bind(server_address)
    
    print(f"Listening on UDP {ip}:{port}...")

    while True:
        data, address = sock.recvfrom(4096)
        
        try:
            json_data = json.loads(data.decode('utf-8'))
            print(f"Received JSON data from {address}: {json_data}")
            
            with open(file_path, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'acceleration_x', 'acceleration_y', 'acceleration_z']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                acceleration_x = json_data.get('accelX', 0)
                acceleration_y = json_data.get('accelY', 0)
                acceleration_z = json_data.get('accelZ', 0)
                timestamp = json_data.get('accelTime', 0)
                
                writer.writerow({'timestamp': timestamp, 'acceleration_x': acceleration_x, 'acceleration_y': acceleration_y, 'acceleration_z': acceleration_z})
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON data: {e}")

if __name__ == "__main__":
    UDP_IP = "ur-ip"  
    UDP_PORT = 8888          
    FILE_PATH = r"ur-path"
    
    with open(FILE_PATH, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'acceleration_x', 'acceleration_y', 'acceleration_z']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
    listen_on_udp(UDP_IP, UDP_PORT, FILE_PATH)
