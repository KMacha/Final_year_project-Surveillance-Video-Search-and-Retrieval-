import numpy as np

from scipy.optimize import linear_sum_assignment
from application.featureprocessing.offlineprocessing.objecttracking.kalmanfilter import KalmanFilter
from application.featureprocessing.featureextraction.shape import fourier_descriptor as fd
from application.featureprocessing.featureextraction.colour import colour_descriptor as cd
from mysql.connector import Error
from cv2 import resize as cv2_resize


class SingleObjectTracker:

    def __init__(self,measurement,object_id,table_name):
        
        self.object_id=object_id

        #we create the KalmanFilter object for the object
        self.kalmanfilter_obj=KalmanFilter()

        #so that it can be 2*1
        self.measurement=np.array([[measurement[0]],[measurement[1]]])

        #when the object is first initialized, we run the kalman filer predict and update
        #for the first cycle
        self.kalmanfilter_obj.predict()
        self.kalmanfilter_obj.update(self.measurement)

        #we set the future predictions to be equal to the first prediction, this is at the start
        self.future_prediction=self.measurement

        #variable to keep track of how many times the object has gone untracked
        #i.e. the number of frames where the object has not been tracked
        self.times_untracked=0

        #variable to decide whether to draw the predicted centroids of the object
        self.draw=False

        #drawing colour
        self.colour=np.random.randint(low=1,high=256,size=3).tolist()

        self.no_times_extracted=0 #this is how many times the features will be extracted

        self.thumbnail=None
        self.classifier_result=None

        self.start_time=self.end_time=None

        #feature descriptors
        self.shape_descriptor=None
        self.colour_descriptor=None

        #the insertion query into the database
        self.insert_query=(
            "INSERT INTO {} "
            "(id,classifier_name,thumbnail,colour_descriptor,"
            "shape_descriptor,start_frame_time,end_frame_time) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)".format(table_name)
        )
    
    def saveFinalDescriptors(self,cursor_obj):
        
        #calculates the average
        if self.no_times_extracted>1:
            self.shape_descriptor/=self.no_times_extracted
            self.colour_descriptor/=self.no_times_extracted
        
        self.binary_thumbnail=self.thumbnail.dumps()
        self.binary_shape_descriptor=self.shape_descriptor.dumps()
        self.binary_colour_descriptor=self.colour_descriptor.dumps()

        self.insertToDB(cursor_obj)

        #we delete the shape and colour descriptor to save on space
        del self.shape_descriptor
        del self.colour_descriptor
        del self.thumbnail

        self.shape_descriptor=self.colour_descriptor=None
    
    def predict(self,measurement):
        #we now run the update, predict cycle
        #we update to get the current states estimate
        self.measurement=np.array([[float(measurement[0])],[float(measurement[1])]])
        self.kalmanfilter_obj.update(self.measurement)

        #print(self.object_id," measurement: ",self.measurement,end=" ")
        #print("prediction: ",self.future_prediction)

        #we predict to get the future predictions for the next state
        self.future_prediction=self.kalmanfilter_obj.predict()
    
    def insertToDB(self,cursor_obj):
        #saves its values to the database
        try:
            cursor_obj.execute(self.insert_query,(self.object_id,self.classifier_result,
                                                self.binary_thumbnail,
                                                self.binary_colour_descriptor,
                                                self.binary_shape_descriptor,
                                                self.start_time,self.end_time
                                                )
                                 )

        except Error as e:
            print("Error: ",e)

    
    #operator overloading, overloading of the operator +
    def __add__(self,no):
        self.times_untracked+=no
    
    #overloading the gt operator
    def __gt__(self,value):
        return True if self.times_untracked>value else False


