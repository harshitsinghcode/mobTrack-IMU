# mobTrack - IMU based Position Tracking 🤳🏻🛜 [ First of its kind ]

Explore the potential of your mobile device's IMU sensor + monocular camera with mobTrack. This repository hosts a comprehensive solution for accurate position tracking, enabling a wide range of applications in robotics, AR, VR, and beyond.

## Overview 📝

This repository provides a comprehensive system for IMU-based position tracking using accelerometer data from your mobile device. Here's a breakdown of how it works:

1. **Data Acquisition**: We capture accelerometer (in this case - `Ic4n607`) data from both Android and iOS devices with "Serializer Sensor" and "IMU-Utility" apps, respectively. Android data is converted to CSV format and stored in the `1. Accelerations` folder, while iOS data is converted from JSON to CSV and stored in the same folder.

2. **Calibration**: Calibration is essential for accurate tracking. Our system offers two calibration methods:
   1. Manual Calibration: Use a dedicated app to calibrate the IMU sensor manually.
   2. Script Calibration: Utilize our `calib.py` script to calibrate the sensor automatically. This script generates `calibration_coeffs.npy`, which contains calibration coefficients for further use.

3. **Data Collection**: Once calibrated, you can collect data using `mig.py`. This script retrieves calibrated data from the sensor and stores it in the `1. Accelerations` folder. Alternatively, if the sensor is already calibrated, you can use `sockets.py` to collect data directly.

4. **Data Processing**: The `sukhoi.py` script processes the collected accelerometer data. It filters the data using a band-pass filter with specified low and high cutoff frequencies. It then integrates the filtered acceleration data to obtain velocity and position information. Finally, it applies a high-pass filter to remove drifts.

5. **Visualization**: Our system offers visualization capabilities, including:

   a. Plotting position graphs for X, Y, and Z axes.
   
   b. Storing velocity data in `2. Velocities` folder.
   
   c. Storing position data in `3. Positions` folder.
   
   d. Interesting part of the repository is that, it also stores the frame captured at the moment with respect to imu recordings in `pics` folder, so that the imu data of every frame has been recorded which can be further used for varied applications.
   
   ![image](https://github.com/harshitsinghcode/mobTrack-IMU/assets/110082422/b02408b7-343f-4d58-91ef-4b4e53cd755c)

## Getting Started 🚀

- To use this system, follow these steps:

- Data Acquisition: Ensure you have the "Serializer Sensor" or "IMU-Utility" app installed on your Android or iOS device, respectively. Connect your device to the WebSocket server to start sending accelerometer data.

- Calibration: Choose the calibration method that suits your needs. For manual calibration, use a calibration app. For script calibration, run calib.py and follow the instructions. Use the generated calibration_coeffs.npy file for further calibration.

```shell
1. python runner.py
2. Enter 'c' to calibrate, 'd' to collect data with calib, 'dw' to collect data without calib, 'a' to run analysis, or 'q' to quit:
3. - Running data collection script...
     Press Ctrl+C to stop data collection.

   - Running data collection script_without clib...
     This PC's IP:  ""
     Listening on Port:  ""

   - Running analysis script...
     Total distance covered: "" meters
     Position data saved to ""
     Velocity data saved to ""

```
## Key Findings 📈

### Based on our observations:

For distances up to 10 metres, the system achieved an accuracy of 73% with a deviation of ±2.02 meters.

## Future Work 🧭

### Potential areas for improvement and future work include:

1. Fusion of gyroscope and gravity data.
2. Application of Kalman filter for position prediction and enhanced accuracy.

## Requirements ⚙️ 

- To run this project, you need:

1. Python (Anaconda environment recommended)
2. Required Python libraries (specified in requirements.txt)
   
## License 📃
This project is licensed under the MIT License.

As **mobTrack** is one of the first iterations using mobile phones's IMU, feel free to explore the repository and contribute to further advancements in IMU based position tracking technology! If you have any questions or suggestions, please don't hesitate to reach out.

Happy tracking! 🧭✈️
