import tkinter as tk
from tkinter import ttk
from tkinter import filedialog,messagebox
import random
import os
import application.featureprocessing.offlineprocessing.previewvideo as preview
import application.featureprocessing.offlineprocessing.offlineprocess as offline
import application.featureprocessing.queryprocessing.querygui as query


class OptionsGUI:

	def configureRoot(self):

		title=geometry=""
		if self.option=="query":
			title="Query & Retrieval"
			geometry="940x480+350+150"
		else:
			title="Offline Video Processing"
			geometry="480x150+350+150"
		
		self.root_window.title(title)
		self.root_window.geometry(geometry)
	
	def __init__(self,parent_window,login_window,db_connection,cursor_obj,classifier_model,option="query"):

		#database connection object and object to run queries
		self.db_connection=db_connection
		self.cursor=cursor_obj

		#instance variable for the parent window, necessary so that we can be able to make
		#the parent window be the first in the stacking order when we exit
		self.parent_window=parent_window
		self.login_window=login_window

		self.classifier_model=classifier_model
		#creates the gui for the option that the user chooses
		self.option=option
		self.root_window=tk.Toplevel(self.parent_window)
		self.configureRoot()
		
		self.root_window.option_add("*tearOff",False)
		self.createMenuBar()
		self.createGui()
	
	
	def createGui(self):
		if self.option=="query":
			self.createQueryGUI()
		else:
			self.createFeatureProcessingGUI()
	
	
	def createMenuBar(self):
		self.menubar=tk.Menu(self.root_window)
		
		self.option_menu=tk.Menu(self.menubar)
		
		if self.option=="query":
			#figure out if it is possible, with the code being in another class
			# self.query_menu=tk.Menu(self.option_menu)
			# self.query_menu.add_command(label="Enter query image",command=self.query_gui.insertQueryImage)
			# self.query_menu.add_command(label="Select Image class") #can I put a combobox on a menu
			
			# self.option_menu.add_cascade(menu=self.query_menu,label="Query options")
			self.option_menu.add_command(label="Offline processing",
										command=lambda: self.createFeatureProcessingGUI(change_from_query=True))
		else:
			self.option_menu.add_command(label="Enter Surveillance footage",command=self.showDialog)
			self.option_menu.add_command(label="Search and Retrieval",
										command=lambda: self.createQueryGUI(change_from_offline=True))
		
		self.option_menu.add_separator()
		self.option_menu.add_command(label="Back to selection options",command=self.goBack)

		self.option_menu.add_separator()
		self.option_menu.add_command(label="Quit/Exit",command=self.exit)
		
		self.option_menu.add_separator()
		self.option_menu.add_command(label="logout",command=self.logout)
		
		self.configuration_menu=tk.Menu(self.menubar)
		
		self.configuration_menu.add_command(label="Settings")
		
		#self.help_menu=tk.Menu(self.menubar)
		#we will create a single class that provides with the help menu
		
		self.menubar.add_cascade(menu=self.option_menu,label="Options")
		self.menubar.add_cascade(menu=self.configuration_menu,label="Configuration")
		
		self.root_window['menu']=self.menubar
	
	def createFeatureProcessingGUI(self,change_from_query=False):
		#creates the gui for processing features from the surveillance video

		#change from query will only be true, when the user selects to go to the offline video
		#processing from the menu bar of the query and search
		if change_from_query:
			#we destroy the current window
			#and make a new class with the option for query
			self.root_window.destroy()
			OptionsGUI(parent_window=self.parent_window,login_window=self.login_window,
						db_connection=self.db_connection,cursor_obj=self.cursor,
						classifier_model=self.classifier_model,option="processing")
			
			return

		self.processingframe=ttk.Frame(self.root_window,width=480,height=150)

		#creating button to get dialog for getting the surveillance footage path from the user
		self.dialogbtn=ttk.Button(self.processingframe,text="Enter surveillance footage",command=self.showDialog)

		#shows the name of the footage collected
		self.vid_label=ttk.Label(self.processingframe,text="Video Name:",justify="left",anchor="nw")
		self.videoname=tk.StringVar()
		self.videolabel=ttk.Label(self.processingframe,textvariable=self.videoname,justify="left",anchor="nw")


		#shows the name of the table that will be used to store everything processed in the database
		self.table_frame=ttk.Frame(self.processingframe)
		self.const_tablelabel=ttk.Label(self.table_frame,text="Table Name: ")
		self.table_name=tk.StringVar()
		self.tablelabel=ttk.Label(self.table_frame,textvariable=self.table_name)

		#checkbutton to activate when we need for the table to be edited
		self.checkbtn_val=tk.StringVar()
		self.table_checkbtn=ttk.Checkbutton(self.table_frame,text="change table name",onvalue="yes",offvalue="no")
		self.checkbtn_val.set("no")
		self.table_checkbtn.configure(variable=self.checkbtn_val,command=self.tableNameEdit)

		self.table_checkbtn.state(['disabled','alternate'])

		#for editing the table name
		self.edit_stringvar=tk.StringVar()
		self.table_edit_frame=ttk.Frame(self.processingframe)
		self.edit_label=ttk.Label(self.table_edit_frame,text="Enter table name:")
		self.table_entry=ttk.Entry(self.table_edit_frame,width=40,textvariable=self.edit_stringvar)
		self.table_btn=ttk.Button(self.table_edit_frame,text="save new table name",command=self.saveNewTableName)
		
		self.previewbtn=ttk.Button(self.processingframe,text="Preview video",command=self.previewVideo)
		self.processbtn=ttk.Button(self.processingframe,text="Process video",command=self.processVideo)
		

		#we create a checkbutton that is going to be used to ask the user if to display the gui while
		# processing the video

		self.video_optionvar=tk.StringVar()
		self.video_option=ttk.Checkbutton(self.processingframe,text="Show Videos")

		self.video_option.configure(onvalue="yes",offvalue="no",variable=self.video_optionvar,
						command=self.processGuiOption)

		self.video_optionvar.set("no")

		#disabled atfirst since there will be no video selected 
		#(will be enabled after video is selected)
		self.previewbtn.state(['disabled'])
		self.processbtn.state(['disabled'])
		self.video_option.state(['disabled','alternate'])

		#layout for the widgets

		self.processingframe.grid(row=0,column=0)
		self.dialogbtn.grid(row=0,column=0,columnspan=5,padx=5,pady=(5,2),sticky="we")
		self.vid_label.grid(row=1,column=0,pady=(2,5),sticky="we")
		self.videolabel.grid(row=1,column=1,pady=(2,5),sticky="w")

		#layout for showing the table name
		self.table_frame.grid(row=2,column=0,rowspan=2,columnspan=4)

		self.const_tablelabel.grid(row=0,column=0,rowspan=2,padx=(5,2),pady=5)
		self.tablelabel.grid(row=0,column=1,rowspan=2,padx=(2,5),pady=5,sticky="we")
		self.table_checkbtn.grid(row=0,column=2,rowspan=2,columnspan=2,padx=5,pady=5,sticky="we")
		

		#layout for editing the table name
		self.table_edit_frame.grid(row=2,column=0,rowspan=2,columnspan=4)

		self.edit_label.grid(row=0,column=0,columnspan=2,padx=(5,2),pady=5)
		self.table_entry.grid(row=0,column=2,columnspan=2,padx=(2,5),pady=5)
		self.table_btn.grid(row=1,column=0,columnspan=4)
		self.table_edit_frame.grid_remove() #will be grid in when appropriate

		#layout for the processing buttons
		self.previewbtn.grid(row=4,column=0,columnspan=2,padx=5,pady=5,sticky="w")
		self.processbtn.grid(row=4,column=2,columnspan=2,padx=5,pady=5,sticky="e")
		self.video_option.grid(row=5,column=2,columnspan=2,padx=5,pady=5,sticky="e")

		#we use place on it so that it can fit perfectly to where it should be
		#self.gui_option.place(x=145,y=120)
	
	def showDialog(self):
		#it opens up a dialog for asking the filename for the surveillance footage
		self.footage_path=filedialog.askopenfilename()
		random_number=str(random.getrandbits(25))

		#check if this works the same way for windows
		footage_name=self.footage_path.split("/")[-1]
		self.videoname.set(footage_name)
		self.table_name.set(footage_name.split(".")[0]+"_"+"table"+"_"+random_number)

		#we enable all the disabled widgets
		self.table_checkbtn.state(["!disabled","!alternate"])
		self.previewbtn.state(["!disabled"])
		self.processbtn.state(["!disabled"])
		self.video_option.state(["!disabled","!alternate"])

	def tableNameEdit(self):
		#we remove the gui for showing the table name and insert for editing
		self.table_frame.grid_remove()
		self.edit_stringvar.set(self.table_name.get())
		self.table_edit_frame.grid()
	
	def saveNewTableName(self):
		self.table_name.set(self.edit_stringvar.get()) #we set the new table name input by the user
		self.checkbtn_val.set("no") #the offvalue of the checkbutton

		#we remove the editing gui and show the one for showing the table name
		self.table_edit_frame.grid_remove()
		self.table_frame.grid()
	
	def previewVideo(self):
		preview_obj=preview.PreviewVideo(root_window=self.root_window,
							video_path=self.footage_path,title=self.videoname.get())
		preview_obj.preview()
	
	def processGuiOption(self):

		if self.video_optionvar.get()=="yes":
			mess='''
				Showing videos while processing will slow down the processing.
				Depending on the system, the processing slow down might be significant or it might be insignificant.\n

				Do you want to continue with showing videos on?
			'''
			ansa=messagebox.askyesno(title="Showing videos while processing",message=mess,icon="warning")
			
			if not ansa: self.video_optionvar.set("no")

	
	def processVideo(self):
		offline.OfflineProcess(parent_window=self.root_window,db_connection=self.db_connection,
								cursor_obj=self.cursor,table_name=self.table_name.get(),
								video_path=self.footage_path,video_name=self.videoname.get(),
								video_option=self.video_optionvar.get(),
								classifier_model=self.classifier_model)
	
	def createQueryGUI(self,change_from_offline=False):
		#change from offline will be True only when the function is called when the user
		#selects from the menu of the offline gui to change to search and retrieval
		if change_from_offline:
			#we destroy the current window
			#and make a new class with the option for query
			self.root_window.destroy()
			OptionsGUI(parent_window=self.parent_window,login_window=self.login_window,
						db_connection=self.db_connection,cursor_obj=self.cursor,
						classifier_model=self.classifier_model,option="query")
			
			return

		query.QueryProcessing(root_window=self.root_window,cursor_obj=self.cursor)
	
	def goBack(self):
		#we destroy the options window and we make the option selection window be 
		#at the front i.e

		self.root_window.destroy()
		self.parent_window.lift()
	
	def exit(self):
		#to exit we destroy the login_window, since it is the main window,
		#everything else will be destroyed
		self.login_window.destroy()
	
	def logout(self):
		#when a user log's out we have to set the always logged in to be false
		if os.path.isfile(".configsettings"):
			file=open(".configsettings",'w')
			file.write("No")
			file.close()

		self.parent_window.destroy()

		#we deiconify the login_window
		self.login_window.deiconify()
		

			
		


if __name__=="__main__":
    from model import classifier
    parent_window=tk.Tk()
    parent_window.title("helping visualize")
    print("just visualising how it looks, NO DATABASE")
    model=classifier.ClassifierModel()
    #model=None
    OptionsGUI(parent_window=parent_window,db_connection=None,cursor_obj=None,classifier_model=model,login_window=None,option="nothing")
    print("This is just for testing")
    print("A lot of things are not going to work in this one")
    parent_window.mainloop()


