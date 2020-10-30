#!/usr/bin/python

#used to create new users to use the system

import mysql.connector as mysql
from mysql.connector import Error
from os import system,name
import hashlib

def clearScreen():
	if name== "nt":
		system("cls")
	else:
		system("clear")


try:
	connection=mysql.connect(host="localhost",database="surveillance_search_retrieval",user="root",password="")
	
	if connection.is_connected():
		print("successfully connected to database")
		cursor=connection.cursor(buffered=True)
		
except Error as e:
	print("Error while connecting to database: ",e)


while True: #infinite loop
	
	print("Pick choice")
	print("1.Create new user\n2.Delete user\n3.Clear Screen\n0.Quit")
	print("Choice>>> ",end="")

	choice=int(input())
	
	if choice==0:
		connection.close()
		break
	elif choice==1:
		#creating a new user
		print("Enter Username: ",end="")
		username=input()
		
		try:
			cursor.execute("SELECT * FROM users WHERE username='{}'".format(username))
			if cursor.rowcount > 0:
				print("Username exists")
				print("try another user name")
			else:
				print("Enter Password: ",end="")
				password=input()
				
				hashed_password=hashlib.sha3_512(password.encode()).hexdigest()
				
				insert_query="INSERT INTO users (username,password) VALUES(%s,%s)"
				values=(username,hashed_password)
				
				cursor.execute(insert_query,values)
				connection.commit()
				
				print("user {} created".format(username))
		
		except Error as e:
			print("ERROR:\n ",e)
			
	elif choice==2:
		pass
		#for deleting the user
	elif choice==3:
		clearScreen()
	else:
		print("No such choice, please try again")
		
		
		
		
		
		
		
