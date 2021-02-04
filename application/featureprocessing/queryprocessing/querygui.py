import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog,messagebox
from PIL import Image,ImageTk
from skimage.filters import threshold_otsu
import application.featureprocessing.queryprocessing.querydb as query_db
from application.featureprocessing.featureextraction.shape import fourier_descriptor as fd
from application.featureprocessing.featureextraction.colour import colour_descriptor as cd

class QueryProcessing:

    def __init__(self,root_window,cursor_obj=None,query_image=None):

        #the root window is the toplevel window which we are going to 
        #create the gui on

        self.root_window=root_window
        self.cursor=cursor_obj

        #we create the colour feature descriptor object
        self.colour_feature_descriptor=cd.ColourDescriptor((8,12,3))

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
        self.query_retrieval_btn=ttk.Button(self.main_query_frame,text="Start Search & Retrieval",
                                    command=self.queryDatabaseUsingImage)

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
        self.query_retrieval_btn.state(["disabled"])

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
        tables=list()
        if self.cursor is not None:
            query="SHOW TABLES"
            self.cursor.execute(query)
            tables=self.cursor.fetchall()
        
        tables.append("None")

        #variable for the combobox and setting the default value
        self.search_table_var=tk.StringVar()
        self.search_table_var.set("None")

        self.select_table_label=ttk.Label(self.query_options_frame,text="Choose DB table to search")
        self.table_list=ttk.Combobox(self.query_options_frame,state='readonly')
        self.table_list.configure(values=tables,textvariable=self.search_table_var)
        # self.table_list.current(len(self.table_list['values'])-1)

        self.use_colour_descriptor=tk.IntVar()
        self.colour_option_ckbtn=ttk.Checkbutton(self.query_options_frame,
                text="Use Colour descriptor",variable=self.use_colour_descriptor)

        self.use_shape_descriptor=tk.IntVar()
        self.shape_option_ckbtn=ttk.Checkbutton(self.query_options_frame,
                text="Use Shape descriptor",variable=self.use_shape_descriptor)
        
        self.category_var=tk.IntVar()
        self.category_option_ckbtn=ttk.Checkbutton(self.query_options_frame,
                text="Select particular category",variable=self.category_var,command=self.activateCategoryChoose)

        self.category_list_var=tk.StringVar()
        self.category_list_var.set("All")
        self.category_list=ttk.Combobox(self.query_options_frame,width=18,state="readonly",textvariable=self.category_list_var)
        self.category_list['values']=("Person(M/F)","Bike(motorcycle/bicycle)","Car","Bus","Lorry","Other","All")
        # self.category_list.current(len(self.category_list['values'])-1)

        #create a mapping of the selected category and the name of the category in the database
        self.category_match_dict={
            "Person(M/F)":"person",
            "Bike(motorcycle/bicycle)":"bike",
            "Bus":"bus",
            "Lorry":"lorry",
            "Car":"car",
            "Other":"other",
            "All":None
        }

        self.search_category_btn=ttk.Button(self.query_options_frame,
                                text="Retrieve using Category\n\t(ONLY)",width=19,)
        self.search_category_btn.configure(command=self.queryDatabaseUsingCategory)

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
        self.invert_btn=ttk.Button(self.processed_options_frame,text="Invert Image",command=self.invertImage)
        
        self.threshold_option_var=tk.IntVar()
        self.threshold_option_ckbtn=ttk.Checkbutton(self.processed_options_frame,text="Set manual threshold")
        #we use the default onvalue and ofvalue of 1 and 0 respectively
        self.threshold_option_ckbtn.configure(variable=self.threshold_option_var,
                                            command=self.activateManualThreshold)

        self.threshold_label=ttk.Label(self.processed_options_frame,text="Threshold Value: ")
        
        self.thresh_var=tk.IntVar()
        self.threshold_value_label=ttk.Label(self.processed_options_frame,textvariable=self.thresh_var)

        self.threshold_scale=ttk.Scale(self.processed_options_frame,orient="horizontal",
                                length=255,from_=0.0,to=255,command=self.thresholdChange)
        
        #disabled until the query image has been processed
        self.invert_btn.state(['disabled'])
        self.threshold_option_ckbtn.state(['disabled','alternate'])
        self.threshold_scale.state(['disabled'])
        
        #grid layout for the processed image options
        self.invert_btn.grid(row=0,column=0,columnspan=2,sticky="W")
        self.threshold_option_ckbtn.grid(row=1,column=0,columnspan=3,sticky="W")

        self.threshold_label.grid(row=2,column=0,columnspan=2,sticky="W")
        self.threshold_value_label.grid(row=2,column=2,sticky="W")
        #we first remove the labels showing the threshold till the query image is processed
        self.threshold_label.grid_remove()
        self.threshold_value_label.grid_remove()

        self.threshold_scale.grid(row=3,column=0,columnspan=5,sticky="W")


    def insertQueryImage(self):
        #we get the query image and process it
        query_image_name=filedialog.askopenfilename()

        self.query_image=cv2.imread(query_image_name)
        
        if self.query_image is None:
            errormessage="Error reading image:\n {}".format(query_image_name)
            messagebox.showinfo(title="Error",message=errormessage,icon="error")
        else:
            temp_image=cv2.resize(self.query_image,(200,200))
            rgb_image=cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
            pil_image=Image.fromarray(rgb_image)
            tk_image=ImageTk.PhotoImage(pil_image)

            #show the query image on the query label
            self.query_image_frame.state(["!disabled"])
            self.query_image_label['image']=tk_image
            self.query_image_label.image=tk_image

            #activate the descriptor buttons setting them both selected
            self.colour_option_ckbtn.state(["!disabled","!alternate"])
            self.shape_option_ckbtn.state(["!disabled","!alternate"])
            self.use_shape_descriptor.set(1)
            self.use_colour_descriptor.set(1)

            #we then process the image, basically this is just finding the binary image
            #and show the binary/processed image
            self.getBinaryImage(image=self.query_image,show_image=True)

            self.processed_image_frame.state(['!disabled'])

            #activate the widgets in the config options frame
            self.processed_options_frame.state(["!disabled"])
            self.invert_btn.state(["!disabled"])
            self.threshold_option_ckbtn.state(["!disabled","!alternate"])
            self.threshold_option_var.set(0)

            #we activate the querying button
            self.query_retrieval_btn.state(["!disabled"])

    
    def activateManualThreshold(self):
        if self.threshold_option_var.get():
            self.threshold_scale.state(["!disabled"])
            self.threshold_label.grid()
            self.threshold_value_label.grid()
        else:
            self.threshold_scale.state(["disabled"])
    
    def thresholdChange(self,thresh_value):
        new_thresh_value=int(float(thresh_value))
        self.thresh_var.set(new_thresh_value)

        self.getBinaryImage(image=self.query_image,thresh_value=new_thresh_value,show_image=True)
    
    def activateCategoryChoose(self):
        #when invoked, it will either deactivate the part for 
        #choosing and searching using certain category only
        if self.category_var.get():
            #activate
            self.category_list.state(['!disabled'])
            self.search_category_btn.state(['!disabled'])
        else:
            #deactivate
            self.category_list.state(['disabled'])
            self.search_category_btn.state(['disabled'])
    
    def getBinaryImage(self,image,thresh_value=None,show_image=False):

        if len(image.shape)==3:
            gray_img=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        else:
            gray_img=image

        if thresh_value is None:
            #we use otsu thresholding
            thresh_value=threshold_otsu(gray_img)
            #this also means it is the first time the function has been called thus
            #we set the thresh_value to the threshold_value scale
            self.threshold_scale.state(['!disabled']) #so that we can set the initial threshold value
            self.threshold_scale.set(thresh_value)
            self.threshold_scale.state(['disabled']) #disable it again after setting the initial threshold value

            #we show the variables that show the threshold
            self.threshold_label.grid()
            self.threshold_value_label.grid()
        
        _,self.binary_image=cv2.threshold(gray_img,thresh_value,255,cv2.THRESH_BINARY)

        if show_image:
            self.showBinaryImage()
    
    def showBinaryImage(self):
        temp_image=cv2.resize(self.binary_image,(200,200))
        pil_image=Image.fromarray(temp_image)
        tk_image=ImageTk.PhotoImage(pil_image)

        self.processed_image_label['image']=tk_image
        self.processed_image_label.image=tk_image
    
    def invertImage(self):
        self.binary_image=cv2.bitwise_not(self.binary_image)
        self.showBinaryImage()
    
    def queryDatabaseUsingImage(self):
        #searches the database by first processing the query image to get the descriptors and then
        #uses those descriptors to find the images that are close

        #start by confirming a database table has been selected
        table_name=self.search_table_var.get()
        if table_name=="None":
            messagebox.showinfo(title="Table Selection",message="No table selected",icon="error")
            return 
        
        category_name=self.category_match_dict[self.category_list_var.get()]

        query_colour_descriptor,query_shape_descriptor=self.getQueryImageDescriptors()

        if category_name:
            query="SELECT * FROM {} WHERE classifier_name='{}'".format(table_name,category_name)
        else:
            query="SELECT * FROM {}".format(table_name)
        
        query_db.DatabaseQuery(cursor_obj=self.cursor,query=query,
                                query_shape_descriptor=query_shape_descriptor,
                                query_colour_descriptor=query_colour_descriptor,
                                table_name=table_name  
                            )
        

    
    def queryDatabaseUsingCategory(self):
        #start by confirming a database table has been selected
        table_name=self.search_table_var.get()
        if table_name=="None":
            messagebox.showinfo(title="Table Selection",message="No table selected",icon="error")
            return
        
        #we get the name of the category choosen as it was input in the database
        category_name=self.category_match_dict[self.category_list_var.get()]

        if category_name:
            query="SELECT * FROM {} WHERE classifier_name='{}'".format(table_name,category_name)
        else:
            query="SELECT * FROM {} ".format(table_name)
        
        query_db.DatabaseQuery(cursor_obj=self.cursor,query=query,table_name=table_name)
    
    def getQueryImageDescriptors(self):
        #gets the descriptors for the query image

        query_image_colour_descriptor=query_image_shape_descriptor=None

        if self.use_colour_descriptor.get():
            query_image_colour_descriptor=self.colour_feature_descriptor.describe(self.query_image)
        
        if self.use_shape_descriptor.get():
            query_image_shape_descriptor=fd.extractFeatures(self.binary_image)

        return query_image_colour_descriptor,query_image_shape_descriptor

        

            
