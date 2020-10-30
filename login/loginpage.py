import tkinter as tk
from tkinter import ttk,font as tkfont,messagebox
import mysql.connector as mysql
from mysql.connector import Error
import hashlib
import os
from model import classifier
import application.appoptions as app



class Login:

	def connectDatabase(self):
		try:
			#we connect to the database
			self.connection=mysql.connect(host="localhost",database="surveillance_search_retrieval",
							user="root",password="")
			
			#we create the object to perform the db operations
			self.cursor=self.connection.cursor(buffered=True)
		
		except Error as e:
			print("Error while connecting: ",e)

	def configureRootWindow(self):
		self.login_root_window.title("User Login")
		self.login_root_window.geometry("480x200+30+50")
		self.login_root_window.resizable(False,False)
	
	def __init__(self):

		self.stay_logged_in=False
		self.logged_in=False

		self.connectDatabase()

		self.login_root_window=tk.Tk()
		self.configureRootWindow()
		self.login_frame=ttk.Frame(self.login_root_window)

		self.createGui()
		
		self.login_frame.grid(row=0,column=0)
		
		#we pad all the widgts inserted in the login_frame
		for widget in self.login_frame.grid_slaves():
			widget.grid_configure(padx=2,pady=2)

		#we create the model for classifying
		#self.model=classifier.ClassifierModel()
		self.model=None

		if os.path.isfile(".configsettings"):
			file=open(".configsettings",'r')
			if file.read()=="Yes":
				self.login_root_window.withdraw()

				self.logged_in=True
				#the main gui after authentication
				self.createAppGUI()
			
			file.close()
					
		self.login_root_window.mainloop()
	
	def createGui(self):
		self.login_label=ttk.Label(self.login_frame,text="LOGIN",font=tkfont.Font(family="Courier",size=15,weight="bold"))
		
		self.username_label=ttk.Label(self.login_frame,text="Username")
		self.username_entry=ttk.Entry(self.login_frame,width=25)
		
		self.password_label=ttk.Label(self.login_frame,text="Password")
		self.password_entry=ttk.Entry(self.login_frame,width=25,show="*")
		
		self.login_button=ttk.Button(self.login_frame,text="Enter",command=self.confirmUserDetails)

		self.check_var=tk.StringVar()
		self.check_var.set("no")
		self.check_button=ttk.Checkbutton(self.login_frame,text="stay logged in",
											onvalue="yes",offvalue="no",variable=self.check_var)
		self.check_button.configure(command=self.checkStayLoggedIn)
		
		
		self.login_label.grid(row=0,column=5,columnspan=2)
		self.username_label.grid(row=1,column=4,columnspan=2)
		self.username_entry.grid(row=2,column=4,columnspan=5)
		
		self.password_label.grid(row=3,column=4,columnspan=2)
		self.password_entry.grid(row=4,column=4,columnspan=5)
		self.check_button.grid(row=5,column=4,columnspan=3)

		self.login_button.grid(row=6,column=5,columnspan=2)
		
		self.app_name_label=ttk.Label(self.login_frame,text="A-Search",font=tkfont.Font(family="Courier",size=30,weight="bold"))
		
		self.app_name_label.grid(row=0,column=0,columnspan=3)
	
	def confirmUserDetails(self):
		username=self.username_entry.get()
		password=hashlib.sha3_512(self.password_entry.get().encode()).hexdigest()


		#we authenticate the user
		try:
			query="SELECT * FROM users WHERE username=%s AND password=%s"
			values=(username,password)

			self.cursor.execute(query,values)
		
			if self.cursor.rowcount==1:
				#to avoid the circular import error
				self.login_root_window.withdraw()

				file=open(".configsettings",'w')

				if self.stay_logged_in:
					file.write("Yes")
				else:
					file.write("No")

				file.close()
				
				#the main gui after authentication
				self.createAppGUI()
			else:
				messagebox.showinfo("message","Incorrect login")
		
		except Error as e:
			print("ERROR OCCURRED:\n",e)
	
	def checkStayLoggedIn(self):
		if self.check_var.get()=="yes":
			self.stay_logged_in=True
		else:
			self.stay_logged_in=False
	
	def createAppGUI(self):
		app.AppOptions(db_connection=self.connection,cursor_obj=self.cursor,
						classifier_model=self.model,parent_window=self.login_root_window)

			
		

if __name__=="__main__":
	Login()
		
		
