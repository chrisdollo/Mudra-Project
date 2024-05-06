#!/usr/bin/env python
# coding: utf-8

# In[7]:


import cv2
import math
import mediapipe as mp


# In[8]:


class HandDetector:

    # constructor for the class
    def __init__(self, mode = False, maxHands = 1, modelC = 1, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelC = modelC
        self.trackCon = trackCon
        
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelC, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        
    # finds and draaw the hands
    def findHands(self, img):
        imgRBG = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRBG)
        
        # If landmarks detected
        if self.results.multi_hand_landmarks:
            # Then draw the landmarks
            for handLandmarks in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLandmarks, self.mpHands.HAND_CONNECTIONS, self.mpDraw.DrawingSpec(color = (255, 0, 0), thickness = 2, circle_radius = 2), self.mpDraw.DrawingSpec(color = (0,255,0), thickness = 2, circle_radius = 2))
        return img
    
    # finds why hand is showing to the camera
    def findHandedness(self):
        if self.results.multi_handedness:
            handType1 = self.results.multi_handedness[0].classification[0].label
            return handType1
    
    # Find the orientation of the hand
    def determineOrientation(self, landmarkList):

        orientation = "X"
        directonVector = [landmarkList[0], landmarkList[9]]
                                    
        xDir = directonVector[1][1] - directonVector[0][1]
        yDir = directonVector[1][2] - directonVector[0][2]

        angle = math.degrees(abs((math.atan2(yDir, xDir))))
        if (angle > 90):
            angle = 180 - angle
        
        if (angle < 70):
            orientation = "X"
        else:
            orientation = "Y"

        return orientation

    # inds the landmarks       
    def findPosition(self, img):
        landmarkList = []

        # if more than one hand was detected
        if self.results.multi_hand_landmarks:

            # this line selects the first hand that was detected
            myHand = self.results.multi_hand_landmarks[0]

            for id, lm in enumerate(myHand.landmark):
                h,w,c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarkList.append([id, cx, cy])
        return landmarkList


    def gestureRecognizer(self, landmarkList):

        # find the distance between 2 points
        def findDistance(point1, point2):
            distance = ((point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)**0.5
            return distance
        

        # find the angle between 2 vectors
        def findAngle(pointA, pointB, pointC, pointD):
            # findVectors
            vectorBA = [(pointA[1] - pointB[1]), (pointA[2] - pointB[2])]
            vectorDC = [(pointC[1] - pointD[1]), (pointC[2] - pointD[2])]

            # find the dot product
            dotProduct = vectorBA[0]*vectorDC[0] + vectorBA[1]*vectorDC[1]

            # find magnitudes of vectors 
            magnitudeVectorBA = (vectorBA[0]**2 + vectorBA[1]**2)**(1/2)
            magnitudeVectorDC = (vectorDC[0]**2 + vectorDC[1]**2)**(1/2)

            angle = 0

            if (magnitudeVectorBA*magnitudeVectorDC) != 0:
                if -1 <= dotProduct/(magnitudeVectorBA*magnitudeVectorDC) <= 1:
                    angle = math.acos(dotProduct/(magnitudeVectorBA*magnitudeVectorDC)) * (180/math.pi)

            return angle
        
        # return if we have a majority of true
        def majorityBool(array):
            count = 0
            for conditions in array:
                if conditions == 1:
                    count = count + 1
            
            return (count > 2) 


        def isHighestPoint(pointTested):
            highestPoint = wrist
            for point in landmarkList:
                if point[2] < highestPoint[2]:
                    highestPoint = point
            
            return (highestPoint == pointTested)



        thumbState = ""
        indexState = ""
        middleState = ""
        ringState = ""
        pinkyState = ""
        handGesture = ""
       
        
        if len(landmarkList) != 0:

            thumbTip = landmarkList[4]
            thumbFirstJoint = landmarkList[3]
            indexTip = landmarkList[8]
            indexFirstJoint = landmarkList[7]
            middleTip = landmarkList[12]
            ringTip = landmarkList[16]
            pinkyTip = landmarkList[20]
            wrist = landmarkList[0]

            orientation = self.determineOrientation(landmarkList)
            

            

            # Distance between relative points 

            ThumbMiddleDistance = findDistance(middleTip, thumbTip)
            ThumbIndexDistance = findDistance(indexTip, thumbTip)
            ThumbRingDistance = findDistance(ringTip, thumbTip)
            ThumbPinkyDistance = findDistance(pinkyTip, thumbTip)

            indexMiddleDistance = findDistance(indexTip, middleTip)
            indexRingDistance = findDistance(ringTip, indexTip)
            indexPinkyDistance = findDistance(indexTip, pinkyTip)

            middleRingDistance = findDistance(ringTip, middleTip)
            middlePinkyDistance = findDistance(middleTip, pinkyTip)

            ringPinkyDistance = findDistance(pinkyTip, ringTip)

            

            # we will use unit distance to measure how close 2 points are
            
            # index distal phalange length
            unitDistance = findDistance(indexTip, indexFirstJoint)

            # thumb distal phalange length
            unitDistance2 = findDistance (thumbTip, thumbFirstJoint)

            # thumb distal phalange length
            unitDistance3 = findDistance (wrist, landmarkList[5])/4

            middleToWristDistance = findDistance(middleTip, wrist)


            handedness = detector.findHandedness()



                

            if (landmarkList[3][2] < landmarkList[2][2]) and ((handedness == "Left" and (landmarkList[4][1] > landmarkList[5][1])) or (handedness == "Right" and (landmarkList[4][1] < landmarkList[5][1]))):
                thumbState = "OPEN"
            else:
                thumbState = "CLOSE"
            




            
            # identifies index' state
            if ((landmarkList[6][2] > landmarkList[7][2] > indexTip[2]) or (((indexTip[1] < landmarkList[7][1] < landmarkList[6][1]) or (landmarkList[6][1] < landmarkList[7][1] < indexTip[1])) and (abs(indexTip[1] - landmarkList[6][1]) > unitDistance))) and (findDistance(indexTip, wrist) > unitDistance3*4):
                indexState = "OPEN"
            else:
                indexState = "CLOSE"


            # identifies middle finder's state
            if ((landmarkList[10][2] > landmarkList[11][2] > middleTip[2]) or (((middleTip[1] < landmarkList[11][1] < landmarkList[10][1]) or (landmarkList[10][1] < landmarkList[11][1] < middleTip[1])) and (abs(middleTip[1] - landmarkList[10][1]) > unitDistance)))  and (middleToWristDistance > unitDistance3*4):
                middleState = "OPEN"
            else:
                middleState = "CLOSE"


            # identidies ring state
            if ((landmarkList[14][2] > landmarkList[15][2] > ringTip[2]) or (((ringTip[1] < landmarkList[15][1] < landmarkList[14][1]) or (landmarkList[14][1] < landmarkList[15][1] < ringTip[1])) and (abs(ringTip[1] - landmarkList[14][1]) > unitDistance)))  and (findDistance(ringTip, wrist) > unitDistance3*4):
                ringState = "OPEN"
            else:
                ringState = "CLOSE"


            # identidies pinky states 
            if ((landmarkList[18][2] > landmarkList[19][2] > pinkyTip[2]) or (((pinkyTip[1] < landmarkList[19][1] < landmarkList[18][1]) or (landmarkList[18][1] < landmarkList[19][1] < pinkyTip[1])) and (abs(pinkyTip[1]-landmarkList[18][1]) > unitDistance)))  and (findDistance(pinkyTip, wrist) > unitDistance3*4):
                pinkyState = "OPEN"
            else:
                pinkyState = "CLOSE"


            
            print("thumbState: ", thumbState)
            print("indexState: ", indexState)
            print("middleState: ", middleState)
            print("ringState: ", ringState)
            print("pinkyState: ", pinkyState)
            
            # identify the gesture

            # 5 MAYURA
            # modify
            #if indexState == "OPEN" and middleState == "OPEN" and pinkyState == "OPEN" and ThumbRingDistance < unitDistance: 
                #handGesture = "MAYURA"

            # 1 PATAAKAM
            if thumbState == "OPEN" and indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN" and (indexMiddleDistance < 2*unitDistance) and middleRingDistance < unitDistance and ringPinkyDistance < 2*unitDistance and (findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) > 20) and orientation == "Y" and findDistance(landmarkList[5], thumbTip)<unitDistance*2.5 and (findAngle(wrist, landmarkList[17], landmarkList[17], pinkyTip) < 30):
                handGesture = "PATAAKAM"


            # 2 TRIPATAAKAM
            elif thumbState == "OPEN" and indexState == "OPEN" and middleState == "OPEN" and pinkyState == "OPEN" and (findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) > 20) and ringTip[2] > landmarkList[7][2] and ThumbRingDistance < unitDistance*3 and orientation == "Y" and (isHighestPoint(indexTip) or isHighestPoint(middleTip)):
                handGesture = "TRIPATAAKAM"


            # 3 ARDHAPATAAKAM
            elif thumbState == "OPEN" and indexState == "OPEN" and ringState != "OPEN" and pinkyState != "OPEN" and middleState == "OPEN" and (findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) > 20) and ringTip[2] > landmarkList[7][2] and pinkyTip[2] > landmarkList[7][2]:
                handGesture = "ARDHAPATAAKAM"


            # 4 KARTARI MUKHAM
            elif thumbState == "CLOSE" and indexState == "OPEN" and middleState == "OPEN" and ringState == "CLOSE" and pinkyState == "CLOSE" and ThumbRingDistance < 1.5*unitDistance and ThumbPinkyDistance < 1.5*unitDistance and middleToWristDistance > unitDistance*6 and indexMiddleDistance < 3*unitDistance:
                handGesture = "KARTARI MUKHAM"


            # 5 MAYURA
            elif thumbState == "CLOSE" and indexState == "OPEN" and middleState == "OPEN" and ringState == "CLOSE" and pinkyState == "OPEN" and ThumbRingDistance < 2*unitDistance and ThumbPinkyDistance > 3*unitDistance:
                handGesture = "MAYURA"


            # 6 ARDHA CHANDRA
            elif thumbState == "OPEN" and indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN" and ThumbIndexDistance > 5*unitDistance and (findAngle(landmarkList[5],landmarkList[6],landmarkList[6],landmarkList[7]) < 15) and (findAngle(landmarkList[9],landmarkList[10],landmarkList[10],landmarkList[11]) < 15) and (findAngle(landmarkList[13],landmarkList[14],landmarkList[14],landmarkList[15]) < 15) and not isHighestPoint(pinkyTip): 
                handGesture = "ARDHA CHANDRA"
    

            # 7 ARAALA
            elif thumbState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN" and (findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) > 20) and indexTip[2] > landmarkList[15][2] and (isHighestPoint(middleTip) or isHighestPoint(ringTip)) and orientation == "Y" and ringTip[2] < landmarkList[7][2]:
                handGesture = "ARAALA"


            # 8 SHUKA TUNDAM
            elif thumbState == "OPEN" and middleState == "OPEN" and pinkyState == "OPEN" and (findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) > 20) and indexTip[2] > landmarkList[11][2] and ringTip[2] > landmarkList[11][2] and isHighestPoint(middleTip) and orientation == "Y":
                handGesture = "SHUKA TUNDAM"


            # 9 MUSHTI 2
            elif findDistance(wrist, indexTip) < unitDistance3*5 and findDistance(wrist, middleTip) < unitDistance3*5 and findDistance(wrist, ringTip) < unitDistance3*5 and findDistance(wrist, pinkyTip) < unitDistance3*5 and findDistance(wrist, thumbTip) < unitDistance3*6 and indexState == "CLOSE" and middleState == "CLOSE" and ringState == "CLOSE"and pinkyState == "CLOSE" and findDistance(thumbTip, middleTip) < unitDistance3*1.5:
                handGesture = "MUSHTI"


            # 10 SHIKHARAM
            elif findDistance(wrist, landmarkList[6]) > findDistance(wrist, indexTip) and findDistance(wrist, landmarkList[10]) > findDistance(wrist, middleTip) and findDistance(wrist, landmarkList[14]) > findDistance(wrist, ringTip) and findDistance(wrist, landmarkList[18]) > findDistance(wrist, pinkyTip)  and orientation == "X" and (findAngle(landmarkList[1], landmarkList[5], landmarkList[2], landmarkList[3]) > 20) and isHighestPoint(landmarkList[4]):
                handGesture = "SHIKHARAM"

            # 11 KAPITHAM
            elif middleState == "CLOSE" and ringState == "CLOSE" and pinkyState == "CLOSE" and (ThumbIndexDistance < unitDistance) and (isHighestPoint(landmarkList[6]) or isHighestPoint(landmarkList[7]) or isHighestPoint(indexTip) ):
                handGesture = "KAPITHAM"

            # 12 KATAKAA MUKHA A
            elif ringState == "OPEN" and pinkyState == "OPEN" and (ThumbIndexDistance < unitDistance) and (ThumbMiddleDistance < unitDistance) and (middlePinkyDistance > unitDistance)  and (middleRingDistance > unitDistance):
                handGesture = "KATAKAA MUKHA A"

            # 12 KATAKAA MUKHA B
            #elif middleState == "CLOSE" and ringState == "CLOSE" and pinkyState == "OPEN" and (ThumbIndexDistance < unitDistance) and (middleTip[2] > ringTip[2] > pinkyTip[2]):
                #handGesture = "KATAKAA MUKHA B"

            # 12 KATAKAA MUKHA C
            elif ringState == "CLOSE" and pinkyState == "CLOSE" and (ThumbIndexDistance < unitDistance) and (ThumbMiddleDistance < unitDistance):
                handGesture = "KATAKAA MUKHA C"

            # 13 SUCHI
            elif findDistance(wrist, indexTip) > unitDistance*7 and findDistance(wrist, middleTip) < unitDistance*5 and findDistance(wrist, ringTip) < unitDistance*5 and findDistance(wrist, pinkyTip) < unitDistance*5 and findDistance(wrist, thumbTip) < unitDistance3*6 and indexState == "OPEN" and findDistance(thumbTip, middleTip) < unitDistance3*1.5:
                handGesture = "SUCHI"
                

            
            # 14 CHANDRAKALA
            # thumb has to be extended and open
            elif thumbState == "OPEN" and indexState == "OPEN" and middleState == "CLOSE" and ringState == "CLOSE" and pinkyState == "CLOSE" and (ThumbIndexDistance > 4*unitDistance) and ((findAngle(landmarkList[1],landmarkList[2], landmarkList[2],landmarkList[3])) < 20) and (findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) < 25):
                handGesture = "CHANDRAKALA"


            # 15 PADMAKOSHA
            elif thumbState == "OPEN" and indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN" and middleToWristDistance < unitDistance2*7 and not(ThumbIndexDistance < unitDistance3 and ThumbMiddleDistance < unitDistance3 and ThumbRingDistance < unitDistance3 and middlePinkyDistance < 1.5*unitDistance3) and ThumbPinkyDistance < unitDistance2*3:
                # majorityBool([ThumbIndexDistance > unitDistance, ThumbMiddleDistance > unitDistance, ThumbPinkyDistance > unitDistance, indexMiddleDistance > unitDistance])
                handGesture = "PADMAKOSHA"


            # 16 SARPASHEERSHA
            # all fingers are open & thumb has to be bent
            elif thumbState == "OPEN" and indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN" and indexMiddleDistance < 1.5*unitDistance and middleRingDistance < unitDistance and ringPinkyDistance < 1.5*unitDistance and (findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) > 15) and (findAngle(wrist, landmarkList[17], landmarkList[17], pinkyTip) > 30):
                handGesture = "SARPASHEERSHA"


            # 17 MRUGASHEERSHA
            # index, ring, middle all have to be bellow the second joint of the pinky
            elif thumbState == "OPEN" and pinkyState == "OPEN" and (indexMiddleDistance < unitDistance2) and (middleRingDistance < unitDistance2) and (ThumbPinkyDistance > 4*unitDistance2) and (indexTip[2] > landmarkList[19][2] and middleTip[2] > landmarkList[19][2] and ringTip[2] > landmarkList[19][2]) and ((findAngle(landmarkList[1],landmarkList[2], landmarkList[2],landmarkList[3])) < 20) and orientation == "Y":
                handGesture = "MRUGASHEERSHA"

            
            # include a condition that says that the distance from the bottom to they tip has to be bigger than the unit distance
            # 18 SIMHAMUKHAM
            elif indexState == "OPEN" and pinkyState == "OPEN" and ThumbMiddleDistance < 1.5*unitDistance and ThumbRingDistance < 1.5*unitDistance and indexMiddleDistance > 2*unitDistance and ringTip[2]>landmarkList[6][2] and middleTip[2]>landmarkList[6][2] and (findAngle(landmarkList[17],landmarkList[18],landmarkList[18],landmarkList[19]) < 30) and (findAngle(landmarkList[5],landmarkList[6],landmarkList[6],landmarkList[7]) < 30):
                handGesture = "SIMHAMUKHAM"
                
            
            # 19 Kangula 
            # the thumb has to be close to make it look more like chandra kala
            elif thumbState == "OPEN" and indexState == "OPEN" and middleState == "OPEN" and ringState == "CLOSE" and pinkyState == "OPEN" and (indexMiddleDistance < 1.5*unitDistance) and (middlePinkyDistance < 3*unitDistance) and ((findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4])) < 30):
                handGesture = "KANGULA"

            # 20 Alapadma
            # the angle between the index and the middle finger has to be more than 20
            elif (indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN") and (ringPinkyDistance > 1.5*unitDistance and middleRingDistance > unitDistance and indexMiddleDistance > 1.5*unitDistance) and (indexTip[2] > middleTip[2] > ringTip[2]) and (findAngle(indexTip, landmarkList[5], middleTip,landmarkList[9]) > 20) and (ThumbIndexDistance > 2*unitDistance):
                handGesture = "ALAPADMA"

            # 21 Chatura
            elif (indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN") and (middleRingDistance < unitDistance and indexMiddleDistance < unitDistance) and wrist[2] < pinkyTip[2]:
                handGesture = "CHATURA"

            # 22 Bhramara
            # pinky and ring are open, distance between the tips of index and thumb AND Middle and Thunb 
            # because of mediapipe skill issuesit doesn't work)
            #if (ringState == "OPEN" and pinkyState == "OPEN") and (ringPinkyDistance > 2*unitDistance):
             #   handGesture = "BHRAMARA"


            # 23 Hamsasya       
            elif (middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN") and (ThumbIndexDistance < unitDistance) and (indexMiddleDistance > (3*unitDistance)):
                handGesture = "HAMSAYA"

            # 24 Hamsapaksha
            # perfectly gets it   
            elif (indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN") and (middleRingDistance < unitDistance and indexMiddleDistance < unitDistance and ringPinkyDistance > 2*unitDistance) and ringTip[2] > pinkyTip[2] and not(findAngle(landmarkList[2],landmarkList[3],landmarkList[3],landmarkList[4]) > 20):
                handGesture = "HAMSAPAKSHA"
            


            # 26 Mukula
            # perfectly gets it   
            elif (indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "OPEN") and (ThumbIndexDistance < unitDistance3 and ThumbMiddleDistance < unitDistance3 and ThumbRingDistance < unitDistance3 and ThumbPinkyDistance < unitDistance3 and middlePinkyDistance < 1.5*unitDistance3) and orientation=="Y":
                handGesture = "MUKULA"


            # 27 Tamrachooda      
            # check if the thumb is half open
            elif middleState == "CLOSE" and ringState == "CLOSE" and pinkyState == "CLOSE" and ( (360-findAngle(landmarkList[6],landmarkList[7], landmarkList[7],indexTip)) / 2 ) < 170 and ( findAngle(landmarkList[5],landmarkList[6], landmarkList[6],landmarkList[7]) / 2 ) < 35 and landmarkList[4][2] > landmarkList[10][2]:
                handGesture = "TAMRACHOODA"


            # 28 Trishoola 
            # perfectly gets it       
            elif thumbState == "CLOSE" and indexState == "OPEN" and middleState == "OPEN" and ringState == "OPEN" and pinkyState == "CLOSE" and ThumbPinkyDistance < unitDistance*2 and indexMiddleDistance < 3*unitDistance and ThumbMiddleDistance > 3*unitDistance3:
                handGesture = "TRISHOOLA"

            


            

        


        

        return handGesture
        
        


# In[ ]:


if __name__ == "__main__":

    # chooses the default camera
    cap = cv2.VideoCapture(0)
    #cap = cv2.flip(cap,0)

    # creates a detector object
    detector = HandDetector()

    # Edit this dictionary
    # --------------- Game dictionnary
    gesture_dic = { "KARTARI MUKHAM":4, "ARDHA CHANDRA":6, "MUSHTI":9, "SHIKHARAM":10, "KIPATHAM":11, "SUCHI":13, "CHANDRAKALA":14, "KANGULA":19, "ALAPADMA":20, "CHATURA":21,  "BHRAMARA":22, "HAMSAYA":23, "HAMSAPAKSHA":24, "MUKULA":26, "TAMRACHOODA":27, "TRISHOOLA":28}

    # --------------- saves the value of the gest
    gest_val = []


    while True:

        # --------------- reads the image captured by the camera and return 2 values
        # --------------- wether or not it was a success and the image itself
        success, img = cap.read()

        # --------------- calls the findHands function on the image
        img = detector.findHands(img)

        # --------------- call the find position and saves the list of landmark
        landmarkList = detector.findPosition(img)


        # --------------- checks wether or not we have landmarks on the hand or if there's a hand
        if len(landmarkList) != 0:
            
            # --------------- identifies the gesture and add the text
            hg = detector.gestureRecognizer(landmarkList)
            cv2.putText(img, detector.gestureRecognizer(landmarkList), (landmarkList[0][1]-50, landmarkList[0][2]-300), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255),2)

            # --------------- if the text detected is in the dictionary of values that we have add it to the gest_value array
            if hg in gesture_dic:
                gest_val.append(gesture_dic[hg])

        
        #img = cv2.resize(img, (500, 500))

        # --------------- just creates the window by which we can see the landmarks
        cv2.imshow("Project Mudras", img)

        hg = detector.gestureRecognizer(landmarkList)

        #print(landmarkList)


        # --------------- allows the user to leave by pressing q
        if cv2.waitKey(1) == ord('q'):
            break


    # --------------- basically shuts down the windows and gets out of the camera    
    cv2.destroyAllWindows()
    cap.release()


# """
# Play with the code to understand the landmark segment part for each of the 21 sensors. Each sensor generates a vector of different components. 
# The first 2 components which are the X and Y coordinates. 
# 
# Task 1:
# Based on the idea we discussed about the position of the segement in the image space, find the different states of each of the digits. 
# Using the states identified for each digit, create the hand gesture as rock, paper or scissors.
# 
# Task 2:
# From the hand gesture identified, return the hand gesture of the winning response. 
# 
# """