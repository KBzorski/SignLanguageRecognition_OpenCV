from __future__ import division
import cv2
import time
import numpy as np
import math
import glob
import os
import pickle
from scipy import spatial
import numpy as np
import nltk
from pathlib import Path

protoFile = "HandModel/pose_deploy.prototxt"
weightsFile = "HandModel/pose_iter_102000.caffemodel"
nPoints = 22
POSE_PAIRS = [ [0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[0,9],[9,10],[10,11],[11,12],[0,13],[13,14],[14,15],[15,16],[0,17],[17,18],[18,19],[19,20] ]
Learn_pairs = [[2,4],[1,3],[5,7],[6,8],[9,11],[10,12],[13,15],[14,16],[17,19],[18,20],[8,12],[0,4],[0,8],[0,12],[0,16],[0,20],[4,8],[4,12],[4,16],[4,20],[8,12],[8,16],[8,20],[12,16],[12,20],[16,20],[2,6],[6,10],[10,14],[14,18]]
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)


def getPointsFromPicture(path):
    frame = cv2.imread(path)

    frameCopy = np.copy(frame)
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    aspect_ratio = frameWidth/frameHeight

    threshold = 0.1

    t = time.time()
    # input image dimensions for the network
    inHeight = 368
    inWidth = int(((aspect_ratio*inHeight)*8)//8)
    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight), (0, 0, 0), swapRB=False, crop=False)

    net.setInput(inpBlob)

    output = net.forward()
    #print("time taken by network : {:.3f}".format(time.time() - t))

    # Empty list to store the detected keypoints
    points = []

    for i in range(nPoints):
        # confidence map of corresponding body's part.
        probMap = output[0, i, :, :]
        probMap = cv2.resize(probMap, (frameWidth, frameHeight))

        # Find global maxima of the probMap.
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

        if prob > threshold :
            cv2.circle(frameCopy, (int(point[0]), int(point[1])), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frameCopy, "{}".format(i), (int(point[0]), int(point[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

            # Add the point to the list if the probability is greater than the threshold
            points.append((int(point[0]), int(point[1])))
        else :
            points.append(None)

    # Draw Skeleton
    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], (0, 255, 255), 2)
            cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.circle(frame, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
    return points

def getFeatureVector(points):
    FeatureVector=[]
    maxLen=0
    if points[2] and points[4]:
        #print((points[2][0]-points[4][0])**2+(points[2][1]-points[4][1])**2)
        maxLen=math.sqrt((points[2][0]-points[4][0])**2+(points[2][1]-points[4][1])**2) #Długość kciuka
    else:
        maxLen=1

    for pair in Learn_pairs:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            FeatureVector.append(math.sqrt((points[partA][0]-points[partB][0])**2+(points[partA][1]-points[partB][1])**2)/maxLen)
        else:
            FeatureVector.append(0)


        #FeatureVector.append(math.atan2(dy, dx)) #obliczanie kątów pomiędzy elementami
        #for i in range(22):
            #points[i]=

    return FeatureVector

def createBase():
    allVectors = []
    pathNum="Numbers/*.png"
    pathAlph="Alphabet/*.png"
    for file in glob.glob(pathNum,recursive = True):
        print(file)
        allVectors.append([getFeatureVector(getPointsFromPicture(file)),os.path.relpath(file, 'Numbers')[:-4]])
        #print(os.path.relpath(file, 'Numbers')[:-4])

    for file in glob.glob(pathAlph, recursive=True):
        print(file)
        allVectors.append([getFeatureVector(getPointsFromPicture(file)),os.path.relpath(file, 'Alphabet')[:-4]])

    print(allVectors)
    with open('FVectors', 'wb') as fp:
        pickle.dump(allVectors, fp)

def loadVectors(path):
    ##LoadedVectors = []

    with open(path, 'rb') as fp:
        LoadedVectors = pickle.load(fp)
    #print(np.asarray(LoadedVectors).shape)
    return LoadedVectors

#createBase()
FeatureVectors=loadVectors("FVectors")
#print(FeatureVectors)


def signIdentification(present_Vector,FeatureVectors):
    maxSi =0
    sign=""

    B=present_Vector

    for Vector in FeatureVectors:
        A=Vector[0]
        #print(A)
        #print(len(A))
        try:
            Similarity = 1 - spatial.distance.cosine(A, B)
        except:
            print("Czegoś brakuje")
            Similarity=0;
        if Similarity>maxSi:
            maxSi=Similarity
            sign=Vector[1]
        #print("Prawdopodobieństwo:",Vector[1],": ",Similarity)

    if maxSi<0.7:
        sign=""
    return sign, maxSi

path="Numbers/2.png"
#path="Alphabet/B.png"
path="Test/TestL.png"
#print(signIdentification(getFeatureVector(getPointsFromPicture(path)),FeatureVectors))




#cv2.namedWindow('Output-Keypoints', cv2.WINDOW_NORMAL)
#cv2.namedWindow('Output-Skeleton', cv2.WINDOW_NORMAL)
#cv2.imshow('Output-Keypoints', frameCopy)
#cv2.imshow('Output-Skeleton', frame)


#cv2.imwrite('Output-Keypoints.jpg', frameCopy)
#cv2.imwrite('Output-Skeleton.jpg', frame)

#print("Total time taken : {:.3f}".format(time.time() - t))

#cv2.waitKey(0)

#print(getFeatureVector(getPointsFromPicture(path)))