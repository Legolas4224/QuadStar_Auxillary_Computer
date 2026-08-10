import mpu6050
import time
import numpy as np

# Create a new Mpu6050 object
mpu6050 = mpu6050.mpu6050(0x69)

# Define a function to read the sensor data
def read_sensor_data():
    # Read the accelerometer values
    accelerometer_data = mpu6050.get_accel_data()

    # Read the gyroscope values
    gyroscope_data = mpu6050.get_gyro_data()

    return accelerometer_data, gyroscope_data, temperature

# Start a while loop to continuously read the sensor data
while True:

    # Read the sensor data
    acel, gyro, temperature = read_sensor_data()

    g = np.sqrt(acel["x"]**2 + acel["y"]**2 + acel["z"]**2)
    mag = np.sqrt(gyro["x"]**2 + gyro["y"]**2 + gyro["z"]**2)
    unit = [v/g for v in acel.values()]

    # Print the sensor data
    print("Accelerometer data:", acel)
    print("Gyroscope data:", gyro)
    print("G:", g)
    print("Unit g:", unit)

    # Wait for 1 second
    time.sleep(1)
