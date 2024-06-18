import os
import pandas as pd
import numpy as np
from scipy.integrate import cumtrapz
from scipy.signal import butter, sosfiltfilt
import matplotlib.pyplot as plt
import glob
import time

BASE_FOLDER_PATH = r'ur-path'
ACCEL_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, '1. Accelerations')
VEL_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, '2. Velocities')
POS_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, '3. Positions')

for folder_path in [VEL_FOLDER_PATH, POS_FOLDER_PATH]:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# i used sos (second-order-sections) cuz it provides numerical stability
# Butterworth filter functions
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    sos = butter(order, normal_cutoff, btype='low', analog=False, output='sos')
    return sos

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    sos = butter(order, normal_cutoff, btype='high', analog=False, output='sos')
    return sos

def sos_filter(data, sos):
    y = sosfiltfilt(sos, data)
    return y

def process_acceleration_data(acceleration_file):
    acceleration_data = pd.read_csv(acceleration_file)

    required_columns = ['Timestamp (IST)', 'X', 'Y', 'Z']
    for col in required_columns:
        if col not in acceleration_data.columns:
            raise ValueError(f"Missing column: {col}")

    timestamps = pd.to_datetime(acceleration_data['Timestamp (IST)'])
    acc_x = acceleration_data['X'].values
    acc_y = acceleration_data['Y'].values
    acc_z = acceleration_data['Z'].values

    time_sec = (timestamps - timestamps.iloc[0]).dt.total_seconds().values

    # Filtering parameters - i got the most accurate value for a 5-m pre-measured distance
    fs = 20.0  
    low_cutoff = 6.90
    high_cutoff = 2.5

    # Butterworth filter
    lowpass_sos = butter_lowpass(low_cutoff, fs)
    highpass_sos = butter_highpass(high_cutoff, fs)

    # Low-pass filter to remove noise
    acc_x_low = sos_filter(acc_x, lowpass_sos)
    acc_y_low = sos_filter(acc_y, lowpass_sos)
    acc_z_low = sos_filter(acc_z, lowpass_sos)

    # High-pass filter to remove drift
    acc_x_filtered = sos_filter(acc_x_low, highpass_sos)
    acc_y_filtered = sos_filter(acc_y_low, highpass_sos)
    acc_z_filtered = sos_filter(acc_z_low, highpass_sos)

    # Calculate velocities
    vel_x = cumtrapz(acc_x_filtered, time_sec, initial=0)
    vel_y = cumtrapz(acc_y_filtered, time_sec, initial=0)
    vel_z = cumtrapz(acc_z_filtered, time_sec, initial=0)

    # Calculate positions
    pos_x = cumtrapz(vel_x, time_sec, initial=0)
    pos_y = cumtrapz(vel_y, time_sec, initial=0)
    pos_z = cumtrapz(vel_z, time_sec, initial=0)

    # High-pass filter to remove drift from positions
    pos_x_filtered = sos_filter(pos_x, highpass_sos)
    pos_y_filtered = sos_filter(pos_y, highpass_sos)
    pos_z_filtered = sos_filter(pos_z, highpass_sos)

    return timestamps, vel_x, vel_y, vel_z, pos_x_filtered, pos_y_filtered, pos_z_filtered

def plot_position_data(timestamps, pos_x_filtered, pos_y_filtered, pos_z_filtered):
    # Plot the filtered position data
    plt.figure()
    plt.plot(timestamps, pos_x_filtered, label='X Position')
    plt.plot(timestamps, pos_y_filtered, label='Y Position')
    plt.plot(timestamps, pos_z_filtered, label='Z Position')
    plt.xlabel('Time')
    plt.ylabel('Position (m)')
    plt.legend()
    plt.title(f'Filtered Position Data')
    plt.show()

def save_position_data(timestamps, pos_x_filtered, pos_y_filtered, pos_z_filtered, total_distance):
    filename = f"position_data_{total_distance:.2f}_meters.csv"
    output_file_path = os.path.join(POS_FOLDER_PATH, filename)

    filtered_position_data = pd.DataFrame({
        'Timestamp (IST)': timestamps,
        'Filtered_Pos_X': pos_x_filtered,
        'Filtered_Pos_Y': pos_y_filtered,
        'Filtered_Pos_Z': pos_z_filtered
    })
    filtered_position_data.to_csv(output_file_path, index=False)
    print(f"Position data saved to {output_file_path}")

def save_velocity_data(timestamps, vel_x, vel_y, vel_z):
    current_time = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"velocity_data_{current_time}.csv"
    output_file_path = os.path.join(VEL_FOLDER_PATH, filename)

    # Save velocity data
    velocity_data = pd.DataFrame({
        'Timestamp (IST)': timestamps,
        'Vel_X': vel_x,
        'Vel_Y': vel_y,
        'Vel_Z': vel_z
    })
    velocity_data.to_csv(output_file_path, index=False)
    print(f"Velocity data saved to {output_file_path}")
    
def main():

    while True:
            # Get the most recent acceleration file
            latest_acceleration_file = max(glob.glob(os.path.join(ACCEL_FOLDER_PATH, '*.csv')), key=os.path.getctime)

            # Process acceleration data
            timestamps, vel_x, vel_y, vel_z, pos_x_filtered, pos_y_filtered, pos_z_filtered = process_acceleration_data(latest_acceleration_file)

            # Plot position data
            plot_position_data(timestamps, pos_x_filtered, pos_y_filtered, pos_z_filtered)

            # Calculate total distance covered
            total_distance = np.sum(np.sqrt(np.diff(pos_x_filtered)**2 + np.diff(pos_y_filtered)**2 + np.diff(pos_z_filtered)**2))
            print(f"Total distance covered: {total_distance:.2f} meters")

            # Save position data
            save_position_data(timestamps, pos_x_filtered, pos_y_filtered, pos_z_filtered, total_distance)

            # Save velocity data
            save_velocity_data(timestamps, vel_x, vel_y, vel_z)

            break  # End the while loop after latest file

if __name__ == "__main__":
    main()
