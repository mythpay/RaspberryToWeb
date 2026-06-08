import sqlite3
from datetime import datetime
conn = sqlite3.connect("mdb.db", check_same_thread=False)

def updateEmployee(itemType, amount, status):    # status 1-success, 0-fail
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = conn.cursor()
        cur.execute("SELECT currentCard FROM session")
        cardID = cur.fetchone()[0]
        print("updateEmp itemType:", itemType)
        print("updateEmp cardId:", cardID)
        if cardID!="" and cardID is not None:
            cur.execute("UPDATE employees SET leftItem=leftItem-1 WHERE cardID=?",(cardID,))
            conn.commit()
            cur.execute("UPDATE session SET currentCard=?, vendStatus=?",("", 0,))
            conn.commit()    
            cur.execute("INSERT INTO vendinghistory (cardID, itemType, amount, status, logDate) VALUES (?,?,?,?,?)", (cardID, itemType, 1, status, now,))        
            conn.commit()
            print("updateEmployee Success:", cardID)
            return True
        else:
            print("updateEmployee failed")
            return False
    except Exception as e:
        print("updateEmployee failed", e)
        return False

def rfid_login(card_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE cardID = ? and leftItem>0 and status=1", (card_id,))
    user = cur.fetchone()

    # cur.execute("UPDATE employees SET leftItem=20 WHERE cardID=?",(card_id,))
    # conn.commit()
    print("user:",user)
    cur.execute("SELECT machineStatus FROM mdbevent")
    machineStatus = cur.fetchone()
    print("machineStatus",machineStatus[0])
    if user:
        cur.execute("UPDATE session SET currentCard=?,vendStatus=?",(card_id, machineStatus[0],))    
        conn.commit()
        # cur.execute("INSERT INTO session (currentCard, vendStatus) VALUES (?,?)", (card_id,1))
        print("rfid-valid-success")
        return True      
    print("rfid-valid-failed")
    return False

def check_rfid_login():
    cur = conn.cursor()
    cur.execute("SELECT currentCard FROM session where vendStatus=1")
    currentCard = cur.fetchone()
    print("currentCard:",currentCard)   
    cur.execute("UPDATE session SET vendStatus=?",( 0,))    
    conn.commit()
    if currentCard[0]!="":
        print("rfid-logged in")
        return True  
    print("rfid-logged out")
    return False