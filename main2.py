import RPi.GPIO as GPIO
import smbus #import SMBus module of I2C
import time
from time import sleep          #import

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define the GPIO pins
LED_PIN = 16

# Motor 1 (Left)
IN3 = 19
IN4 = 26
ENA = 13

# Motor 2 (Right)
IN1 = 5
IN2 = 6
ENB = 12

# Ultrasonic Sensor Pins
TRIG = 22 #on zero its 23
ECHO = 21#on zero its 24

#MPU Sensor Pins
SDA = 2
SCL = 3

#Setup GPIO pins
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

#Initialize PWM for motor speed control
pwm_a = GPIO.PWM(ENA, 1000)  # 1000Hz frequency
pwm_b = GPIO.PWM(ENB, 1000)
pwm_a.start(50)  # Start at 50% duty cycle
pwm_b.start(50)

# Variables
safe_distance = 20  # in cm (stop if object is closer than this)
current_distance = 0

def get_distance():
    # Send pulse to trigger
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    pulse_start = time.time()
    pulse_end = time.time()
    
    # Wait for echo to go high
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    
    # Wait for echo to go low
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Calculate distance in cm
    distance = round(distance, 2)
    
    return distance

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")




def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("Moving Forward")

def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    GPIO.output(LED_PIN, GPIO.LOW)
    print("Moving Backward")

def left():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("Turning Left")

def right():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("Turning Right")

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.LOW)
    print("Stopping")

def set_speed(speed):
    # Speed should be between 0-100
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)

try:
    while True:
        # Get current distance
        current_distance = get_distance()
        print(f"Distance: {current_distance} cm")

        #Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)
        
        #Read Gyroscope raw value
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)
        
        #Full scale range +/- 250 degree/C as per sensitivity scale factor In g units
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0
        
        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0



        print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az) 	
        sleep(1)
        
        if current_distance > safe_distance:
            forward()
        elif current_distance < safe_distance and current_distance > safe_distance/2:
            # Object getting close, slow down
            set_speed(30)
            backward()
            time.sleep(0.5)
            stop()
            time.sleep(0.1)
            
            # Decide which way to turn
            # First check right
            right()
            time.sleep(0.3)
            stop()
            right_dist = get_distance()
            
            # Then check left
            left()
            time.sleep(0.6)  # Turn a bit more to the left
            stop()
            left_dist = get_distance()
            
            # Choose direction with more space
            if right_dist > left_dist and right_dist > safe_distance:
                right()
                time.sleep(0.5)
            elif left_dist > safe_distance:
                left()
                time.sleep(0.5)
            else:
                # No good options, go backward
                backward()
                time.sleep(1)
        else:
            # Too close, emergency stop and reverse
            stop()
            time.sleep(0.1)
            backward()
            time.sleep(1)
            stop()
        
        time.sleep(0.1)  # Short delay between measurements

except KeyboardInterrupt:
    print("Program stopped by user")
    stop()
    pwm_a.stop()
    pwm_b.stop()
    GPIO.cleanup()

