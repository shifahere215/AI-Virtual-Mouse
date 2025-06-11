import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
wScr, hScr = autopy.screen.size()  # Get screen size
# print(wScr, hScr)
smoothening = 17  # Smoothing factor for mouse movement
# #########################

cap = cv2.VideoCapture(0)  # Use 0 for the default camera
cap.set(3, wCam)  # Set width
cap.set(4, hCam)  # Set height


pTime = 0  # Previous time for FPS calculation
clocX, clocY = 0, 0  # Current location of the mouse
plocX, plocY = 0, 0  # Previous location of the mouse

detector = htm.handDetector(maxHands=1)  # Initialize hand detector

while True:
     # 1. Find hand Landmarks
    success, img = cap.read()  # Read the frame from the camera]
    img = detector.findHands(img)  # Detect hands in the image
    lmList, bbox = detector.findPosition(img)  # Get hand landmarks and bounding box

    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

    # 3. Check which fingers are up
    fingers = detector.fingersUp()
    cv2.rectangle(img, (frameR, frameR), (wCam-frameR, hCam-frameR), (255, 0, 255), 2)
    # print(fingers)

    if len(fingers) >= 3:
        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))
            # Add movement code here if needed

            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            # autopy.mouse.move(wScr - clocX, clocY)
            # Ensure values stay within bounds
            mouseX = max(0, min(wScr - 1, wScr - clocX))
            mouseY = max(0, min(hScr - 1, clocY))

            autopy.mouse.move(mouseX, mouseY)

            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
        
        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
    
    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, 
                (255, 0, 0), 3)
    

    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)