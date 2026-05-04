from flask import Flask, flash, jsonify, redirect, url_for, render_template, request, abort, session
from flask_socketio import SocketIO, emit
import sqlite3 as sql
import threading
import time
import psutil
import os
from flask_cors import CORS
from logger import setup_logging
from mdb import MDB

app = Flask(__name__)
app.secret_key='web Kast uodf aoil gdtyrrt'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response
@app.route('/')
def index():
    return render_template('signin.html')

@app.route('/login', methods = ['POST'])
def login():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        # email = request.form['email']
        # password = request.form['password']
        print('email',email)
        
        with sql.connect("mdb.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * from admin WHERE email==(?) AND password==(?)",(email,password))
            user=cur.fetchone()
            # con.close()
            if user !=None:
                session["user_id"]=email
                error = {"success": True,"message": "SingIn Successful"}
                return jsonify(error)
            else:
                error = {"success": False,"message": "Invalid email or password"}
                print('user',user)
                return jsonify(error)
            con.close()

@app.route('/signup')
def signuppage():
   return render_template('signup.html')

@app.route('/register', methods = ['POST'])
def register():
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            email = request.form['email']
            password = request.form['password']
            
            with sql.connect("mdb.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO admin (name,email,password,itemLimit) VALUES (?,?,?,?)",(nm,email,password,5))
                
                con.commit()
                msg = "SignUp Successful!"
        except:
            con.rollback()
            msg = "SingUp Failed"
      
        finally:
            return redirect(url_for('index'))
            con.close()

@app.route('/dashboard')
def dashboard():
    if "user_id" in session:
        return render_template('dashboard.html')
    return redirect(url_for('index'))
def get_process_info():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_usage = process.cpu_percent(interval=1)
    return {
        "cpu_usage": cpu_usage,
        "memory_info": {
            "rss": f"{memory_info.rss / 1024 / 1024:.2f} MB",
            "vms": f"{memory_info.vms / 1024 / 1024:.2f} MB",
        }
    }
@app.route('/employee')
def employee():
    if "user_id" in session:
        return render_template('employee.html')
    return redirect(url_for('index'))
@app.route('/getemployee', methods=['POST'])
def getemployee():
    if "user_id" in session:
        with sql.connect("mdb.db") as con:
            cur = con.cursor()            
            cur.execute("SELECT * from employees")
            users=cur.fetchall()
            return jsonify(users)
@app.route('/addemployee', methods = ['POST'])
def addemployee():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        name = data.get("name")
        ID = data.get("ID")
        cardID = data.get("cardID")
        itemLimit = data.get("itemLimit")
        leftItem = data.get("leftItem")
        status = data.get("status")
        
        with sql.connect("mdb.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO employees (name,ID, cardID, itemLimit, leftItem, status) VALUES (?,?,?,?,?,?)",(name,ID, cardID, itemLimit, leftItem, status))
            con.commit()
            cur.execute("SELECT * from employees")
            user=cur.fetchall()
            if user !=None:
                response = {"success": True,"user": "user"}
                return jsonify(response)
            else:
                error = {"success": False,"message": "Adding Employee Failed"}
                return jsonify(error)
            con.close()

@app.route('/history')
def history():
    if "user_id" in session:
        return render_template('history.html')
    return redirect(url_for('index'))

@app.route('/threads')
def list_threads():
    threads = threading.enumerate()
    thread_info = []
    for thread in threads:
        thread_info.append({
            'name': thread.name,
            'id': thread.ident,
            'daemon': thread.daemon
        })
    error = {"success": 'False',"message": "Invalid email or password"}
    return jsonify(error)

@app.route('/monitoring')
def memory_usage():
    return jsonify(get_process_info())

@app.route('/long_task')
def long_task():
    def task():
        time.sleep(5)
        app.logger.info("Long task finished")
        
        thread = threading.Thread(target=task)
        thread.start()
    return "Long task started!"

@app.route('/enternew')
def new_student():
   return render_template('student.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   if request.method == 'POST':
        try:
            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            pin = request.form['pin']
            
            with sql.connect("mdb.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO students (name,addr,city,pin) VALUES (?,?,?,?)",(nm,addr,city,pin))
                
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
      
        finally:
            return render_template("result.html",msg = msg)
            con.close()

@app.route('/list')
def list():
   con = sql.connect("mdb.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from students")
   
   rows = cur.fetchall(); 
   return render_template("list.html",rows = rows)

# SOCKET IO
# client connects
@socketio.on('connect')
def handle_connect():
    print("Client connected")

# custom event
@socketio.on('message')
def handle_message(data):
    print("Received:", data)
    emit('response', {'data': 'Message received!'})

# disconnect
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('connected')
def page_connected(msg):
    print(msg)
    emit('status_changed', 1)
    emit('return_on_connect', 'Succesfully connected to backend')

mdb=MDB()
mdbthread=threading.Thread(target=mdb.handle_command)

if __name__ == '__main__':
    try:
        # logging_thread = setup_logging(app)
        # logging_thread.start()
        # mdbthread.start()
        
        print("Current Thread count: %i." % threading.active_count())
        # mdbthread.join()
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except:
        print("error")