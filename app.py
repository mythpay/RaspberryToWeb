from flask import Flask, flash, jsonify, redirect, url_for, render_template, request, abort, session
from flask_socketio import SocketIO, emit
import sqlite3 as sql
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import psutil
import os
from flask_cors import CORS
from logger import setup_logging
from rfid import RFIDCard
from newvend import MDBVendingMachine
from vend import MDBDevice

app = Flask(__name__)
app.secret_key='web Kast uodf aoil gdtyrrt'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
DATABASE = "mdb.db"
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

rfidcard=RFIDCard()
rfidthread=threading.Thread(target=rfidcard.run)

mdbdevice = MDBDevice(socketio=socketio)
mdbdevicethread = threading.Thread(target=mdbdevice.run)
# Function to reset tables
def reset_tables(hour):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        # cur.execute("UPDATE employees SET itemLimit=?, leftItem=?",(5,5))
        
        now=datetime.today().strftime("%Y-%m-%d")
        today = datetime.today().strftime("%A")
        days = {"Monday":1,"Tuesday":2,"Wednesday":3,"Thursday":4,"Friday":5,"Saturday":6,"Sunday":7}  
        if(hour==0):
            conn.execute("UPDATE employees SET leftItem = itemLimit")
            conn.commit()
            cur.execute("UPDATE mdbevent SET dailylimit=?, machineStatus=?",(5,0,))
            conn.commit()

        if(hour==9):
            socketio.emit('response', {'data':"on"})
            cur.execute("UPDATE mdbevent SET machineStatus=?",(1,))            
            print(f"9 machine on")
            cur.execute("SELECT machineStatus FROM dayoffweek WHERE day=? LIMIT 1", (days[today],))
            machineStatus = cur.fetchone()[0]
            cur.execute("UPDATE mdbevent SET dailylimit=?, machineStatus=?",(5,machineStatus,))
            conn.commit()

            cur.execute("SELECT EXISTS(SELECT 1 FROM dayoff WHERE date=? LIMIT 1)", (now,))
            exists = cur.fetchone()[0]
            if exists!=0: 
                cur.execute("UPDATE mdbevent SET dailylimit=?, machineStatus=?",(5,0,))
                conn.commit()
        
        if(hour==18):
            socketio.emit('response', {'data':"off"})
            cur.execute("UPDATE mdbevent SET machineStatus=?",(0,))
            conn.commit()
            print(f"18 machine off")
            
        if(hour==1):
            cur.execute("SELECT * FROM machinetimer")
            machinetimer=cur.fetchone()
            create_schedule(
                machinetimer[0],
                machinetimer[1],
                machinetimer[2],
                machinetimer[3]
            )
            print("machinetimer:",machinetimer)
        cur.execute("SELECT machineStatus FROM mdbevent")
        status=cur.fetchone()[0]
        print("reset table machine status:", status)
        mdbdevice.setLED(status)
        conn.close()

        print(f"[{datetime.now()}] Tables reset successfully.")

    except Exception as e:
        print("Reset error:", e)
# Scheduler
scheduler = BackgroundScheduler()
# Run everyday at 12:00 AM
scheduler.add_job(reset_tables, 'cron', hour=0, minute=0, args=[0])
scheduler.start()

def create_schedule(start_hour, start_minute, end_hour, end_minute):

    # remove old jobs if exist
    try:
        scheduler.remove_job("start_job")
    except:
        pass

    try:
        scheduler.remove_job("end_job")
    except:
        pass

    # START machine
    scheduler.add_job(
        reset_tables,
        'cron',
        hour=start_hour,
        minute=start_minute,
        args=[9],
        id="start_job"
    )

    # END machine
    scheduler.add_job(
        reset_tables,
        'cron',
        hour=end_hour,
        minute=end_minute,
        args=[18],
        id="end_job"
    )

    print("Scheduler updated")

