import tkinter as tk
from tkinter import ttk
import os
import application.options as opt


class AppOptions:

	def configureRoot(self):
		self.root.title("A-Search options")
		self.root.geometry("480x200+30+50")
		self.root.resizable(False,False)
	
	def __init__(self,db_connection,cursor_obj,classifier_model,parent_window):
		
		#the database objects
		self.db_connection=db_connection
		self.cursor=cursor_obj
		self.parent_window=parent_window

		self.classifier_model=classifier_model
		#we create the main gui for selecting what the user wants to do
		self.root=tk.Toplevel(self.parent_window)
		self.configureRoot()
		
		self.options_frame=ttk.Frame(self.root,width=480,height=200)
		
		self.root.option_add("*tearOff",False)
		
		self.options_frame.grid(row=0,column=0)
		
		self.createMenuBar()
		self.createGui()
		
		#used when user presses 'X' close button on the window
		self.root.protocol("WM_DELETE_WINDOW",self.destroyWindows)
	
	def createGui(self):
		#creates buttons for the options 
		self.query_btn=ttk.Button(self.options_frame,text="Query (online search & retrieval)",command=lambda: self.createOptionsGUI("query"))
		self.offline_btn=ttk.Button(self.options_frame,text="Offline features processing",command=lambda: self.createOptionsGUI("processing"))
		
		self.query_btn.place(x=125,y=40)
		self.offline_btn.place(x=150,y=100)
		
	
	def createMenuBar(self):
			
		self.menubar=tk.Menu(self.root)
		self.root['menu']=self.menubar
		
		self.options_menu=tk.Menu(self.menubar)
		self.help_menu=tk.Menu(self.menubar)
		
		self.menubar.add_cascade(menu=self.options_menu,label="Options")
		self.menubar.add_cascade(menu=self.help_menu,label="Help")
		
		self.options_menu.add_command(label="Query system")
		self.options_menu.add_command(label="Offline processing")
		
		self.options_menu.add_separator()
		
		self.options_menu.add_command(label="Log out",command=self.logout)
		
		self.options_menu.add_separator()
		
		self.options_menu.add_command(label="Exit",command=self.destroyWindows)
		
		#the help menu we will create its own class that we can always inherit in other classes
	
	def logout(self):
		#when a user log's out we have to set the always logged in to be false
		if os.path.isfile(".configsettings"):
			file=open(".configsettings",'w')
			file.write("No")
			file.close()

		self.root.destroy()

		#we deiconify the parent_window
		self.parent_window.deiconify()
	
	def destroyWindows(self):
		#since it is a top level, destroying the main window will also destroy it
		self.parent_window.destroy()
	
	def createOptionsGUI(self,option_name):

		#calls the method to create the gui for the option choosen
		opt.OptionsGUI(parent_window=self.root,option=option_name,
					db_connection=self.db_connection,cursor_obj=self.cursor,classifier_model=self.classifier_model)



if __name__=="__main__":
	print("Sorry cannot run from main, so many things need to be passed")

		
		
		
		
		
		
		
		
		
		
		
		
		
