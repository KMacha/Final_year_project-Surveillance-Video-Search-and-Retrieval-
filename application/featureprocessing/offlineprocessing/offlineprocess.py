import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cv2
import scrollableframe as sf
from PIL import Image,ImageTk
import time
import application.featureprocessing.offlineprocessing.movingregion as movingregion
from application.featureprocessing.offlineprocessing.objecttracking.tracker import Tracker
from mysql.connector import Error

#Everything to do with offline processing i.e. finding moving region,
#feature extraction, saving in the database ... is handled here


class OfflineProcess(movingregion.MovingRegion):


	def createTable(self,table_name):

		successful=True
		#create the query for creating a table
		query=(
				"CREATE TABLE {} ("
					"id INTEGER UNSIGNED,"
					"classifier_name CHAR(7),"
					"thumbnail BLOB,"
					"colour_descriptor BLOB,"
					"shape_descriptor BLOB,"
					"start_frame_time DOUBLE UNSIGNED,"
					"end_frame_time DOUBLE UNSIGNED,"
					"PRIMARY KEY(id))".format(table_name)
			)

		if self.cursor is not None:
			try:
				self.cursor.execute(query)
				self.db_connection.commit()
				messagebox.showinfo(title="Success",message="Table {} Created Sucessfully".format(table_name))
			except Error as e:
				self.db_connection.rollback()
				message=str(e)

				message+="\n Change table name?"
				change_name=messagebox.askyesno(title="Error",message=message)

				successful=not change_name
				#if the user selects yes, True is returned and successful shall be False, vice versa for no
		
		return successful
	
	def __init__(self,parent_window,db_connection,cursor_obj,table_name,
				video_path,video_name,video_option,classifier_model):
		

		self.parent_window=parent_window

		self.quit=False
		self.video_cap=cv2.VideoCapture(video_path)
		width=self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
		height=self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

		#we call the inherited class constructor
		movingregion.MovingRegion.__init__(self,original_width=width,original_height=height)

		self.APPROX_NO_FRAMES=self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT)

		#database connection object and object to run queries
		self.db_connection=db_connection
		self.cursor=cursor_obj

		#create the table in the database
		if not self.createTable(table_name): #the table was not created successfully
			return

		#variable to check if to show the gui or not
		self.show_video=True if video_option=="yes" else False
		self.show_bigger_video=False

		self.main_window=tk.Toplevel(self.parent_window)
		#configure the main window (root window)
		self.main_window.title("Offline Processing: {}".format(video_name))
		#self.main_window.resizable(False,False)

		#we create the model for classifying
		self.classifier_model=classifier_model	

		#we create the tracker object for tracking the objects duh
		self.tracker_obj=Tracker(10,25,1,classifier_model=self.classifier_model,
					db_connection=self.db_connection,cursor_obj=self.cursor,table_name=table_name)	

		if self.show_video:
			self.main_window.geometry("940x580+100+50")
		else:
			self.main_window.geometry("940x320+100+50")

		self.createGUI()

		#self.main_window.mainloop()
	
	def createGUI(self):
		
		#we have two frames, one for showing the graphical output of the process as it goes on
		#the second frame for showing textual representative output

		if self.show_video:
			#only create part for showing the gui if it is set to true
			self.createVideoGUI()
			
		#create the GUI for the text output
		self.createTextualGUI()		
		
		self.processFootage()
	
	def createVideoGUI(self):
		self.graphical_output_frame=ttk.Frame(self.main_window,width=940,height=240)

		#we are going to show 3 videos
		#the original video
		#after obtaining moving region 
		#and after getting contours of the objects

		self.original_vid_label=ttk.Label(self.graphical_output_frame,text="Original Video",compound="bottom")
		self.movingregion_label=ttk.Label(self.graphical_output_frame,text="Moving Region",compound="bottom")
		self.aftercontour_label=ttk.Label(self.graphical_output_frame,text="Contour Bounding Box",compound="bottom")
		self.objecttracking_label=ttk.Label(self.graphical_output_frame,text="Object Tracking",compound="bottom")

		#layout
		self.graphical_output_frame.grid(row=0,column=0,columnspan=20)
		
		self.original_vid_label.grid(row=0,column=0,padx=5,pady=5)
		self.movingregion_label.grid(row=0,column=1,padx=5,pady=5)
		self.aftercontour_label.grid(row=0,column=2,padx=5,pady=5)
		self.objecttracking_label.grid(row=0,column=3,padx=5,pady=5)


	def createTextualGUI(self):
		self.textual_output_frame=ttk.Frame(self.main_window,borderwidth=3,relief="sunken",width=940,height=240)
		#self.textual_output_frame.grid_propagate(False)

		#get the scrollable frame
		self.scrollable_frame_obj=sf.ScrollableFrame(main_frame=self.textual_output_frame,width=920,height=200)
		self.scrollable_textual_frame=self.scrollable_frame_obj.getFrame()

		self.control_frame=ttk.Frame(self.main_window,width=940,height=50)

		#widgets for the control frame
		#this widgets are just informational ones or some option buttons

		#we create a progress bar that will be used to indicate well progress
		self.progress_bar=ttk.Progressbar(self.control_frame,orient="horizontal",length=400,mode="determinate")

		#we set the maximum steps for the progressbar to be the number of frames to process
		self.progress_bar['maximum']=self.APPROX_NO_FRAMES

		text="Approx number of frames: {}".format(self.APPROX_NO_FRAMES)
		self.approx_frames_label=ttk.Label(self.control_frame,text=text)
		
		self.progress_label=ttk.Label(self.control_frame,text="0% processed")
		self.progress_time_label=ttk.Label(self.control_frame,text="Processing time: ")
		#implement later

		self.query_btn=ttk.Button(self.control_frame,text="Go to Query")
		self.quit_btn=ttk.Button(self.control_frame,text="Cancel Processing",command=self.Quit)
		self.view_btn=ttk.Button(self.control_frame,text="view bigger",command=self.viewBiggerVideo)

		self.query_btn.state(["disabled"]) #it is disabled during processing

		#since its for viewing the video frames been larger, if we are not to show video
		#it should be disabled
		if not self.show_video:
			self.view_btn.state(["disabled"])

		self.textual_output_frame.grid(row=1,column=0,columnspan=20)
		self.control_frame.grid(row=2,column=0)

		self.approx_frames_label.grid(row=0,column=0,columnspan=6)
		self.progress_bar.grid(row=0,column=6,columnspan=10)
		self.progress_label.grid(row=0,column=16,columnspan=4)
		self.progress_time_label.grid(row=1,column=0)
		self.query_btn.grid(row=2,column=10)
		self.quit_btn.grid(row=2,column=12)
		self.view_btn.grid(row=2,column=14)

		for grid_slaveswidget in self.control_frame.grid_slaves():
			grid_slaveswidget.grid_configure(padx=5,pady=5) 

	
	def processFootage(self):
		frames_processed=0
		monitor=0

		ret,curr_frame=self.video_cap.read()
		ret,next_frame=self.video_cap.read()

		#we resize the curr_frame and prev frame and next frame
		resized_curr_frame=self.resizeImage(curr_frame)
		resized_prev_frame=resized_curr_frame.copy()
		resized_next_frame=self.resizeImage(next_frame)

		#we set the prev frame and the next frame

		#convert them to gray
		gray_resized_curr_frame=cv2.cvtColor(resized_curr_frame,cv2.COLOR_BGR2GRAY)
		gray_resized_prev_frame=cv2.cvtColor(resized_prev_frame,cv2.COLOR_BGR2GRAY)
		gray_resized_next_frame=cv2.cvtColor(resized_next_frame,cv2.COLOR_BGR2GRAY)

		#get the first difference image
		diff_image_1=self.getDifferenceImage(gray_resized_curr_frame,gray_resized_prev_frame)
		
		while self.video_cap.isOpened():
			#makes the root_window update so that any pending events can be updated
			self.main_window.update()

			diff_image_2=self.getDifferenceImage(gray_resized_curr_frame,gray_resized_next_frame)

			moving_area=self.findMovingArea(diff_image_1,diff_image_2,gray_resized_curr_frame)

			valid_contours,bigger_contours,bigger_rects,bigger_centroids=self.findValidContours(moving_area)

			#getting the timestamp in milliseconds of the given frame
			timestamp=self.video_cap.get(cv2.CAP_PROP_POS_MSEC)

			#track if there is something to track
			if len(bigger_centroids)>0: #if there is something to track
				self.tracker_obj.update(image=curr_frame,bounding_rects=bigger_rects
										,contours=bigger_contours,centroid_detections=bigger_centroids,timestamp=timestamp)

				
				if len(self.tracker_obj.save_cache)==self.tracker_obj.SAVE_NO:
					label=ttk.Label(self.scrollable_textual_frame)
					label.grid(sticky="nw")

					label['text']="Intermediate Save>>____"
					label['text']+=" Saving {} objects to database...".format(self.tracker_obj.SAVE_NO)

					#save to the database
					self.tracker_obj.intermediateSave()
					self.tracker_obj.save_cache=[]

					label['text']+=" {} objects saved to database".format(self.tracker_obj.SAVE_NO)
			
			frames_processed+=1
			monitor+=1
			if self.show_video and not self.quit:

				rcurr_frame=cv2.resize(curr_frame,(220,220))
				rmoving_area=cv2.resize(moving_area,(220,220))

				rgb_curr_frame=cv2.cvtColor(rcurr_frame,cv2.COLOR_BGR2RGB)

				pil_curr_image=Image.fromarray(rgb_curr_frame)
				pil_moving_area=Image.fromarray(rmoving_area)

				tk_curr_image=ImageTk.PhotoImage(pil_curr_image)
				tk_moving_area=ImageTk.PhotoImage(pil_moving_area)

				#assign image to label
				self.original_vid_label['image']=tk_curr_image
				self.original_vid_label.image=tk_curr_image
				self.movingregion_label['image']=tk_moving_area
				self.movingregion_label.image=tk_moving_area

				#for showing the contours
				cv2.putText(curr_frame,"NO Valid contours: "+str(len(valid_contours)),(5,10),cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5,color=(0,0,255),thickness=2)
				#cv2.drawContours(curr_frame,bigger_contours,-1,(127,200,0),2)

				for rect,centroid in zip(bigger_rects,bigger_centroids):
					cv2.rectangle(curr_frame,(rect[0],rect[1]),(rect[0]+rect[2],rect[1]+rect[3]),(0,0,0),1)
					cv2.circle(curr_frame,(int(centroid[0]),int(centroid[1])),5,(255,0,0),-1)
				
				rcurr_frame=cv2.resize(curr_frame,(220,220))
				rgb_curr_frame=cv2.cvtColor(rcurr_frame,cv2.COLOR_BGR2RGB)
				
				pil_curr_image=Image.fromarray(rgb_curr_frame)
				tk_curr_image=ImageTk.PhotoImage(pil_curr_image)

				self.aftercontour_label['image']=tk_curr_image
				self.aftercontour_label.image=tk_curr_image

				for tracked_object in self.tracker_obj.object_trackers:

					if tracked_object.draw:

						#cv2.putText(temp_curr_frame,str(tracked_object.object_id),tl_co_ordinates,
						#cv2.FONT_HERSHEY_SIMPLEX,0.5,tracked_object.box_colour,2)
						
						x_co_ord=int(tracked_object.future_prediction[0])
						y_co_ord=int(tracked_object.future_prediction[1])

						cv2.putText(curr_frame,str(tracked_object.object_id),(x_co_ord,y_co_ord),cv2.FONT_HERSHEY_SIMPLEX,0.5,tracked_object.colour,2)
						cv2.circle(curr_frame,(x_co_ord,y_co_ord),5,tracked_object.colour,-1)
				
				rcurr_frame=cv2.resize(curr_frame,(220,220))
				rgb_curr_frame=cv2.cvtColor(rcurr_frame,cv2.COLOR_BGR2RGB)
				
				pil_curr_image=Image.fromarray(rgb_curr_frame)
				tk_curr_image=ImageTk.PhotoImage(pil_curr_image)

				self.objecttracking_label.image=tk_curr_image
				self.objecttracking_label['image']=tk_curr_image

				if self.show_bigger_video:
					rcurr_frame=cv2.resize(curr_frame,(640,480))
					rgb_curr_frame=cv2.cvtColor(rcurr_frame,cv2.COLOR_BGR2RGB)
					
					pil_curr_image=Image.fromarray(rgb_curr_frame)
					tk_curr_image=ImageTk.PhotoImage(pil_curr_image)

					self.bigger_tracking_label.image=tk_curr_image
					self.bigger_tracking_label['image']=tk_curr_image


				# time.sleep(0.06)

			if not self.quit:
				frame_processing_label_text="processing frame {}... number of moving objects: {}"\
												.format(frames_processed,len(valid_contours))
				object_tracking_label_text="tracking objects: number of objects been tracked: {} total number of objects tracked: {}"\
												.format(len(self.tracker_obj.object_trackers),self.tracker_obj.object_id_count-1)

				label_text=frame_processing_label_text+" --->> "+object_tracking_label_text
				ttk.Label(self.scrollable_textual_frame,text=label_text).grid(sticky="nw")


			if monitor>=1500:
				self.scrollable_frame_obj.clear()
				monitor=0
			
			#updating the progress (progress bar and the progress label)
			percentage_complete=format(frames_processed/self.APPROX_NO_FRAMES,".0%")

			if not self.quit:
				self.progress_label['text']="{} processed".format(percentage_complete)
				self.progress_bar['value']=frames_processed

			#we assign the frames for the next iteration
			#the curr_frame will basically be the frame that was the next_frame in the previous iteration
			curr_frame=next_frame.copy()
			resized_curr_frame=resized_next_frame.copy()
			gray_resized_curr_frame=gray_resized_next_frame.copy()

			#diff_image_1 will be diff_image_2 from the previous iteration
			diff_image_1=diff_image_2.copy()

			#the only that will be changing will be the next frame
			ret,frame=self.video_cap.read()

			if not ret: break

			next_frame=frame.copy()
			resized_next_frame=self.resizeImage(next_frame)
			gray_resized_next_frame=cv2.cvtColor(resized_next_frame,cv2.COLOR_BGR2GRAY)

			

		#since we were dealing with an approximate number, we set the progress bar to the total number
		#of frames after finishing processing, just so that it can be complete
		if not self.quit:
			self.progress_label['text']="100% processed"
			self.progress_bar['value']=self.APPROX_NO_FRAMES
			self.changeButtons()

			#after finishing processing, we disable the view_btn
			self.view_btn.state(['disabled'])

			#we then save the remaining objects to the database, if there are any
			label=ttk.Label(self.scrollable_textual_frame)
			label.grid(sticky="nw")

			label['text']="Final Save>>____"
			label['text']+=" Saving remaining objects to database..."
			self.main_window.update()

			self.tracker_obj.finalSave()

			label['text']+=" Remaining objects saved to database"
			self.main_window.update()

			self.scrollable_frame_obj.setAutoScroll(value=False)
	
	def Quit(self):
		self.quit=True
		self.video_cap.release()
		self.main_window.destroy()
	
	def viewBiggerVideo(self):
		self.show_bigger_video=True
		
		self.bigger_tracking_window=tk.Toplevel(self.main_window)
		self.bigger_tracking_window.title("Object Tracking Frame")
		self.bigger_tracking_window.geometry("660x500+300+50")

		self.bigger_tracking_frame=ttk.Frame(self.bigger_tracking_window,width=660,height=500)
		self.bigger_tracking_label=ttk.Label(self.bigger_tracking_frame)

		self.bigger_tracking_frame.grid(row=0,column=0)
		self.bigger_tracking_label.grid(row=0,column=0)
		
	
	def changeButtons(self):
		#this will change the states of the buttons after processing has been done
		self.query_btn.state(["!disabled"])
		self.quit_btn['text']="Quit"
		
