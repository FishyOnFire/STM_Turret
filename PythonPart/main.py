from pyexpat import model
from time import sleep

import serial
import cv2
from ultralytics import YOLO


def main():

    model = YOLO("yolo26n.pt")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    last_x = 0
    last_y = 0
    span = 50

    ser = serial.Serial("COM3", 115200)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, classes=[0], conf=0.5, max_det=1) #Person is class 0
        boxes = results[0].boxes


        if len(boxes) > 0:
            
            x1, y1, x2, y2 = map(int, boxes[0].xyxy[0].tolist())

            # Calculate center point
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            # Print coordinates and draw the point
            print(f"Person detected -> Top-Left: ({x1}, {y1}), Bottom-Right: ({x2}, {y2}), Center: ({center_x}, {center_y})")
            cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)

            if center_x < (640 -span):
                
                if last_x != 3:
                    print("Left X")
                    ser.write(bytearray('3','ascii'))
                    last_x = 3
            elif center_x > (640 +span):
                
                if last_x != 1:
                    print("Right X")
                    ser.write(bytearray('1','ascii'))
                    last_x = 1
            else:
                if last_x != 2:
                    print("Stopped X")
                    ser.write(bytearray('2','ascii'))
                    last_x = 2


            if center_y < (360 - span):
                if last_y != 6:
                    ser.write(bytearray('6','ascii'))
                    last_y = 6
            elif center_y > (360 +span):
                if last_y != 4:
                    ser.write(bytearray('4','ascii'))
                    last_y  = 4
            else:
                if last_y != 5:
                    ser.write(bytearray('5','ascii'))
                    last_y = 5


        # rendering
        annotated_frame = results[0].plot()
        cv2.imshow("STM32 Turret", annotated_frame)

        # q quits
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        sleep(0.01) # Sleep for cpu usage
        

        
    cap.release()
    cv2.destroyAllWindows()

    ser.write(bytearray('2','ascii'))
    sleep(0.1)
    ser.write(bytearray('5','ascii'))



    

if __name__ == "__main__":
    main()