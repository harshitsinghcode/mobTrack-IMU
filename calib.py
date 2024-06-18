#falcon-init
import socket
import struct
import errno
import numpy as np
from scipy.optimize import curve_fit
import time

UDP_IP = "ip-address"
UDP_PORT = 8888 
MESSAGE_LENGTH = 13 #one imu-sensor has 13 bytes


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)
sock.bind((UDP_IP, UDP_PORT))

def accel_fit(x_input, m_x, b):
    return (m_x * x_input) + b  

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

def accel_cal():
    print("-" * 50)
    print("Accelerometer Calibration")
    mpu_offsets = [[], [], []]  # offset array 
    axis_vec = ['z', 'y', 'x']  # axis labels
    cal_directions = ["upward", "downward", "perpendicular to gravity"]  
    cal_indices = [2, 1, 0]  # axis indices
    cal_size = 1000  # number of points to use for calibration- again it depends on you(;

    for qq, ax_qq in enumerate(axis_vec):
        ax_offsets = [[], [], []]
        print("-" * 50)
        for direc_ii, direc in enumerate(cal_directions):
            input("-" * 8 + f" Press Enter and Keep IMU Steady to Calibrate the Accelerometer with the {ax_qq}-axis pointed {direc}")
            [get_accel() for ii in range(cal_size)] 
            mpu_array = []
            while len(mpu_array) < cal_size:
                try:
                    accel_data = get_accel()
                    if accel_data:
                        ax, ay, az = accel_data
                        mpu_array.append([ax, ay, az])  
                except:
                    continue
            ax_offsets[direc_ii] = np.array(mpu_array)[:, cal_indices[qq]]  

        # Use three calibrations (+1g, -1g, 0g) for linear fit
        popts, _ = curve_fit(accel_fit, np.append(np.append(ax_offsets[0], ax_offsets[1]), ax_offsets[2]),
                             np.append(np.append(1.0 * np.ones(np.shape(ax_offsets[0])),
                                                 -1.0 * np.ones(np.shape(ax_offsets[1]))),
                                       0.0 * np.ones(np.shape(ax_offsets[2]))),
                             maxfev=10000)
        mpu_offsets[cal_indices[qq]] = popts  # place slope and intercept in offset array
    print('Accelerometer Calibrations Complete')
    return mpu_offsets

if __name__ == "__main__":
    accel_coeffs = accel_cal()
    np.save('calibration_coeffs.npy', accel_coeffs)
    print("Calibration coefficients saved to 'calibration_coeffs.npy'")
