from time import sleep

import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.SerialModule import SerialObject
import math

# Initialize camera, hand detector, and serial communication
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=2)
MySerial = SerialObject("COM3", 9600, 3)

# Function to map distance to brightness (Reversed Logic)
def distance_to_brightness(distance, max_distance=200):
    # Map distance (0 - max_distance) to brightness (0 - 255)
    # Brightness increases with distance, decreases when fingers are close
    brightness = int(min(distance, max_distance) / max_distance * 255)
    return brightness

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        # If one hand is detected
        if len(hands) == 1:
            hand1 = hands[0]

            # Right hand controls LED states (on/off based on fingers raised)
            if hand1["type"] == "Right":
                fingersUp = detector.fingersUp(hand1)
                fingersUp=[i+300 for i in fingersUp]
                fingersUp.append(400)
                print("Right Hand Fingers:", fingersUp)
                MySerial.sendData(fingersUp)

        elif len(hands) == 2:
            hand1, hand2 = hands[0], hands[1]

            # Identify which hand is right and which is left
            if hand1["type"] == "Right":
                right_hand = hand1
                left_hand = hand2
            else:
                right_hand = hand2
                left_hand = hand1

            # Right hand controls LED states (on/off based on fingers raised)
            fingersUp_right = detector.fingersUp(right_hand)
            print("Right Hand Fingers:", fingersUp_right)
            fingersUp_right=[i+300 for i in fingersUp_right]
            fingersUp_right.append(400)
            MySerial.sendData(fingersUp_right)
            # Left hand controls brightness (Reversed logic: closer = dimmer)
            lmList_left = left_hand['lmList']
            index_finger_tip = lmList_left[4]
            thumb_finger_tip = lmList_left[8]

            # Calculate the distance between the tips of the index and middle fingers
            distance = math.dist(index_finger_tip, thumb_finger_tip)
            print("Distance between fingers (Left Hand):", distance)
            # Convert the distance to brightness
            brightness = distance_to_brightness(distance)
            if brightness <= 20:
                brightness = 0
            if brightness >= 150:
                brightness = 255
            print("LED Brightness:", brightness)

            # Send brightness value to control 5 LEDs
            MySerial.sendData([brightness] * 5+[500])

            # Visualize the brightness as a bar
            bar_height = int(brightness / 255 * 300)  # Scale to 300 pixels for the bar
            cv2.rectangle(img, (50, 400), (100, 400 - bar_height), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'Brightness: {brightness}', (50, 380), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    else:
        # No hands detected, turn off all LEDs
        MySerial.sendData([0] * 5)

    # Show the image with brightness bar
    cv2.imshow('Image', img)
    cv2.waitKey(1)