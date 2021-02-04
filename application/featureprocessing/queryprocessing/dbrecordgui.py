import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image,ImageTk
import cv2

import application.featureprocessing.queryprocessing.previewvideo as query_preview
import application.featureprocessing.queryprocessing.querydb as query_db

'''
    module for the class of showing the gui and options associated with 
    a certain record gotten from the database
'''


class DBRecord:
    #class variables
    instances_created=instances_destroyed=0
    video_file_path=video_cap=None

    #grand parent window is the parent window to the parent window
    grand_parent_window=parent_window=None #it will be set before the class is called
    table_name=None
    cursor=None


    def __init__(self,parent_frame,row_no,col_no,image=None,
                    start_frame_time=None,end_frame_time=None,
                    colour_descriptor=None,shape_descriptor=None):

        DBRecord.instances_created+=1 #updating the class variable
        #create the frame and label that will be used for showing the image thumbnail, together with
        #some options for the image

        self.tk_image=None 

        if image is not None:
            rgb_image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            pil_image=Image.fromarray(rgb_image)
            self.tk_image=ImageTk.PhotoImage(pil_image)

        self.start_frame_time=start_frame_time
        self.end_frame_time=end_frame_time

        self.colour_descriptor=colour_descriptor
        self.shape_descriptor=shape_descriptor

        self.frame=ttk.Frame(parent_frame,width=275,height=275,border=1,relief="solid")
        self.label=ttk.Label(self.frame,text="Thumbnail Image {}".format(DBRecord.instances_created)
                    ,compound="bottom")
        self.label['image']=self.tk_image
        self.label.image=self.tk_image

        self.preview_btn=ttk.Button(self.frame,text="Preview\nVideo",command=self.previewVideo)
        self.search_btn=ttk.Button(self.frame,
                                    text="   Search using\nthumbnail image",
                                    command=self.searchUsingThumbnailGUI
                                )

        self.frame.grid(row=row_no,column=col_no,padx=5,pady=5)
        self.label.grid(row=0,column=0,columnspan=5)        
        self.preview_btn.grid(row=1,column=0,columnspan=2,sticky="NE")
        self.search_btn.grid(row=1,column=2,columnspan=3,sticky="NW")
    
    def previewVideo(self):
        if DBRecord.video_file_path is None:
            message="No video selected\nPlease select video to use"
            messagebox.showinfo(title="No Video",message=message)
            return
        
        if DBRecord.video_cap is None:
            DBRecord.video_cap=cv2.VideoCapture(DBRecord.video_file_path)
        
        #we set the video capture object to the time saved in the database
        DBRecord.video_cap.set(cv2.CAP_PROP_POS_MSEC,self.start_frame_time)
        query_preview.PreviewVideo(grand_parent_window=self.grand_parent_window,
                                root_window=DBRecord.parent_window,video_cap=DBRecord.video_cap,
                                start_frame_time=self.start_frame_time,end_frame_time=self.end_frame_time,
                                cursor=DBRecord.cursor)
    
    def configureThumbnailWindow(self):
        self.thumbnail_window.title("thumbnail image search")
        self.thumbnail_window.geometry("250x100+550+250")
        self.thumbnail_window.resizable(False,False)
    
    def searchUsingThumbnailGUI(self):

        #we create the gui for options to search using thumbnail
        self.thumbnail_window=tk.Toplevel(DBRecord.parent_window)
        self.configureThumbnailWindow()
        self.thumbnail_frame=ttk.Frame(self.thumbnail_window)

        self.descriptor_choice=tk.StringVar()

        radiobtn_1=ttk.Radiobutton(self.thumbnail_frame,
                                    text=" Use both descriptors ",
                                    variable=self.descriptor_choice,
                                    value="both"
                                )
        radiobtn_2=ttk.Radiobutton(self.thumbnail_frame,
                                    text="Use colour descriptor only",
                                    variable=self.descriptor_choice,
                                    value="colour"
                                )
        radiobtn_3=ttk.Radiobutton(self.thumbnail_frame,
                                    text="Use shape descriptor only",
                                    variable=self.descriptor_choice,
                                    value="shape"
                                )

        self.thumbnail_search_btn=ttk.Button(self.thumbnail_frame,
                                             text="Start Search & Retrieval",
                                             command=self.searchUsingThumbnail
                                          )
        
        self.descriptor_choice.set("both")

        self.thumbnail_frame.grid()
        radiobtn_1.grid(row=0,column=0,columnspan=3,rowspan=2,padx=0,pady=(1,2))
        radiobtn_2.grid(row=2,column=0,columnspan=4,rowspan=2,padx=0,pady=2)
        radiobtn_3.grid(row=4,column=0,columnspan=4,rowspan=2,padx=0,pady=2)
        self.thumbnail_search_btn.grid(row=6,column=0,columnspan=4,rowspan=2,padx=(0,3),pady=2)
    
    def searchUsingThumbnail(self):
        search_choice=self.descriptor_choice.get()

        query="SELECT * FROM {}".format(DBRecord.table_name)
        
        if search_choice=="both":
            query_db.DatabaseQuery(cursor_obj=DBRecord.cursor,query=query,
                                    query_shape_descriptor=self.shape_descriptor,
                                    query_colour_descriptor=self.colour_descriptor,
                                    table_name=DBRecord.table_name
                                )
        elif search_choice=="shape":
           query_db.DatabaseQuery(cursor_obj=DBRecord.cursor,query=query,
                                    query_shape_descriptor=self.shape_descriptor,
                                    table_name=DBRecord.table_name
                                )
        elif search_choice=="colour":
           query_db.DatabaseQuery(cursor_obj=DBRecord.cursor,query=query,
                                    query_colour_descriptor=self.colour_descriptor,
                                    table_name=DBRecord.table_name
                                )




    def __del__(self):
        DBRecord.instances_destroyed+=1

        #checks to see if all the instances of the class have been destroyed
        if DBRecord.instances_destroyed==DBRecord.instances_created:
            #after all instances are destroyed, we reset the class variables to their default values
            DBRecord.instance_destroyed=DBRecord.instances_created=0
            DBRecord.video_file_path=None
            DBRecord.video_cap=None