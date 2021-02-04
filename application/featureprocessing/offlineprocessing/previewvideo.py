import tkinter as tk 
from tkinter import ttk
from PIL import Image,ImageTk
import cv2

class PreviewVideo:

    def __init__(self,root_window,video_path=None,title="Preview",video_cap=None,
                start_frame_time=None,end_frame_time=None):

        self.preview_window=tk.Toplevel(root_window)
        self.preview_window.title(title)
        self.preview_window.geometry("640x530+300+50")

        self.pause=False

        self.video_cap=video_cap if (video_cap is not None) else cv2.VideoCapture(video_path)

        self.start_frame_time=start_frame_time
        self.end_frame_time=end_frame_time

        self.playing_speed=10
    
    def preview(self):
        self.createGUI()
        self.showVideo()
    
    def createGUI(self):
        self.preview_frame=ttk.Frame(self.preview_window,width=640,height=600)
        self.preview_label=ttk.Label(self.preview_frame)
        
        #buttons to effect the playing the video
        self.actions_frame=ttk.Frame(self.preview_frame)

        #to start the video again from the start
        self.again_btn=ttk.Button(self.actions_frame,text="Preview Again",command=self.previewAgain)

        #to pause and play the video
        self.pause_play_btn=ttk.Button(self.actions_frame,text="Pause",command=self.pausePlayVideo)

        self.current_speed=tk.StringVar()
        self.current_speed.set(self.playing_speed)
        self.speed_label=ttk.Label(self.actions_frame,text="Play Speed:")
        self.current_speed_label=ttk.Label(self.actions_frame,textvariable=self.current_speed)

        #spinbox to increase or decrease the speed
        self.speed_adjust_label=ttk.Label(self.actions_frame,text="Speed:")
        self.speed_adjust=ttk.Scale(self.actions_frame,from_=1.0,to=100.0,orient="horizontal",length=150,command=self.updateSpeed)
        self.speed_adjust.set(self.playing_speed)

        self.quit_btn=ttk.Button(self.actions_frame,text="Exit",command=self.preview_window.destroy)

        self.preview_frame.grid(row=0,column=0)
        self.preview_label.grid(row=0,column=0)

        self.actions_frame.grid(row=1,column=0)

        self.speed_label.grid(row=0,column=0)
        self.current_speed_label.grid(row=0,column=1)

        self.again_btn.grid(row=0,column=2)
        self.pause_play_btn.grid(row=0,column=3)

        #leave one column, will be useful for when we are adding for querying
        self.speed_adjust_label.grid(row=0,column=5)
        self.speed_adjust.grid(row=0,column=6)
        self.quit_btn.grid(row=0,column=7)
    
    def updateSpeed(self,current_scale_value):
        #we update the playing speed as set by the user
        self.playing_speed=int(float(current_scale_value))
        self.current_speed.set(self.playing_speed)
    
    def previewAgain(self):
        if self.start_frame_time!=None:
            self.video_cap.set(cv2.CAP_PROP_POS_MSEC,self.start_frame_time)
        else:
            self.video_cap.set(cv2.CAP_PROP_POS_MSEC,0)

        #we check if the video sequence had ended, if it had ended, we call the method again
        #if it had not ended, we allow it to continue.
        #Calling the function again when it has not ended causes the label not to display anything else
        if not self.ret:
            self.showVideo()
    
    def pausePlayVideo(self):
        self.pause=not self.pause #we basically unset/set the value of the pause variable

        if self.pause: #if video is paused
            #change button text to play
            self.pause_play_btn["text"]="Play"
        else: #if the video is not paused
            #change button text to pause
            self.pause_play_btn["text"]="Pause"

            #call the show video method again, sine after pauseing it was exited
            self.showVideo()

        
    
    def showVideo(self):
        if self.pause:
            return
        self.ret,self.frame=self.video_cap.read()

        #we need self.ret so that we can be able to use it in the previewAgain method
        if not self.ret:
            return
        
        self.frame=cv2.resize(self.frame,(640,480))
        #frame=cv2.flip(frame,1)
        frame=cv2.cvtColor(self.frame,cv2.COLOR_BGR2RGB)

        pil_image=Image.fromarray(frame)
        tk_image=ImageTk.PhotoImage(pil_image)

        self.preview_label.image=tk_image

        self.preview_label.configure(image=tk_image)

        if (self.end_frame_time!=None) and (self.video_cap.get(cv2.CAP_PROP_POS_MSEC)>=self.end_frame_time):
            #we set self.ret to be false so that when preview again is pressed, we can be able to 
            #replay
            self.ret=False
            return

        self.preview_label.after(self.playing_speed,self.showVideo)

