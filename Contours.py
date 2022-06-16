from queue import Empty
import cv2
from cv2 import rectangle 
import numpy as np
import os
import matplotlib.pyplot as plt
def sortBBox(listboxmax,listboxmin):
    for i in range(len(listboxmax)):
        for j in range(0,len(listboxmax)-i-1):
            if listboxmax[j][0] > listboxmax[j+1][0]:
                temp = listboxmax[j]
                listboxmax[j] = listboxmax[j+1]
                listboxmax[j+1] = temp
               
                temp1 = listboxmin[j]
                listboxmin[j] = listboxmin[j+1]
                listboxmin[j+1] = temp1
    return listboxmax, listboxmin

def padding(bin):
    #bottom
    for i in range(bin.shape[1]):
        bin[bin.shape[0]-2][i]=0
        bin[bin.shape[0]-1][i]=0
    #top
    for i in range(bin.shape[1]):
        bin[0][i]=0
        bin[1][i]=0
    #left
    for i in range(bin.shape[0]):
        bin[i][bin.shape[1]-2]=0
        bin[i][bin.shape[1]-1]=0
    #right
    for i in range(bin.shape[0]):
        bin[i][0]=0
        bin[i][1]=0
    return bin
def coverGreemColorToWhiteColor(image):
    height,width = image.shape[0],image.shape[1]
    for loop1 in range(height):
        for loop2 in range(width):
            r,g,b = image[loop1,loop2]
            if g > 1+r and g>1+b:
                image[loop1,loop2] = 255,255,255
    return image
def getBoundingBox(contours):
    listboxmin = []
    listboxmax = []
    for id in range(0,len(contours)):
        listx=[]
        listy=[]
        for coor in contours[id]:
            listx.append(coor[0][0])
            listy.append(coor[0][1])
        minx = np.min(listx)
        miny = np.min(listy)
        maxx = np.max(listx)
        maxy = np.max(listy)
        listboxmin.append((minx,miny))
        listboxmax.append((maxx,maxy))
    return listboxmax, listboxmin
def removeBadContours(image,listboxmax,listboxmin):
    area = []
    areaHeight = []
    areaWidth = []
    bettetContours = []
    multiChar = []
    listChar = []
    listboxmax,listboxmin = sortBBox(listboxmax,listboxmin)
    for i in range(len(listboxmax)):
        w = listboxmax[i][0] - listboxmin[i][0]
        h = listboxmax[i][1] - listboxmin[i][1]
        areaHeight.append(float(h))
        areaWidth.append(float(w))
        area.append(w*h)
    avgAreaHeight= np.average(areaHeight)
    avgAreaWidth= np.average(areaWidth)
    avgArea = np.average(area)
    for i in range(len(listboxmax)):
        w = listboxmax[i][0] - listboxmin[i][0]
        h = listboxmax[i][1] - listboxmin[i][1]
        if h > avgAreaHeight/1.9: 
            bettetContours.append([listboxmin[i],listboxmax[i]])
        elif w < h*2 and h > avgAreaHeight/2.5:
            bettetContours.append([listboxmin[i],listboxmax[i]])
    id = 0
    for i in range(len(bettetContours)): 
        w = bettetContours[i][1][0] - bettetContours[i][0][0] 
        h = bettetContours[i][1][1] - bettetContours[i][0][1] 
        if w > h and w >1.3*h and h * w > avgArea :
            multiChar = [bettetContours[i][0],bettetContours[i][1]]
            imgcp = image
            imgcp = imgcp[multiChar[0][1]:multiChar[1][1],multiChar[0][0]:multiChar[1][0]]
            id+=1
            w = multiChar[1][0] - multiChar[0][0] 
            h = multiChar[1][1] - multiChar[0][1] 
            if w > avgAreaWidth and w < 2.5*avgAreaWidth:
                imgcp2 = image[multiChar[0][1]:multiChar[1][1],multiChar[0][0]+int(w/2):multiChar[1][0]]
                imgcp2 = padding(imgcp2)
                contourss,hierachy=cv2.findContours(imgcp2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                bboxmax,bboxmin = getBoundingBox(contourss)
                bbox = []
                for k in range(len(bboxmax)):
                    bbox.append([bboxmin[k],bboxmax[k]])
                bigArea = 0
                for l in bbox:
                    w1 = l[1][0] - l[0][0]
                    h1 = l[1][1] - l[0][1]
                    if w1*h1 >bigArea:
                        bigArea = w1*h1
                if 2*bigArea > (w/2)*h:
                    listChar.append([(multiChar[0][0]-2,multiChar[0][1]-2),(multiChar[1][0]-int(w/2)+2,multiChar[1][1]+2)])
                    listChar.append([(multiChar[0][0]+int(w/2)-2,multiChar[0][1]-2),(multiChar[1][0]+2,multiChar[1][1]+2)])
                else:
                    listChar.append([(multiChar[0][0]-2,multiChar[0][1]-2),(multiChar[1][0]+2,multiChar[1][1]+2)])
            elif w < 3.5*avgAreaWidth and w >= 2.5*avgAreaWidth:
                listChar.append([(multiChar[0][0]-2,multiChar[0][1]-2),(multiChar[1][0]-int(w/3)*2+2,multiChar[1][1]+2)])
                listChar.append([(multiChar[0][0]+int(w/3)-2,multiChar[0][1]-2),(multiChar[1][0]-int(w/3)+2,multiChar[1][1]+2)])
                listChar.append([(multiChar[1][0]-int(w/3)-2,multiChar[0][1]-2),(multiChar[1][0]+2,multiChar[1][1]+2)])
        else:
            listChar.append([(bettetContours[i][0][0],bettetContours[i][0][1]),(bettetContours[i][1][0],bettetContours[i][1][1])])
    return listChar
def splitCharFromSerialNo(image):
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    SerialNo = image
    SerialGray = coverGreemColorToWhiteColor(SerialNo)
    SerialGray = cv2.cvtColor(SerialGray, cv2.COLOR_BGR2GRAY)
    # Inverse 
    m, dev = cv2.meanStdDev(SerialGray)
    ret, thresh = cv2.threshold(SerialGray, m[0][0] - 0.5*dev[0][0], 255, cv2.THRESH_BINARY_INV)
    # Padding
    thresh = padding(thresh)
    # Finding countours
    contours,hierachy=cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    listboxmax,listboxmin = getBoundingBox(contours)
    listChar = removeBadContours(thresh,listboxmax,listboxmin)
    return listChar
img = cv2.imread('/home/anlab/ANLAB/VisualCode/Contours/SplitHandWriting/TestImage/InputSerialNum/MFG No.032212693 LK-21VHU-02.jpg')
listChar = splitCharFromSerialNo(img)

cv2.waitKey(0)
cv2.destroyAllWindows()

