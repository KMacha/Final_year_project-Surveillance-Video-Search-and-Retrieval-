#!/usr/bin/python

import cv2
import argparse
import imutils
import sys
import numpy as np
import time
import pybgs as bgs

class MovingRegion:

    def __init__(self,original_width,original_height):
        self.img_aspect_ratio=original_width/original_height

        self.new_width=200
        self.new_height=int(self.new_width*self.img_aspect_ratio)

        self.scale=(self.new_width/original_width,self.new_height/original_height)

        self.kernel=np.ones(shape=(3,3),dtype=np.uint8)

        self.vibe_algorithm=bgs.ViBe()
    
    def autoCanny(self,image):
        mean=image.mean()
        min_threshold=0.66*mean
        max_threshold=1.33*mean
        
        return cv2.Canny(image,min_threshold,max_threshold)


    def resizeImage(self,image,width=None,height=None,use_predefined=True):
        #when use_predefined is true we resize the image to a width of 200
        #then resize the image preserving the aspect ratio so that the image
        #doesn't get so much distorted

        if use_predefined:
            return cv2.resize(image,(self.new_width,self.new_height))
        else:
            if not width and not height: #if both are not set we return the image not resized
                return image

            elif not width: #if only the width is not set 
                width=height//self.img_aspect_ratio
            elif not height: #if only height is not set
                height=int(width*self.img_aspect_ratio)

            return cv2.resize(image,(width,height))

    def getDifferenceImage(self,gray_image_curr,gray_image_next):
        diff_image=cv2.absdiff(gray_image_curr,gray_image_next)

        adaptive_threshold=3*diff_image.mean()

        adaptive_threshold=15 if adaptive_threshold<15 else adaptive_threshold

        #we apply the threshold
        _,thresh=cv2.threshold(diff_image,adaptive_threshold,255,cv2.THRESH_BINARY)
        
        #cv2.imshow("threshold",cv2.resize(thresh,(640,480)))
        #we dilate the image
        dilated_image=cv2.dilate(thresh,self.kernel,iterations=1)

        #opened_image=cv2.morphologyEx(dilated_image,cv2.MORPH_OPEN,kernel,iterations=2)
        #closed_image=cv2.morphologyEx(opened_image,cv2.MORPH_CLOSE,kernel,iterations=1)


        #cv2.imshow("dilated",cv2.resize(dilated_image,(640,480)))
        return dilated_image
    
    def findMovingArea(self,frame):

        final_moving_area=self.vibe_algorithm.apply(frame)

        return final_moving_area

    def findValidContours(self,image):
        #since we are using open cv 4
        contours,_=cv2.findContours(image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        #contours=contours[1] if imutils.is_cv3() else contours[0]

        valid_contours=[]
        bigger_contours=[]
        bigger_rects=[]
        bigger_centroids=[] 

        for contour in contours:
            area=cv2.contourArea(contour)
            if area>=100:
                valid_contours.append(contour)
                bigger_contours.append(np.round(np.divide(contour,self.scale)).astype(np.int32))

                #we get the bounding rectangle of the bigger contours
                #we take advantage of the fact that the contour has just been appended thus it is
                #the last one in the list

                bigger_rects.append(cv2.boundingRect(bigger_contours[-1]))

                #we also find the centroids from the bigger contour
                #centroid_co_ords=np.squeeze(bigger_contours[-1].mean(axis=0))

                bigger_centroids.append(np.squeeze(bigger_contours[-1].mean(axis=0)))
        
        return valid_contours,bigger_contours,bigger_rects,np.array(bigger_centroids)


if __name__=="__main__":
    import os

    obj=MovingRegion(original_width=1280,original_height=720)

    video_path="/home/macha/Programming/School Final Year Project/project/videos/vtest.avi"

    video_cap=cv2.VideoCapture(video_path)

    if video_cap.isOpened():
        print("yes it is open")
    else:
        print("error while opening video capture")
        os.system("exit")
    

    while True:

        ret,frame=video_cap.read()

        if not ret: break

        moving_area=obj.findMovingArea(frame)

        cv2.imshow("frame",cv2.resize(frame,(640,480)))
        cv2.imshow("moving",cv2.resize(moving_area,(640,480)))

        if cv2.waitKey(30) & 0xff==ord('q'):
            video_cap.release()
            break
    
    cv2.destroyAllWindows()
