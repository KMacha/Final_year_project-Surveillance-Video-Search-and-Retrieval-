import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog,messagebox
from PIL import Image,ImageTk
import random
import numpy as np
import pickle

import scrollableframe as sf

class ShowThumbnail:
    times_called=0 #class variable 

    def __init__(self,parent_frame,row_no,col_no,image=None,
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

        self.frame=ttk.Frame(parent_frame,width=275,height=275,border=1,relief="solid")
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
        screen_width=self.query_window.winfo_screenwidth()
        screen_height=self.query_window.winfo_screenheight()

        self.height=screen_height-170
        self.width=screen_width-200

        #we set the width manually if the calculated one is small
        if self.width<=0:
            self.width=800 if screen_width>800 else screen_width
        
        if self.height<=0:
            self.height=500 if screen_height>500 else screen_height


        self.query_window.geometry("+50+10") #setting the position only

        self.query_window.title("Retrieval Results")
        self.query_window.maxsize(width=screen_width-50,height=screen_height-60)

    def __init__(self,cursor_obj,query,query_shape_descriptor=None,
                query_colour_descriptor=None):
        '''
            a record fetched from the db is a tuple of
            id, --> at index 0
            classifier_name,  --> at index 1
            thumbnail, -->at index 2
            colour_descriptor, -->at index 3
            shape_descriptor, -->at index 4
            start_frame_time, -->at index 5
            end_frame_time -->at index 6

        '''

        self.cursor=cursor_obj

        self.cursor.execute(query)

        if self.cursor.rowcount==0:
            message="No Records found"
            messagebox.showinfo(title="No Records",message=message)
            return

        #list of values fetched from the db
        self.records_list=self.cursor.fetchall()
        self.randomise=True

        self.query_window=tk.Toplevel()
        self.configureMainWindow()
        self.main_frame=ttk.Frame(self.query_window)

        self.scrollable_frame_obj=sf.ScrollableFrame(self.main_frame,width=self.width,height=self.height,auto_scroll=False)
        self.scrollable_frame=self.scrollable_frame_obj.getFrame()

        self.createUniversalOptions()

        self.main_frame.grid(row=1,column=0)

        #when there are no descriptors, it means we use only the category,i.e. 
        # just retrieve the records from the database and show them to the user randomly
        if (query_shape_descriptor is None) and (query_colour_descriptor is None):
            #we show some sample records
            self.showRecords()

            
        else:
            if query_shape_descriptor is not None:
                self.shape_cost=self.calculateShapeDistance(query_shape_descriptor)
            
            if query_colour_descriptor is not None:
                self.colour_cost=self.calculateColourDistance(query_colour_descriptor)
            
            self.combined_cost=self.combineBoth(query_shape_descriptor,query_colour_descriptor)

            self.records_list=list(self.combined_cost.keys())
            self.costs=list(self.combined_cost.values())

            self.randomise=False
            self.showRecords(randomise=self.randomise)
    
    def createUniversalOptions(self):
        #this basically creates the option of asking the user if they want to see 
        #all the retrieval results
        self.options_frame=ttk.Frame(self.query_window)
        
        self.records_retrieved_label=ttk.Label(self.options_frame)
        self.records_retrieved_label['text']="Retrieved {} Record(s)".format(len(self.records_list))

        self.shown_records_label=ttk.Label(self.options_frame)
        self.shown_records_label["text"]="Number of record(s) on display:"

        self.no_shown_records_label=ttk.Label(self.options_frame)

        self.see_all_btn=ttk.Button(self.options_frame,text="Display All Results",
                                    command=self.showAllRecords)

        self.options_frame.grid(row=0,column=0,columnspan=5)
        
        self.records_retrieved_label.grid(row=0,column=0,columnspan=3,sticky="W",padx=5)
        self.shown_records_label.grid(row=1,column=0,columnspan=4,sticky="W",padx=(5,0))
        self.no_shown_records_label.grid(row=1,column=4,sticky="W")
        self.see_all_btn.grid(row=0,column=5,padx=5,rowspan=2,columnspan=3)


    
    def showRecords(self,show_all=False,randomise=True):

        if not show_all:
            self.no_records=10 if len(self.records_list)>=10 else len(self.records_list)

            #sample no_records record to display
            if randomise:
                display_records_list=random.sample(self.records_list,self.no_records)
            else:
                display_records_list=self.records_list[:self.no_records]
        else:
            display_records_list=self.records_list
            self.no_records=len(self.records_list)
        
        #display number of records that are currently are been shown
        self.no_shown_records_label["text"]=self.no_records

        row=0
        column=0

        for record in display_records_list:
            image=pickle.loads(record[2])
            if column==5:
                row+=1
                column=0
            
            ShowThumbnail(parent_frame=self.scrollable_frame,row_no=row,col_no=column,image=image)
            column+=1
        
        # self.scrollable_frame.grid(row=1,column=0)
    
    def showAllRecords(self):
        if self.no_records==len(self.records_list):
            messagebox.showinfo(title=" ",message="Already displaying all records")
        else:
            self.showRecords(show_all=True)
    
    def euclideanDistance(self,a,b):
        return np.sqrt(np.sum((a-b)**2))
    
    def calculateShapeDistance(self,query_shape_descriptor):
        '''
            a record fetched from the db is a tuple of
            id, --> at index 0
            classifier_name,  --> at index 1
            thumbnail, -->at index 2
            colour_descriptor, -->at index 3
            shape_descriptor, -->at index 4
            start_frame_time, -->at index 5
            end_frame_time -->at index 6

        '''
        #it will be a dict of record_id: cost
        cost_dict=dict()
        for record in self.records_list:
            #record is one record fetched from the db
            record_shape_descriptor=pickle.loads(record[4])
            cost_dict[record]=self.euclideanDistance(query_shape_descriptor,record_shape_descriptor)
        
        return cost_dict
        

    def calculateColourDistance(self,query_colour_descriptor):
        '''
            a record fetched from the db is a tuple of
            id, --> at index 0
            classifier_name,  --> at index 1
            thumbnail, -->at index 2
            colour_descriptor, -->at index 3
            shape_descriptor, -->at index 4
            start_frame_time, -->at index 5
            end_frame_time -->at index 6

        '''
        cost_dict=dict()
        for record in self.records_list:
            #record is one record fetched from the db
            record_colour_descriptor=pickle.loads(record[3])
            cost_dict[record]=self.euclideanDistance(query_colour_descriptor,record_colour_descriptor)
        
        
        return cost_dict
    
    def combineBoth(self,query_shape_descriptor,query_colour_descriptor):
        #it combines the cost of both the shape and the colour
        if (query_shape_descriptor is not None) and (query_colour_descriptor is None):
            combined_cost=self.shape_cost
        elif (query_shape_descriptor is None) and (query_colour_descriptor is not None):
            combined_cost=self.colour_cost
        else:
            combined_cost={aa[0]:aa[1]*0.5+bb[1]*0.5 
                            for aa,bb in zip(self.shape_cost.items(),self.colour_cost.items())}

            # self.combined_cost=self.combineBoth()

        return {k: v for k, v in sorted(combined_cost.items(), key=lambda item: item[1])}