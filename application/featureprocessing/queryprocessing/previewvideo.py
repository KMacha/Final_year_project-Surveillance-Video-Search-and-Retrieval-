import cv2
import tkinter as tk
from tkinter import ttk
import application.featureprocessing.queryprocessing.querygui as query
import application.featureprocessing.offlineprocessing.previewvideo as preview

#inherits the PreviewVideo that had been made for the offline processing
class PreviewVideo(preview.PreviewVideo):

    def __init__(self,grand_parent_window,root_window,video_cap,start_frame_time,end_frame_time,cursor=None):
        super().__init__(root_window=root_window,video_cap=video_cap,
                        start_frame_time=start_frame_time,end_frame_time=end_frame_time)
        
        self.cursor=cursor
        self.grand_parent_window=grand_parent_window
        self.root_window=root_window
        self.preview()
        #in the actions frame, see the offlineprocessing.previewvideo, 
        #we are going to add an option for grabbing region of interest

        self.grab_roi_btn=ttk.Button(self.actions_frame,
                                        text="grab roi",
                                        command=self.GrabROI
                                    )
        
        self.grab_roi_btn.grid(row=0,column=4)
    

    def GrabROI(self):
        self.pause=False 
        #set to false to ensure after calling pauseplayvideo method, the video will be paused

        self.pausePlayVideo() # we start by first pausing the video

        #code to grab a roi using cv2
        from_center=False
        show_crosshair=False
        roi=cv2.selectROI("region of interest",self.frame,from_center,show_crosshair)

        if roi !=(0,0,0,0):
            img=self.frame[int(roi[1]):int(roi[1]+roi[3]),int(roi[0]):int(roi[0]+roi[2])]

            cv2.imshow("region of interest",img)

            if cv2.waitKey(0) & 0xff==ord('q'):
                cv2.destroyAllWindows()
        else:
            cv2.destroyAllWindows()
        
        self.root_window.destroy()
        #self.grand_parent_window.destroy()
        query.QueryProcessing(root_window=self.grand_parent_window,cursor_obj=self.cursor,
                                query_image=img
                            )
        