@app.route('/updateschedule', methods=['POST'])
def updateschedule():

    try:
        data = request.get_json()

        start_time = data.get("startTime")   # example: 09:30
        end_time = data.get("endTime")       # example: 18:00

        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("UPDATE machinetimer SET startHour=?,startMinute=?,endHour=?,endMinute=?",(start_hour, start_minute, end_hour, end_minute,))   
            con.commit()  

        create_schedule(
            start_hour,
            start_minute,
            end_hour,
            end_minute
        )

        return jsonify({
            "success": True,
            "message": "Timer updated"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })
# # Run at 9:00 AM
# scheduler.add_job(reset_tables, 'cron', hour=9, minute=0, args=[9])
# # Run at 6:30 PM
# scheduler.add_job(reset_tables, 'cron', hour=18, minute=30, args=[18])
# Every 1 minutes
# scheduler.add_job(reset_tables, 'interval', minutes=1, args=[9])


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
        
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM admin WHERE email==(?) AND password==(?)",(email,password,))
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
            
            with sql.connect(DATABASE) as con:
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

@app.route('/getalldetails', methods=['POST'])
def getalldetails():
    if "user_id" in session:
        with sql.connect(DATABASE) as con:
            cur = con.cursor()            
            cur.execute("SELECT * FROM employees")
            users=cur.fetchall()      
            cur.execute("SELECT * FROM mdbevent")
            machine=cur.fetchone()
            cur.execute("SELECT date FROM dayoff WHERE machineStatus=0")
            dayoff=cur.fetchall()
            cur.execute("SELECT * FROM dayoffweek")
            days=cur.fetchall() 
            cur.execute("SELECT * FROM machinetimer")
            machinetimer=cur.fetchone() 
            cur.execute("""
                SELECT COUNT(*) 
                FROM vendinghistory
                WHERE DATE(logDate) = DATE('now', 'localtime')
            """)
            today_count = cur.fetchone()[0]
            return jsonify(users, machine, dayoff, days, machinetimer, today_count)

@app.route('/adddayoff', methods = ['POST'])
def adddayoff():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        dateval = data.get("val")
        print("dateval:", dateval)
        print("localtime:",datetime.strptime(dateval,"%Y-%m-%d"))
        
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT EXISTS(SELECT 1 FROM dayoff WHERE date=? LIMIT 1)", (dateval,))
            exists = cur.fetchone()[0]
            print('exists:', exists)
            if exists==0:    
                cur.execute("INSERT INTO dayoff (date, machineStatus) VALUES (?,?)",(dateval, 0))
                con.commit()
                cur.execute("SELECT date FROM dayoff")
                days=cur.fetchall()
                if days !=None:
                    response = {"success": True,"days": days}
                    return jsonify(response)
                else:
                    error = {"success": False,"message": "Adding DayOff Failed"}
                    return jsonify(error)   
            else:         
                error = {"success": False,"message": "Dayoff Existing"}
                return jsonify(error)

            con.close()

@app.route('/deletedayoff', methods = ['POST'])
def deletedayoff():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        dateval = data.get("val")
        
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM dayoff WHERE date=?",(dateval))
            con.commit()
            cur.execute("SELECT date FROM dayoff")
            days=cur.fetchall()
            if days !=None:
                response = {"success": True,"days": days}
                return jsonify(response)
            else:
                error = {"success": False,"message": "Adding DayOff Failed"}
                return jsonify(error)
            con.close()

@app.route('/updatedayoffweek', methods = ['POST'])
def updatedayoffweek():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        day = data.get("day")
        status = data.get("status")
        
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("UPDATE dayoffweek SET machineStatus=? WHERE day=?",(status, day,))   
            con.commit()  
            cur.execute("SELECT * FROM dayoffweek")
            days=cur.fetchall() 
            if days !=None:
                response = {"success": True,"days": days}
                return jsonify(response)
            else:
                error = {"success": False,"message": "Adding DayOff Failed"}
                return jsonify(error)   

            con.close()

@app.route('/employee')
def employee():
    if "user_id" in session:
        return render_template('employee.html')
    return redirect(url_for('index'))

