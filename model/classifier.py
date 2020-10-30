#!/usr/bin/python

import cv2
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'

import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.inception_v3 import preprocess_input

class ClassifierModel:
	
	def __init__(self,confidence_predict_score=0.85):
		#we load the model and the classes that were used to train the model
		self.model=load_model("model/classifier_model/Model")
		self.classes=np.load("model/classifier_model/classes.npz")['arr_0']
		self.confidence_predict_score=confidence_predict_score
	
	def predictClass(self,image):
		if image.shape[0]!=200 or image.shape[1]!=200:
			image=cv2.resize(image,(200,200))
			
		predictions=self.model.predict(np.expand_dims(preprocess_input(image),axis=0))
		max_class_index=int(np.argmax(predictions,axis=1))
		
		predicted_class="other"
		if predictions[0][max_class_index]>=0.85:
			predicted_class=self.classes[max_class_index]
		
		
		return predicted_class
	


if __name__=="__main__":
	print("just checking if the model and classes have been loaded")
	
	model=ClassifierModel()
	print("Classes:\n",model.classes)
	print("Model summary:\n",model.model.summary())
	
	img=cv2.imread("model/sample_images/woman_7.jpg")
	print(model.predictClass(image=img))
	
	
	
	
	
	
		
