import tkinter as tk 
from tkinter import ttk
from PIL import Image,ImageTk
import cv2

class PreviewVideo:

    def __init__(self,root_window,video_path,video_name):

        self.preview_window=tk.Toplevel(root_window)
        self.preview_window.title(video_name)
        self.preview_window.geometry("640x530+300+50")

        self.video_cap=cv2.VideoCapture(video_path)

        self.playing_speed=10

        self.createGUI()

        self.showVideo()
    
    def createGUI(self):
        self.preview_frame=ttk.Frame(self.preview_window,width=640,height=600)
        self.preview_label=ttk.Label(self.preview_frame)
        
        #buttons to effect the playing the video
        self.actions_frame=ttk.Frame(self.preview_frame)

        #to start the video again from the start
        self.again_btn=ttk.Button(self.actions_frame,text="Preview Again",command=self.previewAgain)

        self.current_speed=tk.StringVar()
        self.current_speed.set(self.playing_speed)
        self.speed_label=ttk.Label(self.actions_frame,text="Current Speed:")
        self.current_speed_label=ttk.Label(self.actions_frame,textvariable=self.current_speed)

        #spinbox to increase or decrease the speed
        self.speed_adjust_label=ttk.Label(self.actions_frame,text="Speed:")
        self.speed_adjust=ttk.Scale(self.actions_frame,from_=1.0,to=100.0,orient="horizontal",length=200,command=self.updateSpeed)
        self.speed_adjust.set(self.playing_speed)

        self.quit_btn=ttk.Button(self.actions_frame,text="Exit",command=self.preview_window.destroy)

        self.preview_frame.grid(row=0,column=0)
        self.preview_label.grid(row=0,column=0)

        self.actions_frame.grid(row=1,column=0)

        self.speed_label.grid(row=0,column=0)
        self.current_speed_label.grid(row=0,column=1)

        self.again_btn.grid(row=0,column=2)
        self.speed_adjust_label.grid(row=0,column=3)
        self.speed_adjust.grid(row=0,column=4)
        self.quit_btn.grid(row=0,column=5)
    
    def updateSpeed(self,current_scale_value):
        #we update the playing speed as set by the user
        self.playing_speed=int(float(current_scale_value))
        self.current_speed.set(self.playing_speed)
    
    def previewAgain(self):

        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES,1)

        #we check if the video sequence had ended, if it had ended, we call the method again
        #if it had not ended, we allow it to continue.
        #Calling the function again when it has not ended causes the label not to display anything else
        if not self.ret:
            self.showVideo()
        
    
    def showVideo(self):

        self.ret,frame=self.video_cap.read()

        #we need self.ret so that we can be able to use it in the previewAgain method
        if not self.ret:
            return
        
        frame=cv2.resize(frame,(640,480))
        #frame=cv2.flip(frame,1)
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        pil_image=Image.fromarray(frame)
        tk_image=ImageTk.PhotoImage(pil_image)

        self.preview_label.image=tk_image

        self.preview_label.configure(image=tk_image)

        self.preview_label.after(self.playing_speed,self.showVideo)

