#!/usr/bin/python

import cv2
import argparse
import imutils
import sys
import numpy as np
import time

class MovingRegion:

    def __init__(self,original_width,original_height):
        self.img_aspect_ratio=original_width/original_height

        self.new_width=200
        self.new_height=int(self.new_width*self.img_aspect_ratio)

        self.scale=(self.new_width/original_width,self.new_height/original_height)

        self.kernel=np.ones(shape=(3,3),dtype=np.uint8)
    
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
    
    def findMovingArea(self,diff_image_1,diff_image_2,gray_image_curr):

        final_diff_image=cv2.bitwise_and(diff_image_1,diff_image_2)
        canny_curr_frame=self.autoCanny(gray_image_curr)

        #we do the canny comparisons 
        canny_diff_image_1=cv2.bitwise_and(canny_curr_frame,diff_image_1)
        canny_diff_image_2=cv2.bitwise_and(canny_curr_frame,diff_image_2)

        final_canny_diff_image=cv2.bitwise_or(canny_diff_image_1,canny_diff_image_2)

        final_moving_area=cv2.bitwise_or(final_diff_image,final_canny_diff_image)

        return final_moving_area

    def findValidContours(self,diff_image):
        #since we are using open cv 4
        contours,_=cv2.findContours(diff_image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
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
    pass
    # #ret,curr_frame=videocap.read()
    # #ret,frame=videocap.read()
    # #print(curr_frame.shape)
    
    # new_curr_frame=cv2.resize(curr_frame,(200,355))
    
    # if not ret:
    #     print("error when reading video")
    #     sys.exit(-1)

    # prev_frame=cv2.resize(curr_frame,(200,355))
    # next_frame=cv2.resize(frame,(200,355))
    # unresized_next_frame=frame.copy()

    # gray_image_prev=cv2.cvtColor(prev_frame,cv2.COLOR_BGR2GRAY)
    # gray_image_curr=cv2.cvtColor(new_curr_frame,cv2.COLOR_BGR2GRAY)
    # diff_image_1=getDifferenceImage(gray_image_prev,gray_image_curr)
    
    # while True:
    #     temp_curr_frame=new_curr_frame.copy() 

    #     gray_image_curr=cv2.cvtColor(new_curr_frame,cv2.COLOR_BGR2GRAY)

    #     gray_image_next=cv2.cvtColor(next_frame,cv2.COLOR_BGR2GRAY)

    #     #since in the next step the previous frame will be the value of the current frame
    #     #and the current frame will be the value of the next frame
    #     #there is no need to calculate diff_image_1 again, since it will be the similar
    #     #to the previous copy of diff_image_2
        
    #     diff_image_2=getDifferenceImage(gray_image_curr,gray_image_next)

    #     diff_image=cv2.bitwise_and(diff_image_1,diff_image_2)
    #     moving_area=cv2.bitwise_xor(diff_image,diff_image_2)

    #     valid_contours,bigger_contours=findValidContours(diff_image)
    #     #print("valid contours found for image: {}".format(len(valid_contours)))
    #     cv2.putText(temp_curr_frame,"No Valid contours: "+str(len(valid_contours)),(5,10),cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5,color=(0,0,255),thickness=2)
    #     cv2.drawContours(temp_curr_frame,valid_contours,-1,(127,200,0),2)
    #     cv2.imshow(" 3 frame differencing showing contours",temp_curr_frame)
        
    #     #cv2.putText(curr_frame,"No Valid contours: "+str(len(valid_contours)),(5,10),cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5,color=(0,0,255),thickness=2)
    #     #cv2.drawContours(curr_frame,bigger_contours,-1,(127,200,0),2)
        
    #     #resized_640_curr=cv2.resize(curr_frame,(640,480))
    #     #cv2.imshow("640*480",resized_640_curr)
        
    #     new_curr_frame=next_frame.copy()
    #     curr_frame=unresized_next_frame.copy()

    #     ret,frame=videocap.read()

    #     if not ret: break
        
    #     unresized_next_frame=frame.copy()
    #     next_frame=cv2.resize(frame,(200,355))

    #     #we set difference image 1 to be the copy of difference image 2
    #     diff_image_1=diff_image_2.copy() 