import os
import subprocess

def run_calibration():
    print("Running calibration script...")
    subprocess.run(["python", "calib.py"])

def run_data_collection():
    print("Running data collection script...")
    subprocess.run(["python", "mig.py"])
    

def run_data_collection_without_calib():
    print("Running data collection script_without clib...")
    subprocess.run(["python", "sockets.py"])

def run_analysis():
    print("Running analysis script...")
    subprocess.run(["python", "sukhoi.py"])

if __name__ == "__main__":
    while True:
        choice = input("Enter 'c' to calibrate, 'd' to collect data with calib, 'dw' to collect data without calib, 'a' to run analysis, or 'q' to quit: ").lower()
        if choice == 'c':
            run_calibration()
        elif choice == 'd':
            run_data_collection()
        elif choice == 'a':
            run_analysis()
        elif choice == 'dw':    
            run_data_collection_without_calib()
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please enter 'c', 'd', 'a', or 'q'.")
