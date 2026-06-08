import serial
import threading
import time
import gpiod
from gpiod.line import Direction, Value
from queue import Queue
from database import updateEmployee, check_rfid_login

class MDBParser:
    def __init__(self):
        self.worker_queue = Queue()

    def setLED(self, status):
        print("MDBparser, LED:", status)
        self.worker_queue.put({
            "type": "update_led",
            "status": status
        })

class MDBDevice:
    def __init__(self, socketio, port="/dev/ttyUSB0", baud=9600, 
        GPIO_CHIP = "/dev/gpiochip0", LINE =5,):
        self.ser = serial.Serial(port, baudrate=baud, timeout=0.1)
        self.parser = MDBParser()
        self.lock = threading.Lock()
        self.rx_queue = b""
        self.buf = b""
        self.running = True
        self.vmcready=False
        self.last_frame_time = time.time()
        self.has_frame = threading.Event()   
        self.item = ""
        self.handled_events = set()
        self.handled_events.clear()
        self.socketio = socketio
        self.socketiodata=0
        self.machinestatus=0
        # GPIO setup
        self.LINE = LINE
        self.request = gpiod.request_lines(
            GPIO_CHIP,
            consumer="led-blink",
            config={
                self.LINE: gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value.ACTIVE
                )
            }
        )
        self.worker_queue = Queue()

        print(f"Connected to {port}")
    # ---------------- TX ----------------

    def send(self, data: bytes):
        self.ser.write(data)

    def send_ack(self):
        self.send(bytes([0x00]))

    def send_nack(self):
        self.send(bytes([0xFF]))

    def send_config_response(self):
        self.sendchecksum("0102184032020501")
        print("TX: CONFIG RESPONSE")

    def send_expansion_identity(self):
        # self.send(bytes.fromhex(
        #     "0957544E31313134333634303036362047564331202020202020202083957B"
        # ))
        self.sendchecksum("0957544E3131313433363430303636204756433120202020202020208395")

        print("TX: EXPANSION IDENTITY")

    def begin_session(self):
        self.send(bytes.fromhex("03FFFF01"))
        # self.sendchecksum("03FFFF")
        self.handled_events.clear()
        print("TX: BEGIN SESSION:", time.time())
        self.vmcready=True
        self.last_frame_time=time.time()

    def end_session(self):
        self.send(bytes([0x07, 0x07]))
        print("TX: END SESSION")

    def approve_vend(self):
        try:
            if self.already_done("vend"):
                return  
            if check_rfid_login()==True and self.vmcready==True:
                self.send(bytes.fromhex("0500000308")) 
                # self.sendchecksum("05FFFFFFFF")      
                self.mark_done("vend")
                print("TX: APPROVE VEND:")
        except Exception as e:
            self.vmcready=False
            print(f"Error: {e}")

    def deny_vend(self):
        self.send(bytes([0x06, 0x06]))
        print("TX: DENY VEND")

    def feed(self, data: bytes):
        with self.lock:
            if len(data)>0:
                if b'\x03' in data:
                    self.rx_queue=self.buf+data
                    print("extract buf:",self.rx_queue)
                    self.buf=b""
                    self.has_frame.set()
                else:
                    self.buf+=data                

    def already_done(self, key):
        return key in self.handled_events

    def mark_done(self, key):
        self.last_frame_time = time.time()
        self.handled_events.add(key)

    def checksum(self, hex_cmd):
        data = bytes.fromhex(hex_cmd)   
        return sum(data) & 0xFF
    
    def sendchecksum(self, hex_cmd):
        
        cs   = self.checksum(hex_cmd)
        full = hex_cmd + f'{cs:02X}'
        data = bytes.fromhex(full)
        print("Full:", data)
        self.ser.write(data)

    # ---------------- RX HANDLER ----------------
    def handle_frame(self):
        with self.lock:
            frame =self.rx_queue
            if frame==b"":
                return

            # RESET handled events on new session
            if b'1401' in frame:  # VMC ENABLE = session start
                if self.already_done("1401"):
                    return     
                print("VMC ENABLE")       
                self.mark_done("1401")
                self.rx_queue=b""
                self.worker_queue.put({
                    "type": "socketio",
                    "data": 1
                })
                print("self.item:", self.item)
                if self.vmcready==True and self.item!="":
                    self.worker_queue.put({
                        "type": "update_employee",
                        "item": self.item
                    })
                # self.end_session()
                self.begin_session()
                return

            if b'1100' in frame:
                if self.already_done("1100"):
                    return

                print("CONFIG REQUEST")
                self.mark_done("1100")
                print("self.handled_events:", self.handled_events)
                self.send_config_response()
                return

            if b'1700' in frame:
                if self.already_done("1700"):
                    return

                print("EXPANSION REQUEST")
                self.mark_done("1700")
                self.send_expansion_identity()
                return

            if b'0B0B' in frame:
                # if self.already_done("0B0B"):
                #     return
                now=time.time()-self.last_frame_time
                print("time:", now)
                print("BILL ACTIVITY")
                # self.mark_done("0B0B")

                self.send_ack()
                self.vmcready = False
                self.item=""
                self.worker_queue.put({
                    "type": "socketio",
                    "data": 0
                })
                return
            
            if b'1400' in frame:
                # if self.already_done("0B0B"):
                #     return
                now=time.time()-self.last_frame_time
                print("time:", now)
                print("READER DISABLE")
                # self.mark_done("0B0B")
                
                self.send_ack()
                self.vmcready = False
                self.item=""
                self.worker_queue.put({
                    "type": "socketio",
                    "data": 2
                })
                self.handled_events.clear()
                # self.end_session()
                # self.begin_session()
                # self.running=False
                return

            if b'1300' in frame:
                # if self.already_done("1300"):
                #     return

                print("VEND REQUEST")
                # self.mark_done("1300")

                self.approve_vend()

                self.worker_queue.put({
                    "type": "update_itemtype",
                    "item": frame
                })
                return

            if b'1301' in frame:
                if self.already_done("1301"):
                    return

                print("VEND CANCEL")
                self.mark_done("1301")

                self.deny_vend()
                return

            if b'1304' in frame:
                if self.already_done("1304"):
                    return

                print("SESSION COMPLETE")
                self.mark_done("1304")

                if self.vmcready==True and self.item!="":
                    self.worker_queue.put({
                        "type": "update_employee",
                        "item": self.item
                    })

                self.end_session()
                self.begin_session()
                return

            if b'1307' in frame:
                if self.already_done("1307"):
                    return

                print("VEND CANCEL ACK")
                self.mark_done("1307")

                self.send_ack()
                return

            # print("UNKNOWN FRAME:", frame)
    # ---------------- THREAD ----------------
    def setLED(self, status):
        print("Machine Status:", status)
        self.machinestatus=status
        self.worker_queue.put({
            "type": "update_led",
            "status": status
        })
    def reader_loop(self):
        print("UART reader started")
        global buffer
        while self.running:
            data = self.ser.read_all()
            if data:
                # print("UART reader data:", data)
                self.feed(data)

    def processor_loop(self):
        print("Packet processor started")
        while self.running:
            self.has_frame.wait() 
            self.handle_frame()
            self.has_frame.clear()

    def worker_loop(self):
        print("Worker thread started")
        while self.running:
            try:
                task = self.worker_queue.get(timeout=1)
                if task["type"] == "update_employee":
                    updateEmployee(
                        task["item"],
                        1,
                        1
                    )

                elif task["type"] == "socketio":
                    tempLED=0
                    if self.machinestatus==1 and task["data"]==1:
                        print("machinestatus ON - LED ON")
                        tempLED=1
                        self.request.set_value(self.LINE, Value.ACTIVE)
                    else:
                        print("LED OFF")
                        self.request.set_value(self.LINE, Value.INACTIVE)
                    
                    self.socketio.emit(
                        'response',
                        {'data': task["data"]}
                    )
                    print("socketio emit:",task["data"])
                    self.socketiodata = task["data"]

                elif task["type"] == "update_itemtype":                    
                    item=task["item"]
                    index= item.find(b'1300')
                    itemtype = int(item[index+8:index+12].decode())
                    self.item = itemtype
                    print("itemtype:", itemtype)

                if task["type"] == "update_led":
                    tempLED=0
                    if task["status"]==1 and self.socketiodata==1:
                        print("machinestatus ON - LED ON")
                        tempLED=1
                        self.request.set_value(self.LINE, Value.ACTIVE)
                    else:
                        print("LED OFF")
                        self.request.set_value(self.LINE, Value.INACTIVE)
                    
                    # self.socketio.emit(
                    #     'response',
                    #     {'data': tempLED}
                    # )

            except Exception as e:
                pass

    def ack_worker(self):
        while self.running:

            time.sleep(0.5)

            idle_time = time.time() - self.last_frame_time
            if idle_time >= 25:
                print("SENDING PERIODIC ACK (idle state)")
                self.send_ack()
                self.last_frame_time = time.time()
    # ---------------- START ----------------
    def currentsocketstatus(self):
        self.socketio.emit('response', {'data':self.socketiodata})

    def run(self):
        try:
            print("MDB CASHLESS STARTED")
            print("=" * 40)

            threading.Thread(target=self.reader_loop, daemon=True).start()
            threading.Thread(target=self.processor_loop, daemon=True).start()
            threading.Thread(target=self.worker_loop, daemon=True).start()
            # threading.Thread(target=self.ack_worker, daemon=True).start()
            self.begin_session()

            while True:
                time.sleep(1)        
        except KeyboardInterrupt:
            print("STOPPING")
            self.running = False
            self.send(bytes([0x07, 0x07]))
            print("END SESSION")
            self.ser.close()
# if __name__ == "__main__":
#     dev = MDBDevice()
#     dev.start()