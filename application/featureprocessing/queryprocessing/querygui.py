import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog,messagebox
from PIL import Image,ImageTk

class QueryProcessing:

    def __init__(self,root_window):

        #the root window is the toplevel window which we are going to 
        #create the gui on

        self.root_window=root_window
        self.createGUI()

    def createGUI(self):
        self.main_query_frame=ttk.Frame(self.root_window,width=940,height=480)

        #create different label frames for the different parts of the query window
        self.query_image_frame=ttk.Labelframe(self.main_query_frame,text="Query Image",width=225,height=225)
        self.query_options_frame=ttk.Labelframe(self.main_query_frame,text="Search Options")
        self.processed_image_frame=ttk.Labelframe(self.main_query_frame,text="Processed image",width=225,height=225)
        self.processed_options_frame=ttk.Labelframe(self.main_query_frame,text="Config options")

        self.query_image_frame.configure(borderwidth=2,relief="sunken")
        self.processed_image_frame.configure(borderwidth=2,relief="sunken")

        self.query_options_frame.configure(borderwidth=2,relief="sunken")
        self.processed_options_frame.configure(borderwidth=2,relief="sunken")

        #labels to display the query image and the processed image
        self.query_image_label=ttk.Label(self.query_image_frame,compound="image",anchor="center")
        self.processed_image_label=ttk.Label(self.processed_image_frame,compound="image",anchor="center")

        #query and retrieval button
        self.query_retrieval_btn=ttk.Button(self.main_query_frame,text="Start Search & Retrieval")

        #search options
        self.createSearchOptions()
        

        #query buttons
        self.insert_btn=ttk.Button(self.main_query_frame,text="     Insert\nQuery Image",command=self.insertQueryImage)
        self.draw_btn=ttk.Button(self.main_query_frame,text="     Draw\nQuery Image")

        #processed image options
        self.createProcessedImageOptions()

        #we disable some frames until the query image has either been read or processed
        self.query_image_frame.state(['disabled'])
        self.processed_image_frame.state(['disabled'])
        self.processed_options_frame.state(['disabled'])

        #Query window layout
        
        self.main_query_frame.grid(row=0,column=0)

        #main query frame layout
        self.query_image_frame.grid(row=0,column=0,columnspan=5,padx=(5,1),pady=5)
        self.query_options_frame.grid(row=0,column=5,sticky="NW",columnspan=3,padx=(1,5),pady=5)
        self.processed_image_frame.grid(row=0,column=8,columnspan=5,padx=(5,1),pady=5)
        self.processed_options_frame.grid(row=0,column=14,sticky="NW",columnspan=5,padx=(1,5),pady=5)

        #we set the grid propagate for the query image frame and the processed image frame to false
        self.query_image_frame.grid_propagate(False)
        self.processed_image_frame.grid_propagate(False)

        self.query_image_label.grid(row=0,column=0)
        self.processed_image_label.grid(row=0,column=0)

        self.insert_btn.grid(row=1,column=0,sticky="W",columnspan=2,padx=(5,0),pady=(0,5))
        self.draw_btn.grid(row=1,column=2,sticky="W",columnspan=2,padx=(0,5),pady=(0,5))
        self.query_retrieval_btn.grid(row=1,column=8,columnspan=3,padx=5,sticky="W")
        
        for grid_children in self.query_options_frame.grid_slaves():
            grid_children.grid_configure(padx=3,pady=3)
        
        for grid_children in self.processed_options_frame.grid_slaves():
            grid_children.grid_configure(padx=3,pady=3)
    
    def createSearchOptions(self):
        #the table selection combobox
        self.select_table_label=ttk.Label(self.query_options_frame,text="Choose DB table to search")
        self.table_list=ttk.Combobox(self.query_options_frame,state='readonly')
        self.table_list['values']=("None")

        self.use_colour_descriptor=tk.IntVar()
        self.colour_option_ckbtn=ttk.Checkbutton(self.query_options_frame,
                text="Use Colour descriptor",variable=self.use_colour_descriptor)

        self.use_shape_descriptor=tk.IntVar()
        self.shape_option_ckbtn=ttk.Checkbutton(self.query_options_frame,
                text="Use Shape descriptor",variable=self.use_shape_descriptor)
        
        self.category_var=tk.IntVar()
        self.category_option_ckbtn=ttk.Checkbutton(self.query_options_frame,
                text="Select particular category",variable=self.category_var)

        self.category_list=ttk.Combobox(self.query_options_frame,width=18,state="readonly")
        self.category_list['values']=("Person(M/F)","Bike(motorcycle/bicycle)","Car","Bus","Lorry","All","Other")
        self.search_category_btn=ttk.Button(self.query_options_frame,text="Retrieve From Category",width=19)

        #we disable some options until the query image is read and processed
        self.colour_option_ckbtn.state(['disabled','alternate'])
        self.shape_option_ckbtn.state(['disabled','alternate'])

        self.category_list.state(['disabled'])
        self.search_category_btn.state(['disabled'])

        #grid layout for the search options
        self.select_table_label.grid(row=0,column=0,columnspan=3,sticky="NW")
        self.table_list.grid(row=1,column=0,columnspan=3,sticky="NW")
        self.colour_option_ckbtn.grid(row=2,column=0,columnspan=3,sticky="NW")
        self.shape_option_ckbtn.grid(row=3,column=0,columnspan=3,sticky="NW")
        self.category_option_ckbtn.grid(row=4,column=0,columnspan=3,sticky="NW")
        self.category_list.grid(row=5,column=1,columnspan=3,sticky="NE")
        self.search_category_btn.grid(row=6,column=1,columnspan=3,sticky="NE")
    
    def createProcessedImageOptions(self):
        self.invert_btn=ttk.Button(self.processed_options_frame,text="Invert Image")
        
        self.threshold_option_var=tk.IntVar()
        self.threshold_option_ckbtn=ttk.Checkbutton(self.processed_options_frame,text="Set manual threshold")
        #we use the default onvalue and ofvalue of 1 and 0 respectively
        self.threshold_option_ckbtn.configure(variable=self.threshold_option_var) 

        self.threshold_scale=ttk.Scale(self.processed_options_frame,orient="horizontal",
                                length=255,from_=0.0,to=255)
        
        #disabled until the query image has been processed
        self.invert_btn.state(['disabled'])
        self.threshold_option_ckbtn.state(['disabled','alternate'])
        self.threshold_scale.state(['disabled'])
        
        #grid layout for the processed image options
        self.invert_btn.grid(row=0,column=0,sticky="W")
        self.threshold_option_ckbtn.grid(row=1,column=0,sticky="W")
        self.threshold_scale.grid(row=2,column=0,sticky="W")


    def insertQueryImage(self):
        #we get the query image and process it
        query_image=filedialog.askopenfilename()

        image=cv2.imread(query_image)
        
        if image is None:
            errormessage="Error reading image:\n {}".format(query_image)
            messagebox.showinfo(title="Error",message=errormessage,icon="error")
        else:
            image=cv2.resize(image,(200,200))
            pil_image=Image.fromarray(image)
            tk_image=ImageTk.PhotoImage(pil_image)

            self.query_image_label['image']=tk_image
            self.processed_image_label['image']=tk_image
            self.query_image_label.image=tk_image
            
