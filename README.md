# Burglar Alarm
Team members: David Bai, Peter Wang

Setup:
1. Set up an AWS EC2 Instance with an nginx proxy in order to run Flask.
2. Run server.py on the EC2 instance
3. Substitute the IPs in detector, main, and app.js for your own ec2 instance public IP
4. install mediapipe dependencies for detector.py
5. install npm dependencies for react app
6. set up grovepi on your own raspberry pi, run main.py
7. All nodes should be set up, and npm start the react app to start streaming data. 