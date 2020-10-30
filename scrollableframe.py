#!/usr/bin/python

import tkinter as tk
from tkinter import ttk

#we create a reusable class for a scrollable frame using tkinter

class ScrollableFrame:

	def configureEvent(self,event):
		#the configure event is activated only when the frame changes size

		self.canvas['scrollregion']=self.canvas.bbox("all")

		if self.auto_scroll: self.canvas.yview_moveto(1)
	
	def __init__(self,main_frame,width=100,height=200,auto_scroll=True):
		
		self.auto_scroll=auto_scroll

		self.width=width
		self.height=height

		self.canvas=tk.Canvas(main_frame,width=width,height=height)
		
		#creating both the horizontal and vertical scrollbars
		self.yscrollbar=ttk.Scrollbar(main_frame,orient="vertical",command=self.canvas.yview)
		self.xscrollbar=ttk.Scrollbar(main_frame,orient="horizontal",command=self.canvas.xview)

		#the scrollable frame
		self.scrollable_frame=ttk.Frame(self.canvas,width=width,height=height)

		#we create the binding for the configure event	
		self.scrollable_frame.bind("<Configure>",self.configureEvent)
		
		#we draw the scrollable frame on the canvas
		self.canvas.create_window((0,0),window=self.scrollable_frame,anchor="nw")
	
		#we configure the canvas for the scrollbar
		self.canvas.configure(yscrollcommand=self.yscrollbar.set,xscrollcommand=self.xscrollbar.set)
		
		#we pack all the widgets
		self.yscrollbar.pack(side="right",fill="y")
		self.xscrollbar.pack(side="bottom",fill="x")
		
		self.canvas.pack(side="left",fill="both",expand=True)
		self.canvas.pack_propagate(False)
		self.scrollable_frame.propagate(0)
	
	def getFrame(self):
		#returns the scrollable frame
		return self.scrollable_frame
	
	def setAutoScroll(self,value):
		self.auto_scroll=value
	
	def clear(self):
		#destroying everything in the frame
		for child in self.scrollable_frame.winfo_children():
			child.destroy()

		#we reinit the size of the frame and set the scroll region to all 0's 
		#so that the scrollbar can be able to adjust to the start again
		self.scrollable_frame['width']=self.width
		self.scrollable_frame['height']=self.height
		#self.canvas['width']=self.width
		#self.canvas['height']=self.height
		self.canvas['scrollregion']=(0,0,0,0)


		#self.canvas.yview_moveto(1)


if __name__=="__main__":
	print("just visualizing to see how it looks")
	
	root_window=tk.Tk()
	
	frame1=ttk.LabelFrame(root_window, text="first_frame",width=400,height=200)
	frame2=ttk.Frame(root_window,width=400,height=200)
	
	obj=ScrollableFrame(main_frame=frame2,width=400,height=200)
	
	ttk.Label(obj.getFrame(),text="Yeaaaaah what's love got to do got to do yeah whats love got to do got to do").grid()
	for i in range(50):
		ttk.Label(obj.getFrame(),text="this is label {}".format(i)).grid()
		
	
	frame1.grid(row=0,column=0,sticky="we")
	frame2.grid(row=1,column=0,sticky="we")
	
	root_window.mainloop()
	
	
	
	
	
	
	
		