@app.route('/getemployee', methods=['POST'])
def getemployee():
    if "user_id" in session:
        with sql.connect(DATABASE) as con:
            cur = con.cursor()            
            cur.execute("SELECT * FROM employees")
            users=cur.fetchall()
            return jsonify(users)

@app.route('/addemployee', methods = ['POST'])
def addemployee():
    try:
        error = None
        if request.method == 'POST':
            data = request.get_json()
            name = data.get("name")
            empID = data.get("empID")
            cardID = data.get("cardID")
            itemLimit = data.get("itemLimit")
            leftItem = data.get("leftItem")
            status = data.get("status")
            
            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO employees (name,empID, cardID, itemLimit, leftItem, status) VALUES (?,?,?,?,?,?)",(name,empID, cardID, itemLimit, leftItem, status))
                con.commit()
                cur.execute("SELECT * FROM employees")
                users=cur.fetchall()
                if users !=None:
                    response = {"success": True,"users": users}
                    return jsonify(response)
                else:
                    error = {"success": False,"message": "Adding Employee Failed"}
                    return jsonify(error)
                con.close()
                
    except Exception as e:
        error = {"success": False,"message": "Card Already Enrolled"}
        return jsonify(error)

@app.route('/deleteemployee', methods = ['POST'])
def deleteemployee():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        cardID = data.get("cardID")
        print('cardid:',cardID)
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM employees WHERE cardID =?",(cardID,))
            con.commit()
            cur.execute("SELECT * FROM employees")
            users=cur.fetchall()
            if users !=None:
                response = {"success": True,"users": users}
                return jsonify(response)
            else:
                error = {"success": False,"message": "Removing Employee Failed"}
                return jsonify(error)
            con.close()

@app.route('/updateemployee', methods = ['POST'])
def updateemployee():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        id=data.get("id")
        name = data.get("name")
        empID = data.get("empID")
        cardID = data.get("cardID")
        itemLimit = data.get("itemLimit")
        status = data.get("status")
        
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("UPDATE employees SET name=?,empID=?, cardID=?, itemLimit=?, status=? WHERE id=?",(name,empID, cardID, itemLimit, status, id,))
            con.commit()
            cur.execute("SELECT * FROM employees")
            users=cur.fetchall()
            if users !=None:
                response = {"success": True,"users": users}
                return jsonify(response)
            else:
                error = {"success": False,"message": "Updating Failed"}
                return jsonify(error)
            con.close()

@app.route('/serachemployee', methods = ['POST'])
def serachemployee():
    error = None
    if request.method == 'POST':
        data = request.get_json()
        name = data.get("name")        
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM employees WHERE name=? OR cardID=?",(name, name,))
            users=cur.fetchall()
            if users !=None:
                response = {"success": True,"users": users}
                return jsonify(response)
            else:
                error = {"success": False,"message": "Search Failed"}
                return jsonify(error)
            con.close()

@app.route('/gethistory', methods=['POST'])
def gethistory():
    try:
        page = request.json.get('page', 1)
        limit = 10
        offset = (page - 1) * limit

        with sql.connect(DATABASE) as con:
            cur = con.cursor()

            # Get total transaction count
            cur.execute("SELECT COUNT(*) FROM vendinghistory")
            total_transactions = cur.fetchone()[0]

            # Get paginated records
            query = """
                SELECT 
                    employees.name,
                    employees.empID,
                    employees.cardID,
                    vendinghistory.itemType,
                    vendinghistory.amount,
                    vendinghistory.status,
                    vendinghistory.logDate
                FROM vendinghistory
                INNER JOIN employees 
                    ON vendinghistory.cardID = employees.cardID
                ORDER BY vendinghistory.logDate DESC
                LIMIT ? OFFSET ?
            """

            cur.execute(query, (limit, offset))
            users = cur.fetchall()

            response = {
                "success": True,
                "page": page,
                "limit": limit,
                "total_transactions": total_transactions,
                "total_pages": (total_transactions + limit - 1) // limit,
                "users": users
            }

            return jsonify(response)

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })

