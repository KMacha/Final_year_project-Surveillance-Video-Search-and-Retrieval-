#!/usr/bin/python

import cv2
import torch
import torchvision
import numpy as np

class ClassifierModel:
	
    def __init__(self,confidence_predict_score=0.85):
        #we create a transform to convert the numpy array to a pytorch tensor
        self.tensor_transform=torchvision.transforms.ToTensor()

        #softmax activation function so that the output will be in range [0,1]
        self.softmax_activation=torch.nn.Softmax(dim=1)

        self.device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        #we load the model and the classes that were used to train the model
        self.model=self.loadModel(model_path="model/classifier_model/pyt_squeezenet_model.pth")
        self.classes=np.load("model/classifier_model/pyt_classes.npz")['arr_0']

        self.confidence_predict_score=confidence_predict_score

    def predictClass(self,image):
        self.model.eval() #we set the model to evaluate mode 
        
        if image.shape[0]!=224 or image.shape[1]!=224:
	        image=cv2.resize(image,(224,224))

        image_tensor=torch.unsqueeze(self.tensor_transform(image),dim=0).to(self.device)

        with torch.no_grad():
            predictions,max_class_index=torch.max(self.model(image_tensor),dim=1)

        predicted_class="other"
        if predictions[0]>=self.confidence_predict_score:
	        predicted_class=self.classes[max_class_index]


        return predicted_class

    def loadModel(self,model_path): 
        squeezenet1_1_model=torchvision.models.squeezenet1_1(pretrained=False).to(self.device)

        squeezenet1_1_model.classifier[1]=torch.nn.Conv2d(512,5,kernel_size=(1,1),stride=(1,1))

        squeezenet1_1_model.load_state_dict(torch.load(model_path,map_location=self.device))

        return squeezenet1_1_model
	


if __name__=="__main__":
	print("just checking if the model and classes have been loaded")
	
	model=ClassifierModel()
	print("Classes:\n",model.classes)
	print("Model summary:\n",model.model)
	
	img=cv2.imread("model/sample_images/woman_7.jpg")
	print(model.predictClass(image=img))
	
	
	
	
	
	
		
