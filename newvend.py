import serial
import time
import gpiod
from gpiod.line import Direction, Value
from database import updateEmployee, check_rfid_login

buffer = b""
class MDBVendingMachine:

    def __init__(
        self,
        socketio,
        PORT='/dev/ttyUSB0',
        BAUDRATE = 9600,
        VMC_SCALE = 50,
        GPIO_CHIP = "/dev/gpiochip0",
        LINE =5,
    ):

        self.ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )    
        self.vmcready = True
        self.item = ""
        self.socketio = socketio
        self.socketiodata=0
        self.VMC_SCALE = VMC_SCALE
        self.LINE = LINE
        # GPIO setup
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

        print(f"Connected to {PORT}")

    # -----------------------------
    # Send raw MDB hex command
    # -----------------------------
    def checksum(self, hex_cmd):
        data = bytes.fromhex(hex_cmd)   
        return sum(data) & 0xFF
    
    def send(self, hex_cmd):
        
        cs   = self.checksum(hex_cmd)
        full = hex_cmd + f'{cs:02X}'
        data = bytes.fromhex(full)

        self.ser.write(data)
        print(f"SENT: {full}")

        time.sleep(0.15)

    def read_frame(self):
        global buffer
        buffer =buffer+ self.ser.read(self.ser.in_waiting or 1)
        
        # print("buffer:",buffer)
        while b'\x02' in buffer and b'\x03' in buffer:
            start = buffer.find(b'\x02')
            end   = buffer.find(b'\x03', start + 1)
            if start != -1 and end != -1:
                frame = buffer[start+1:end]
                buffer = buffer[end+1:]
                try:
                    ascii_str = frame.decode('ascii').strip()
                    cmd = bytes.fromhex(ascii_str).hex().upper()
                    if cmd and cmd != '1010':
                        return cmd
                except:
                    pass
        return None


    # -----------------------------
    # Enable vending device
    # -----------------------------
    def begin_session(self):
        print("\n>> Begin Session...")
        # Send max credit in VMC scale units
        # $655 / $0.50 per unit = 1310 units = 0x051E
        self.vmcready=True
        self.item=""
        self.send('03FFFF')

    # -----------------------------
    # Approve vend
    # -----------------------------
    def approve_vend(self, price_hex):

        # MDB cashless vend approved
        price = int(price_hex, 16) / 100
        print(f">> Approving ${price:.2f}...")
        # 05 = Vend Approved
        # 00 = no surcharge
        # price_hex = exact amount

        self.send('0500'+price_hex)

    # -----------------------------
    # Deny vend
    # -----------------------------
    def deny_vend(self):
        print(">> Denying vend...")
        self.vmcready=False
        self.item=""
        self.send('06')

    # -----------------------------
    # Cancel session
    # -----------------------------
    def end_session(self):
        print(">> End Session...")
        # 07 = End Session
        self.vmcready=False
        self.item=""
        self.send('07')

    def handle_vend(self, cmd, offset=4):
        try:
            if check_rfid_login()==True:
                price_raw = int(cmd[offset:offset+4], 16)
                # item      = int(cmd[offset+4:offset+8], 16)
                itemtype      = int(cmd[offset+4:offset+8])
                price     = price_raw * 50/100
                # Convert actual price back to cents for approval
                price_cents = int(price * 100)
                price_hex = f'{price_raw:04X}'
                print(f"-- VEND REQUEST: Item #{itemtype} Price:${price:.2f} --")
                self.vmcready=True
                self.item=itemtype
                self.approve_vend(price_hex)
            else:
                self.deny_vend()
        except Exception as e:
            print(f"Error: {e}")
    # -----------------------------
    # Close serial
    # -----------------------------
    def close(self):

        self.ser.close()

        print("Serial closed")

    def currentsocketstatus(self):
        self.socketio.emit('response', {'data':self.socketiodata})
    # -----------------------------
    # Listen for incoming MDB data
    # -----------------------------
    def listen(self):
        print("Starting vending system...")
        self.send('0102000132020500')
        self.send('0957544E3131313433363430303636204756433120202020202020208395')
        self.begin_session()
        lasttime=time.time()
        while True:
            cmd = self.read_frame()
            time.sleep(0.1)
            
            if not cmd:
                continue

            print(f"VMC: {cmd}")
            print(f"vmcready: {self.vmcready}")
            print(f"item: {self.item}")
                
            # Config
            if '11000204010018' in cmd:
                print("-- Config --",bytes.fromhex('0102000132020500'))
                # send('0102000132020500')

            # Expansion
            elif '170057544' in cmd:
                print("-- Expansion --")
                # send('0957544E3131313433363430303636204756433120202020202020208395')
            
            # # VMC Ready
            if '140115' in cmd:
                duration=time.time()-lasttime
                lasttime=time.time()
                print("-- VMC READY --",duration)
                self.request.set_value(self.LINE, Value.ACTIVE)
                self.socketiodata=1
                self.socketio.emit('response', {'data':1})
                if self.vmcready==True and self.item!="":
                    updateEmployee(self.item, 1, 1)
                self.begin_session()
                # session_open = True

            # # Reader disabled
            elif '140114' in cmd:
                print("-- Reader disabled --")
                self.begin_session()
                # session_open = True

            # Price range
            elif cmd.startswith('1101'):
                max_p = int(cmd[4:8], 16) / 100
                min_p = int(cmd[8:12], 16) / 100
                print(f"-- Price Range: ${min_p:.2f} - ${max_p:.2f} --")

            # # Vend Request alternate
            # elif cmd.startswith('3400') and len(cmd) >= 12:            
            #     time.sleep(0.1)
            #     # deny_vend()

            # Vend Request standard
            elif '1300' in cmd and len(cmd) >= 12:
                start=cmd.find('1300')
                cmdtmp=cmd[start:len(cmd)]
                print("cmdtmp:",cmdtmp)
                self.handle_vend(cmd, 4)

            # Negative vend
            elif cmd.startswith('1301'):
                print("-- VEND DENIED BY VMC --")
                self.deny_vend()

            # # Vend Success
            elif '1302' in cmd:
                startsc=cmd.find('1302')
                cmdsc=cmd[startsc:len(cmd)]
                # amount = int(cmdsc[4:8], 16) / 100
                itemtype   = int(cmdsc[4:8])
                print(f"-- VEND SUCCESS! Item #{itemtype} $ --")
                # updateEmployee(item, 1, 1)

            # Vend Failure
            elif cmd.startswith('1303'):
                print("-- VEND FAILED --")
                # updateEmployee(int(cmd[4:8]), 1, 0)

            # Session Complete
            elif '130417' in cmd:
                print("-- SESSION COMPLETE --")
                if self.vmcready==True and self.item!="":
                    updateEmployee(self.item, 1, 1)
                self.end_session()
                self.begin_session()

            # # Cancelled
            # elif cmd.startswith('1304'):
            #     print("-- CANCELLED --")
            #     end_session()
            #     session_open = False
            #     begin_session()
            #     session_open = True

            # # Out of sequence
            elif cmd.startswith('0B0B'):
                # send('0B04')    
                self.vmcready=False
                self.request.set_value(self.LINE, Value.INACTIVE)
                self.socketiodata=0
                self.socketio.emit('response', {'data':0})
                self.send('0000')    
                print("-- Out of Sequence --")  

            # # Bill activity Status
            # elif cmd.startswith('3333'):
            #     print("-- Bill activity Status --")
            #     # ser.reset_input_buffer()
            #     # ser.reset_output_buffer()


    def run(self):
        try:
            self.listen()
        except Exception as e:
            print("error newvend:",e)
            self.end_session()
            self.close()