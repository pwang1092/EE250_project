
import sys
import time
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('Software/Python/')
import grovepi
# This append is to support importing the LCD library.
sys.path.append('Software/Python/grove_rgb_lcd')
import grove_rgb_lcd

ultrasonic_port = 3
light_sensor_port = 4

# Connect the Grove Light Sensor to analog port A0
light_sensor = 0
grovepi.pinMode(light_sensor,"INPUT")

def getDistance():
	return grovepi.ultrasonicRead(ultrasonic_port)

def getLightReading():
	return sensor_value = grovepi.analogRead(light_sensor)

def main():
	while true:
		print("Distance:", getDistance(), "Light:", getLightReading())
		time.sleep(0.1)


if __name__ == "__main__":
	main();