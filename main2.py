import serial
import cv2
import math
from cvzone.HandTrackingModule import HandDetector

# Function to initialize serial communication
def initialize_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate)
        ser.timeout = 1
        print(f"Successfully opened port {port}")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        return None

# Initialize camera, hand detector, and serial communication
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=2)
serialcomm = initialize_serial('COM3', 9600)  # Change port if necessary

# Function to map distance to brightness with enhanced visibility
def distance_to_brightness(distance, max_distance=200):
    # Exponential scaling to make low brightness levels more visible
    # Modify the exponent to adjust the sensitivity of the brightness
    exponent = 2  # Adjust this value as needed (higher value = more sensitivity at low brightness)
    brightness = int(((distance / max_distance) ** exponent) * 255)
    return brightness

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        if len(hands) == 1:
            hand1 = hands[0]

            if hand1["type"] == "Right":
                fingersUp = detector.fingersUp(hand1)
                print("Right Hand Fingers:", fingersUp)
                if serialcomm:
                    serialcomm.write(f"LED_STATE:{','.join(map(str, fingersUp))}\n".encode())

            elif hand1["type"] == "Left":
                lmList1 = hand1['lmList']
                index_finger_tip = lmList1[8]
                middle_finger_tip = lmList1[12]

                distance = math.dist(index_finger_tip, middle_finger_tip)
                brightness = distance_to_brightness(distance)
                print("LED Brightness:", brightness)

                if serialcomm:
                    serialcomm.write(f"BRIGHTNESS:{brightness}\n".encode())

                bar_height = int(brightness / 255 * 300)
                cv2.rectangle(img, (50, 400), (100, 400 - bar_height), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f'Brightness: {brightness}', (50, 380), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        elif len(hands) == 2:
            hand1, hand2 = hands[0], hands[1]

            if hand1["type"] == "Right":
                right_hand = hand1
                left_hand = hand2
            else:
                right_hand = hand2
                left_hand = hand1

            fingersUp_right = detector.fingersUp(right_hand)
            print("Right Hand Fingers:", fingersUp_right)
            if serialcomm:
                serialcomm.write(f"LED_STATE:{','.join(map(str, fingersUp_right))}\n".encode())

            lmList_left = left_hand['lmList']
            index_finger_tip = lmList_left[8]
            middle_finger_tip = lmList_left[12]

            distance = math.dist(index_finger_tip, middle_finger_tip)
            brightness = distance_to_brightness(distance)
            print("LED Brightness:", brightness)

            if serialcomm:
                serialcomm.write(f"BRIGHTNESS:{brightness}\n".encode())

            bar_height = int(brightness / 255 * 300)
            cv2.rectangle(img, (50, 400), (100, 400 - bar_height), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'Brightness: {brightness}', (50, 380), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    else:
        if serialcomm:
            serialcomm.write(b'BRIGHTNESS:0\n')

    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
if serialcomm:
    serialcomm.close()