@app.route('/addhistory', methods = ['POST'])
def addhistory():
    try:
        error = None
        if request.method == 'POST':
            data = request.get_json()
            cardID = data.get("cardID")
            itemType = data.get("itemType")
            
            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO vendinghistory (cardID, itemType, amount, status) VALUES (?,?,?,?)", (cardID, itemType, 1, 1))
                con.commit()
                cur.execute("SELECT employees.name, employees.empID, employees.cardID, vendinghistory.itemType, vendinghistory.amount,vendinghistory.status, vendinghistory.logDate FROM vendinghistory INNER JOIN employees ON vendinghistory.cardID=employees.cardID WHERE vendinghistory.cardID=?",(cardID,))
                users=cur.fetchall()
                if users !=None:
                    response = {"success": True,"users": users}
                    return jsonify(response)
                else:
                    error = {"success": False,"message": "Adding Employee Failed"}
                    return jsonify(error)
                con.close()
                
    except Exception as e:
        error = {"success": False,"message": e}
        return jsonify(error)

@app.route('/searchhistory', methods = ['POST'])
def searchhistory():
    try:
        error = None
        if request.method == 'POST': 
            data = request.get_json()
            cardID = data.get("cardID")
            date = data.get("date")        
            print("date is ",{cardID,date})   
            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                if date=="":
                    print("date is empty")
                    cur.execute("SELECT employees.name, employees.empID, employees.cardID, vendinghistory.itemType, vendinghistory.amount,vendinghistory.status, vendinghistory.logDate FROM vendinghistory INNER JOIN employees ON vendinghistory.cardID=employees.cardID WHERE vendinghistory.cardID=?", (cardID,))
                elif cardID=="":
                    print("cardID is empty")
                    cur.execute("SELECT employees.name, employees.empID, employees.cardID, vendinghistory.itemType, vendinghistory.amount,vendinghistory.status, vendinghistory.logDate FROM vendinghistory INNER JOIN employees ON vendinghistory.cardID=employees.cardID WHERE DATE(vendinghistory.logDate)=?", (date,))    
                elif cardID!="" and date!="":
                    print("data is not empty")
                    cur.execute("SELECT employees.name, employees.empID, employees.cardID, vendinghistory.itemType, vendinghistory.amount,vendinghistory.status, vendinghistory.logDate FROM vendinghistory INNER JOIN employees ON vendinghistory.cardID=employees.cardID WHERE vendinghistory.cardID=? AND DATE(vendinghistory.logDate)=?", (cardID,date,))
                users=cur.fetchall()
                if users !=None:
                    response = {"success": True,"users": users}
                    return jsonify(response)
                else:
                    error = {"success": False,"message": "Adding Employee Failed"}
                    return jsonify(error)
                con.close()
                
    except Exception as e:
        error = {"success": False,"message": e}
        return jsonify(error)

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

@app.route('/changemachinestatus',methods = ['POST'])
def changemachinestatus():
   if request.method == 'POST':
        try:
            data = request.get_json()
            status = data.get("status")
            print('status:',status)
            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("UPDATE mdbevent SET dailylimit=?,machineStatus=?",(5,status,))                
                con.commit()
                mdbdevice.setLED(status)
                response = {"success": True}
                return jsonify(response)
        except:
            con.rollback()
            response = {"success": False}
            return jsonify(response)     

@app.route('/list')
def list():
   con = sql.connect(DATABASE)
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * FROM students")
   
   rows = cur.fetchall(); 
   return render_template("list.html",rows = rows)

# SOCKET IO
# client connects
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    mdbdevice.currentsocketstatus()

# disconnect
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")
    socketio.emit('response', {'data':0})

@socketio.on('connected')
def page_connected(msg):
    print("Client msg:",msg)

if __name__ == '__main__':
    try:
        # logging_thread = setup_logging(app)
        # logging_thread.start()
        rfidthread.start()
        mdbdevicethread.start()
        reset_tables(1)
        print("Current Thread count: %i." % threading.active_count())
        # mdbthread.join()
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except:
        print("error")