
import sys
import time
import requests
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('Software/Python/')
import grovepi
# This append is to support importing the LCD library.
sys.path.append('Software/Python/grove_rgb_lcd')
import grove_rgb_lcd

# Grove ultrasonic sensor to digital port D4
ultrasonic_port = 4

# Connect the Grove Light Sensor to analog port A0
light_sensor = 0
grovepi.pinMode(light_sensor,"INPUT")

def getDistance():
	return grovepi.ultrasonicRead(ultrasonic_port)

def getLightReading():
	return grovepi.analogRead(light_sensor)

def main():
	url = "http://52.38.44.83/api/sensors"

	while True:
		distance = getDistance()
		light = getLightReading()

		obj = {"ultrasonic_reading": distance, "light_level": light}
		requests.post(url, json = obj)
		print("Distance:", distance, "Light:", light)

		time.sleep(0.1)


if __name__ == "__main__":
	main();


#
#curl -X POST \
#     -H "Content-Type: application/json" \
#     -d '{"sound_level": 75, "light_level": 150, "timestamp": "2024-11-19T15:42:00Z"}' \