import cv2
import time
import numpy as np
import LearnSign as SL

protoFile = "HandModel/pose_deploy.prototxt"
weightsFile = "HandModel/pose_iter_102000.caffemodel"
nPoints = 22
POSE_PAIRS = [ [0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[0,9],[9,10],[10,11],[11,12],[0,13],[13,14],[14,15],[15,16],[0,17],[17,18],[18,19],[19,20] ]

threshold = 0.2

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,500)
fontScale              = 1.5
fontColor              = (255,255,255)
#fontColor              = (0,0,0)
lineType               = 2



#input_source = "asl.mp4"
input_source = "AlphabetVideo.avi"
cap = cv2.VideoCapture(input_source) #for video input
#cap=cv2.VideoCapture(0) #for camera input
hasFrame, frame = cap.read()

frameWidth = frame.shape[1]
frameHeight = frame.shape[0]

bottomLeftCornerOfText=(int(frameWidth*0.5),int(frameHeight*0.75))

aspect_ratio = frameWidth/frameHeight

inHeight = 368
inWidth = int(((aspect_ratio*inHeight)*8)//8)

vid_writer = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 15, (frame.shape[1],frame.shape[0]))

net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
k = 0

cv2.namedWindow('Output-Skeleton', cv2.WINDOW_NORMAL)

FeatureVectors=SL.loadVectors("FVectors_old2")

while 1:
    complex_sign=0
    k+=1
    t = time.time()
    hasFrame, frame = cap.read()
    frameCopy = np.copy(frame)
    if not hasFrame:
        cv2.waitKey()
        break

    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                              (0, 0, 0), swapRB=False, crop=False)

    net.setInput(inpBlob)

    output = net.forward()

    print("forward = {}".format(time.time() - t))

    # Empty list to store the detected keypoints
    points = []

    for i in range(nPoints):
        # confidence map of corresponding body's part.
        probMap = output[0, i, :, :]
        probMap = cv2.resize(probMap, (frameWidth, frameHeight))

        # Find global maxima of the probMap.
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

        if prob > threshold :
            cv2.circle(frameCopy, (int(point[0]), int(point[1])), 6, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frameCopy, "{}".format(i), (int(point[0]), int(point[1])), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 0, 255), 2, lineType=cv2.LINE_AA)

            # Add the point to the list if the probability is greater than the threshold
            points.append((int(point[0]), int(point[1])))
        else :
            points.append(None)

    # Draw Skeleton
    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], (0, 255, 255), 2, lineType=cv2.LINE_AA)
            cv2.circle(frame, points[partA], 5, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.circle(frame, points[partB], 5, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

    print("Time Taken for frame = {}".format(time.time() - t))

    # cv2.putText(frame, "time taken = {:.2f} sec".format(time.time() - t), (50, 50), cv2.FONT_HERSHEY_COMPLEX, .8, (255, 50, 0), 2, lineType=cv2.LINE_AA)
    # cv2.putText(frame, "Hand Pose using OpenCV", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 50, 0), 2, lineType=cv2.LINE_AA)

    Identification=SL.signIdentification(SL.getFeatureVector(points),FeatureVectors)

    if(Identification[0][-2]=="_"):
        if(complex_sign==Identification[0][-1]):
            pass
        elif(complex_sign==0 and Identification[0][-1]==1):
            complex_sign=1
        elif (complex_sign == 1 and Identification[0][-1] == 2):
            complex_sign = 2
        elif (complex_sign == 2 and Identification[0][-1] == 3):
            complex_sign = 3
        elif (complex_sign == 3 and Identification[0][-1] == 4):
            complex_sign = 4
        elif (complex_sign == 4 and Identification[0][-1] == 5):
            complex_sign = 5
    elif(complex_sign>1):
        Identification[0]=Identification[0][:-2]
        complex_sign=0
        cv2.putText(frame, Identification[0], bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
    else:
        cv2.putText(frame, Identification[0], bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        

    #cv2.putText(frame, Identification[0],bottomLeftCornerOfText, font, fontScale,fontColor,lineType)
    print(Identification[0]," - Similarity: ",Identification[1])

    cv2.imshow('Output-Skeleton', frame)
    # cv2.imwrite("video_output/{:03d}.jpg".format(k), frame)
    key = cv2.waitKey(1)
    if key == 27:
        break

    print("total = {}".format(time.time() - t))

    vid_writer.write(frame)

vid_writer.release()
