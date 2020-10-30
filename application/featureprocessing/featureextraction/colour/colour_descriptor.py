#!/usr/bin/python

import numpy as np
import cv2
import imutils

class ColourDescriptor:
    def __init__(self,bins):
        self.bins=bins #the number of bins for our histogram
    
    def describe(self,image):
        image=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        features=[]

        (h,w)=image.shape[:2] #the image height and width

        #get center of the image
        (cx,cy)=(int(w*0.5),int(h*0.5))

        #we divide the image into different segments
        #top left, top right, bottom right bottom left
        #find why we need to do this in the book
        imagesegments=[
            (0,cx,0,cy), #top left
            (cx,w,0,cy), #top right
            (cx,w,cy,h), #bottom right
            (0,cx,cy,h) #bottom left
        ]

        #we construct an elliptical mast=k representing the center of the image
        (axesx,axesy)=(int(w*0.75)//2,int(h*0.75)//2)
        ellipmask=np.zeros(image.shape[:2],dtype="uint8")
        cv2.ellipse(ellipmask,(cx,cy),(axesx,axesy),0,0,360,255,-1)

        for (startx,endx,starty,endy) in imagesegments: #go through each segment
            cornermask=np.zeros(image.shape[:2],dtype="uint8")
            cv2.rectangle(cornermask,(startx,starty),(endx,endy),255,-1)
            cornermask=cv2.subtract(cornermask,ellipmask)
            
            hist=self.histogram(image,cornermask) #get the list of histograms
            features.extend(hist)
        
        hist=self.histogram(image,ellipmask)
        features.extend(hist)

        return np.array(features)
    
    def histogram(self,image,mask):
        hist=cv2.calcHist([image],[0,1,2],mask,self.bins,[0,180,0,256,0,256])

        #we normalise the histogram depending on the version of open cv we are using
        if imutils.is_cv2():
            hist=cv2.normalize(hist).flatten()
        else:
            hist=cv2.normalize(hist,hist).flatten()
        

        return hist