class Tracker:

    def __init__(self,dist_thresh,max_frames_skip,object_id_count,
                classifier_model,db_connection,cursor_obj,table_name):
        '''
            dist_thresh: it is the distance threshold, when the tracker exceed the threshold,
            it is deleted and a new tracker created

            max_frames_skip: this is the maximum number of frames that are allowed to be
            skipped, with the track object going undetected

            object_id_count: starting identification of the object
        '''

        self.dist_thresh=dist_thresh
        self.max_frames_to_skip=max_frames_skip
        self.object_id_count=object_id_count
        self.classifier_model=classifier_model

        #database connection object and cursor
        self.db_connection=db_connection
        self.cursor=cursor_obj
        self.table_name=table_name

        self.object_trackers=np.array([]) #this is the list of the objects that are being tracked

        #we create the colour_descriptor object
        self.colour_feature_descriptor=cd.ColourDescriptor((8,12,3))

        self.save_cache=[] #this will be used to hold the list of the objects that can be saved
        self.SAVE_NO=2000
    
    
    def getColourDescriptor(self,i:int,set_thumbnail=False,obj=None):
        #it returns the colour descriptor for the detection given by index i
        rect=self.bounding_rects[i] #we get the rect that we need

        start_row_index=rect[0]
        end_row_index=rect[0]+rect[2]
        start_col_index=rect[1]
        end_col_index=rect[1]+rect[3]
        
        #the roi= image[start_row_index:end_row_index,start_col_index:end_col_index]

        #we start with the column index here because in open cv it starts with the columns
        #roi is the region of interest duh!!
        roi=self.image[start_col_index:end_col_index,start_row_index:end_row_index]

        if set_thumbnail and obj is not None:
            obj.thumbnail=cv2_resize(roi,(220,220))
            obj.classifier_result=self.classifier_model.predictClass(roi)
            

        return self.colour_feature_descriptor.describe(roi)

    
    def update(self,image,bounding_rects,contours,centroid_detections,timestamp):

        '''
            -the update goes like, if there are no tracks being tracked, we create them,
            this means that, when self.object_trackers list is empty, we create new ones from
            the detection

            -we then Calculate cost using sum of square distance between 
            predicted vs detected centroids

            -Using Hungarian Algorithm assign the correct
                detected measurements to predicted tracks

                -Identify tracks with no assignment, if any
                If tracks are not detected for long time, remove them
            - Now look for un_assigned detects
            - Start new tracks
            - Update KalmanFilter state, lastResults and tracks trace

            The detections argument is basically the co-ordinates of the objects to be tracked and 
            the centroid of the object is a list of tuples i.e (box_co_ordinates,centroid_co_ordinates)

        '''
        self.timestamp=timestamp
        self.image=image
        self.bounding_rects=bounding_rects
        self.contours=contours
        self.centroid_detections=centroid_detections

        #here we create the track vector if none is detected
        if len(self.object_trackers)==0:
            self.initTrackVector()
        

        #now we calculate the cost between the detections and the saved object tracks
        #using the sum of squared distances
        #print("number of object trackers: ",len(self.object_trackers))
        self.calculateCost()
        #after getting the cost matrix, next step is assigning optimally, using hungarian
        #print("Cost matrix shape: ",self.cost_matrix.shape)
        #print(self.cost_matrix)

        #we then use the hungarian algorithm to assign
        self.assignment=np.zeros(shape=len(self.object_trackers),dtype=np.int32)-1 #to be -1
        row_index,col_index=linear_sum_assignment(self.cost_matrix)

        self.assignment[row_index]=col_index
        #this line above meaning, a certain object being tracked(row_index) 
        #has been assigned to detection (col_index)


        #we then identify the tracks with no assignment, this are the ones whose assignment is -1
        self.findUnassignedObjects()
            

        #we then delete the tracks that are not detected for a long time
        self.deleteObjects()
        
        
        #we then look for unassigned detections and start tracking them
        self.findUnassignedDetections()

        #we then update kalman filter, together with some state variables for the objects being tracked
        self.updateTrackingObjectsState()


    def initTrackVector(self):
        #we initialize the tracking vector if it has not yet been created 

        for index,centroid_co_ordinates in enumerate(self.centroid_detections):
            object_track=SingleObjectTracker(centroid_co_ordinates,self.object_id_count,
                                            table_name=self.table_name)

            #get the shape descriptor
            object_track.start_time=self.timestamp
            object_track.shape_descriptor=fd.fourierDescriptor(self.contours[index],self.centroid_detections[index])
            object_track.colour_descriptor=self.getColourDescriptor(index,set_thumbnail=True,obj=object_track)
            object_track.no_times_extracted+=1
            self.object_id_count+=1

            self.object_trackers=np.append(self.object_trackers,object_track)
    
    def calculateCost(self):
        #we calculate the cost for each.

        N=len(self.object_trackers)
        #M=len(self.centroid_detections)

        #objects being tracked make up the rows
        #all the detections found make up the columns

        self.cost_matrix=[]

        for i in range(N):
            diff=np.linalg.norm(self.object_trackers[i].future_prediction.reshape(-1,2)-self.centroid_detections.reshape(-1,2),axis=1)
            self.cost_matrix.append(diff)
        
        self.cost_matrix=np.array(self.cost_matrix)*0.1
    
    def findUnassignedObjects(self):
        #these are the objects whose assignment is -1

        #Using vectorisation

        #first we find the costs of all the assignments, it does not matter what the cost for those
        #with an assignment of -1 will be
        indexes=np.arange(len(self.assignment))
        temp_costs=self.cost_matrix[indexes,self.assignment[indexes]]

        #having gotthen all the costs, we set value of assignment to be -1, if the cost exceeds the
        #threshold
        self.assignment=np.where(temp_costs>self.dist_thresh,-1,self.assignment)

        #then we add the skipped frames for all the objects whose assignment=-1
        self.object_trackers[self.assignment==-1]+1

        #the above line works since we have overloaded the '+' operator in the class

        '''

        for tracked_object in range(len(self.assignment)):

            #we start by checking those objects that have passed the distance threshold
            matched_detection=self.assignment[tracked_object]
            #tracked object are in the row of our cost matrix
            #matched detection which is the object that a tracked_object matched with is in the
            #column of the cost matrix

            if matched_detection!=-1:

                #when the distance is greater than the distance threshold
                #the object is marked as not to have been tracked and we increment the number of 
                #skipped frames
                if self.cost_matrix[tracked_object][matched_detection]>self.dist_thresh:
                    self.assignment[tracked_object]=-1
                    self.object_trackers[tracked_object].skipped_frames+=1

            else:
                self.object_trackers[tracked_object].skipped_frames+=1
            '''
    
    def deleteObjects(self):

        #we vectorize

        del_tracks_indexes=np.where(self.object_trackers>self.max_frames_to_skip)
        #possible since we have overloaded the '>' operator in the class

        if len(del_tracks_indexes)>0:
            #before we delete the objects, we add them to the save cache
            self.save_cache.extend(self.object_trackers[del_tracks_indexes])

            #delete the objects and their assignments
            self.object_trackers=np.delete(self.object_trackers,del_tracks_indexes)
            self.assignment=np.delete(self.assignment,del_tracks_indexes)

        '''
        del_tracks=[]

        for i in range(len(self.object_trackers)):
            if self.object_trackers[i].skipped_frames > self.max_frames_to_skip:
                del_tracks.append(i)

        if len(del_tracks)>0:
            for id in del_tracks:
                if id<len(self.object_trackers):
                    del self.object_trackers[id]
                    self.assignment=np.delete(self.assignment,id)
                else:
                    print("the id has passed the bounds")
        '''
    
    def findUnassignedDetections(self):
        #unassigned detections are basically new detections
        unassigned_detections=[]

        for i in range(len(self.centroid_detections)):
            if i not in self.assignment:
                unassigned_detections.append(i)
        
        #we start new tracks for the unassigned detections
        if len(unassigned_detections)>0:

            for index in unassigned_detections:

                #we initialize kalman filter for the new detection, (object to be tracked)
                object_track=SingleObjectTracker(self.centroid_detections[index],self.object_id_count,
                                                table_name=self.table_name)


                object_track.start_time=self.timestamp
                #get the shape descriptor
                object_track.shape_descriptor=fd.fourierDescriptor(self.contours[index],self.centroid_detections[index])
                object_track.colour_descriptor=self.getColourDescriptor(index,set_thumbnail=True,obj=object_track)
                object_track.no_times_extracted+=1

                object_track.draw=True

                self.object_id_count+=1
                self.object_trackers=np.append(self.object_trackers,object_track)
    
    def updateTrackingObjectsState(self):
        for i in range(len(self.assignment)):

            if self.assignment[i]!=-1:
                self.object_trackers[i].skipped_frames=0
                
                #this index is the detection that a certain object has been matched with
                index=self.assignment[i]

                #get the shape descriptor
                centroid_co_ordinates=self.centroid_detections[index]
                self.object_trackers[i].end_time=self.timestamp
                self.object_trackers[i].shape_descriptor+=fd.fourierDescriptor(self.contours[index],centroid_co_ordinates)
                self.object_trackers[i].colour_descriptor+=self.getColourDescriptor(index)
                self.object_trackers[i].no_times_extracted+=1
                
                self.object_trackers[i].predict(centroid_co_ordinates)
                self.object_trackers[i].draw=True

            else:
                self.object_trackers[i].predict(self.object_trackers[i].future_prediction)
                self.object_trackers[i].draw=False
    
    def saveToDB(self,arr):
        
        if self.cursor is not None:
            
            try:
                for final_object in arr:

                    #binarize the arrays in the object and save to the database
                    final_object.saveFinalDescriptors(cursor_obj=self.cursor)
                    self.db_connection.commit()

            except Error as e:
                print ("an error occured: ",e)

        else:
            print("Unfortunately the cursor is None")

           
    
    def intermediateSave(self):
        #this method is called when the save cache has 8000 objects
        self.saveToDB(self.save_cache)
    
    def finalSave(self):
        #this method will be called once all the processing has finished

        if len(self.object_trackers)>0:
            self.saveToDB(self.object_trackers)
        
        if len(self.save_cache)>0:
            self.saveToDB(self.save_cache)

        
        self.object_trackers=self.save_cache=[]
