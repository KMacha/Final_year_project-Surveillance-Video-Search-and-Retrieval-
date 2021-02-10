*****************************************INITIAL CONFIGURATION***************************************************************************

A standard python installation with additional modules is required.

install tkinter, if not installed, for your system by following instructions in the given link below.
link:https://tkdocs.com/tutorial/install.html

installation for the pybgs module as listed in the requirements.txt file may fail. consider following instructions for your given system as given by the below link
link:https://github.com/andrewssobral/bgslibrary/wiki/Installation-instructions

>> Check the requirements.txt file to check which modules you need to install.
    
    >>> Alternatively, one can install the modules by simply running "pip install -r requirements.txt" on a terminal without the quotes.

A DBMS is also required, preferably mysql since the modules used to connect with the database are for mysql.
Follow instructions from the link below to install mysql for your system
link: https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/

Once mysql has been installed, ensure there is a root user without a password, (root user with empty password is what is used in the program).
To use your own user, consider editing two files found in ./project/login/.add_users.py and ./project/login/loginpage.py.
    >> in these two files, find a line consisting of "mysql.connect(host="localhost",database="surveillance_search_retrieval",user="root",password=""),
        then change the user to your own name that you created and the password to the one that you created

Assess mysql, assuming root user with no password, one can access using "mysql -u root" on a terminal, ignore the quotes, a gui can also be used.
($>) represents the mysql prompt

1. Create a database called "surveillance_search_retrieval" as show below
    $> CREATE DATABASE surveillance_search_retrieval;

    if you use your own database name, change the database in use in the two files shown above in the same line that was mentioned.

    The databases present can be viewed using

    $> SHOW DATABASES;

2. Change to the database and create a users table, the users table is going to be used for the test credentials to use the system, since a login is required.
    >> the users table has two fields username and password, (do not change these names)
    >>This can be done as follows, assuming the database is called surveillance_search_retrieval

    $> USE surveillance_search_retrieval; #these changes to the database created
    $> CREATE TABLE users (username VARCHAR(50), password VARCHAR(255), PRIMARY KEY(username));

3. The table users is the only table that needs to be created, after creation of the table successfully, exit ($>exit;) and change to the login directory
   i.e. ./project/login

   >> in the login directory, run the hidden file .add_users (./.add_users)  and select the option to create a new user, create a user with a username and password.
    >> These username and password created will be our test credentials.
    

****************************************************END***********************************************************************************

************************************************PROJECT STRUCTURE*************************************************************************

Taking the project folder as the root directory, the directory structure of the project is explained below.
    1. ./project/application: This is the main part of the project, which contains the following subfolders
        >>>> ./project/application/appoptions.py: Creates the gui presenting user with the main options for the program, offline processing and querying
        >>>> ./project/application/options.py: Create the gui based on the option chosen by the user.
        >>>> ./project/applicaation/featureprocessing: directory that contains all the parts of the project needed for both offline processing and querying
            I't's directory structure is as follows
            >>>> ./featureprocessing/featureextraction/colour: contains the necessary code for the colour descriptor (colour_descriptor.py)
            >>>> ./featureprocessing/featureextraction/shape: contains the necessary code for the shape descriptor (fourier_descriptor.py)

            >>>> ./featureprocessing/offlineprocessing/movingregion.py: Contains the code for background subtraction, finding the moving region and contours
            >>>> ./featureprocessing/offlineprocessing/offlineprocess.py: Main file containing the code to generate the gui for offline processing
            >>>> ./featureprocessing/offlineprocessing/previewvideo.py: Contains code to show a preview of the selected video
            >>>> ./featureprocessing/offlineprocessing/objecttracking: directory containing the code to track the moving objects
                >>>>> contains the kalmanfilter.py and the tracker.py files

            >>>> ./featureprocessing/queryprocessing/querygui.py:Main file containing the code to generate the gui for query processing
            >>>> ./featureprocessing/queryprocessing/querydb.py: Contains code for querying the database, calculating distance metric between results and the
                query and returning the results
            >>>> ./featureprocessing/queryprocessing/dbrecordgui.py: Contains code to generate the gui used to show the retrieval results from the database
                based on the query
            >>>> ./featureprocessing/queryprocessing/previewvideo.py: inherits from offlineprocessing/previewvideo to show code for previewing the resuls +some                    added functionality
    
    2. ./project/config/ViBe.xml: configuration file that consists of some configuration settings for the background subtraction algorithm used.

    3 ./project/login: Contains the initial login code, has following subfiles
        >>>> ./project/login/.add_users.py: A test executable file that can be used by an adminstrator to add users to the database who can use the system.
            (It is only used for testing while developing the program), a more better and secure way would be required for a production system.
        >>>> ./project/login/loginpage.py: This files creates the initial login gui for the program, it creates the gui that a none logged in user is first
            presented with
    
    4. ./project/model: directory containing everything to do with the classification model, consider it's project structure
        >>>> ./project/model/classifier_model/pyt_squeezenet_model.pth: Contains the weights for a pytorch squeezenet model classifier
        >>>> ./prject/model/classifier_model/pyt_classes.npz: Is a numpy compressed file that consists of the name of the classes used for the pytorch model
            >>>>> To view the names of the classes from the pyt_classes.npz file, open up a terminal in that directory, and run python to get to the interpreter
                >>>>> Run the following in the interpreter, &> represents the interpreter 
                    &> import numpy as np
                    &> np.load("pyt_classes.npz")['arr_0']
       
       >>>> ./project/model/classifier_model/tensorflow_model_backup: contains code for a Inception_v3 tensorflow model, which can be substituted for the 
            pytorch squeezenet model. 
            ** The main reason for choosing the pytorch squeezenet model was its fast execution compared to the Inception_v3 model, during training though,
            the Inception_v3 model had a higher accuracy and higher F1 scores than the squeezenet model

        >>>> ./project/model/classifier.py: contains the code that creates the model and ready's the model for use
    
    5. ./project/videos: Consists of some videos that can be used to test the functionality of the system

***************************************************************END********************************************************************************************

*************************************************************Running program*********************************************************************************

Step 1. First follow the steps in INITIAL CONFIGURATION above, after the database and some test credentials have been created successfully, proceed to step 2

Step 2. >> To run the program, in the projects root directory, i.e. ./project,
    run python -m login.loginpage
    >>> This will run the main login page, after logging in with the test credentials created in the first step, the user is presented with a gui with two options
    >>> At this point, everything is now straight forward, user can choose to select the query option or the offline process, The gui's for each are easy to use

****************************************************************END********************************************************************************************


