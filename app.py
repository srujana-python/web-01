from flask import Flask, render_template,request,redirect,url_for, flash, session
 # For flask implementation
from pymongo import MongoClient # Database connector
from bson.objectid import ObjectId # For ObjectId to work
from bson.errors import InvalidId # For catching InvalidId exception for ObjectId
from flask_pymongo import PyMongo
import os
import bcrypt
from datetime import datetime

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
client = MongoClient(mongodb_host, mongodb_port)    #Configure the connection to the database
db = client.srujana    #Select the database
todos = db.todo #Select the collection
users = db.users # for user collection


app = Flask(__name__)
app.config['SECRET_KEY'] = 'testing'


app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(app)
title = "TODO APPLICATION"
heading = "TODO APPLICATION"


def redirect_url():# return back to index page
	return request.args.get('next') or \
		request.referrer or \
		url_for('index')

@app.route("/list")
def lists ():
	#Display the all Tasks
	print("iiiiiiiii")
	print(session["ID"])
	print(ObjectId(session["ID"]))
	todos_l = todos.find({"createdBy":ObjectId(session["ID"])})
	print(todos_l)
	# for i in todos_l:
	# 	print(i)
	
	#a1="active"
	return render_template('index.html',todos=todos_l,t=title,h=heading)
	

@app.route("/")
def login():
	#Display the Uncompleted Tasks
	return render_template('login.html')

@app.route('/login_action', methods =["GET", "POST"])
def login_action():
   print("hello")
   uname = request.form['username'] 
   pwd = request.form['password'] 
   print(uname)
   print(pwd)
   login = users.find_one({"username":uname,"password":pwd})
   print("***********")
 
   if login:
	   id=str(login["_id"])
	   print(id)
	   session["ID"]=id
	   print(session["ID"])
	   return redirect("/list")
   else:
	   return render_template("login_error.html")

@app.route('/register_action', methods =["GET", "POST"])
def register_action():
   print("hello")
   uname = request.form['username'] 
   pwd = request.form['password'] 
   email = request.form['email'] 
   phone = request.form['phone'] 
  
   query=users.find_one({"username":uname})
   if query:
	    return render_template('register_error.html')
	  
   else:
	    signup = users.insert_one(
		{
			"username":uname,
			"password":pwd,
			"email":email,
			"phone":phone,
			"createdOn":datetime.now(),
			"updatedOn":datetime.now(),
			})
	
	    return redirect("/login")

@app.route("/register")
def register():
	print(register)
	return render_template('register.html')

@app.route("/login")
def register_login():	
	#Display the Uncompleted Tasks

	return render_template('login.html')

@app.route("/uncompleted")
def tasks ():
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no","createdBy":ObjectId(session["ID"])})
	#a2="active"
	return render_template('index.html',todos=todos_l,t=title,h=heading)


@app.route("/completed")
def completed ():
	#Display the Completed Tasks
	print(completed)
	todos_l = todos.find({"done":"yes","createdBy":ObjectId(session["ID"])})
	#a3="active"
	return render_template('index.html',todos=todos_l,t=title,h=heading)

@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	if(task[0]["done"]=="yes"):
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"no"}})# $set for replace the value)
	else:
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	# Re-directed URL i.e. PREVIOUS URL from where it came into this one
	return redirect(redir)

#@app.route("/add")
#def add():
#	return render_template('add.html',h=heading,t=title)

@app.route("/action", methods=['POST'])
def action ():
	#Adding a Task
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	todos.insert_one(
		{
			 "name":name, 
			 "desc":desc, 
			 "date":date, 
			 "pr":pr, 
			 "done":"no",
			 "createdBy":ObjectId(session["ID"]),
			 "createdOn":datetime.now(),
			 "updatedOn":datetime.now(),
			 })
	return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a Task with various references
	key=request.values.get("_id")
	todos.delete_one({"_id":ObjectId(key)})
	return redirect("/")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	todos.update_one({"_id":ObjectId(id)}, 
	{
		'$set':{ "name":name, 
				 "desc":desc, 
				 "date":date, 
				 "pr":pr ,
				 "updatedOn":datetime.now(),
				 }
	})
	return redirect("/")

@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(refer=="id"):
		try:
			todos_l = todos.find({refer:ObjectId(key)})
			if not todos_l:
				return render_template('index.html',todos=todos_l,t=title,h=heading,error="No such ObjectId is present")
		except InvalidId as err:
			pass
			return render_template('index.html',todos=todos_l,t=title,h=heading,error="Invalid ObjectId format given")
	else:
		todos_l = todos.find({refer:key})
	return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

@app.route("/about")
def about():
	return render_template('credits.html',t=title,h=heading)

if __name__ == "__main__":
	env = os.environ.get('FLASK_ENV', 'development')
	#port = int(os.environ.get('PORT', 5000))
	debug = False if env == 'production' else True
	app.run(debug=True)
	#app.run(port=port, debug=debug)
