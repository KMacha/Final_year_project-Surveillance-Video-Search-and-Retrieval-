import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog,messagebox
from PIL import Image,ImageTk
import random
import pickle

class ShowThumbnail:
    times_called=0 #class variable 

    def __init__(self,parent_window,row_no,col_no,image=None,
                    start_frame_time=None,end_frame_time=None):

        ShowThumbnail.times_called+=1 #updating the class variable
        #create the frame and label that will be used for showing the image thumbnail, together with
        #some options for the image

        self.tk_image=None 

        if image is not None:
            rgb_image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            pil_image=Image.fromarray(rgb_image)
            self.tk_image=ImageTk.PhotoImage(pil_image)

        self.start_frame_time=start_frame_time
        self.end_frame_time=end_frame_time

        self.frame=ttk.Frame(parent_window,width=275,height=275,border=1,relief="solid")
        self.label=ttk.Label(self.frame,text="Thumbnail Image {}".format(ShowThumbnail.times_called)
                    ,compound="bottom")
        self.label['image']=self.tk_image
        self.label.image=self.tk_image

        self.preview_btn=ttk.Button(self.frame,text="Preview\nVideo")
        self.search_btn=ttk.Button(self.frame,text="   Search using\nthumbnail image")

        self.frame.grid(row=row_no,column=col_no,padx=5,pady=5)
        self.label.grid(row=0,column=0,columnspan=5)        
        self.preview_btn.grid(row=1,column=0,columnspan=2,sticky="NE")
        self.search_btn.grid(row=1,column=2,columnspan=3,sticky="NW")
        



class DatabaseQuery:
    def configureMainWindow(self):
        self.query_window.title("Retrieval Results")

    def __init__(self,cursor_obj,query,query_image=None,binary_image=None,use_category_only=False):
        
        self.cursor=cursor_obj

        #when use_category_only is true, it means we search the database using only  for the particular
        if use_category_only:
            self.cursor.execute(query)

            if self.cursor.rowcount==0:
                message="No Records found matching chosen category"
                messagebox.showinfo(title="No Records",message=message)
            else:
                #we show some sample records
                self.records_list=self.cursor.fetchall()
                self.query_window=tk.Toplevel()
                self.configureMainWindow()
                self.createUniversalOptions()
                self.showRecords()
    
    def createUniversalOptions(self):
        #this basically creates the option of asking the user if they want to see 
        #all the retrieval results
        self.options_frame=ttk.Frame(self.query_window)
        
        self.records_retrieved_label=ttk.Label(self.options_frame)
        self.records_retrieved_label['text']="Retrieved {} Record(s), Number of record(s) on display: "\
                                .format(len(self.records_list))

        self.records_shown_label=ttk.Label(self.options_frame)

        self.see_all_btn=ttk.Button(self.options_frame,text="Display All Results",
                                    command=self.showAllRecords)

        self.options_frame.grid(row=0,column=0,columnspan=5)
        
        self.records_retrieved_label.grid(row=0,column=0)
        self.records_shown_label.grid(row=0,column=1)
        self.see_all_btn.grid(row=0,column=2,padx=5)


    
    def showRecords(self,show_all=False):

        if not show_all:
            self.no_records=10 if len(self.records_list)>=10 else len(self.records_list)

            #sample no_records record to display
            display_records_list=random.sample(self.records_list,self.no_records)
        else:
            display_records_list=self.records_list
            self.no_records=len(self.records_list)
        
        #display number of records that are currently are been shown
        self.records_shown_label["text"]=self.no_records

        row=1
        column=0

        for record in display_records_list:
            image=pickle.loads(record[2])
            if column==5:
                row+=1
                column=0
            
            ShowThumbnail(parent_window=self.query_window,row_no=row,col_no=column,image=image)
            column+=1
    
    def showAllRecords(self):
        if self.no_records==len(self.records_list):
            messagebox.showinfo(title=" ",message="Already displaying all records")
        else:
            self.showRecords(show_all=True)