import numpy as np 

class KalmanFilter:

    def __init__(self):

        self.dt=0.1
        self.x_std_meas=0.15 #deviation for the x measurement
        self.y_std_meas=0.15 #deviation for the y measurement

        self.std_acc=2.5 #deviation for the acceleration

        #state variables
        self.x=np.array([[0],[0],[1],[1]])

        #input/control variables
        self.u=np.array([[1],[1]])

        #state transition matrix
        self.A=np.array([[1,0,self.dt,0],[0,1,0,self.dt],[0,0,1,0],[0,0,0,1]])

        #input transition matrix
        self.B=np.array([[self.dt**2/2.0,0],[0,self.dt**2/2.0],[self.dt,0],[0,self.dt]])

        #observation matrix
        self.H=np.array([[1,0,0,0],[0,1,0,0]])

        #process noise covariance matrix
        self.Q=np.array([[self.dt**4/4.0,0,self.dt**3/2.0,0],
                        [0,self.dt**4/4.0,0,self.dt**3/2.0],
                        [self.dt**3/2.0,0,self.dt**2,0],
                        [0,self.dt**3/2.0,0,self.dt**2]])*self.std_acc**2
        
        #measurement noise covariance matrix
        self.R=np.array([[self.x_std_meas**2,0],[0,self.y_std_meas**2]])
        
        #estimate uncertainity
        self.P=np.eye(self.A.shape[1])

        self.identity_matrix=np.eye(self.H.shape[1])
    
    def predict(self):
        #using the extrapolation equations
        self.x=np.dot(self.A,self.x)+np.dot(self.B,self.u)

        self.P=np.dot(np.dot(self.A,self.P),self.A.T)+self.Q

        return self.x[:2]
    
    def update(self,z):
        #z is the current measurement

        #first calc the kalman gain
        temp=np.linalg.pinv(np.dot(np.dot(self.H,self.P),self.H.T)+self.R)

        kalman_gain=np.dot(np.dot(self.P,self.H.T),temp)

        #calculate the current state estimate using the state update equation
        self.x=self.x + kalman_gain @ (z-(self.H @ self.x))

        #calculate the estimate uncertaint using the covariance update equation
        self.P=(self.identity_matrix-(kalman_gain @ self.H))@ self.P