import serial
import threading
import time
from collections import deque
from queue import Queue

class MDBParser:
    def __init__(self):
        self.buffer = deque()
        self.lock = threading.Lock()
        self.rx_queue = b""
        self.buf = b""
    def feed(self, data: bytes):
        with self.lock:

            self.rx_queue =data
            # for b in data:
            #     self.buffer.append(b)
        # print("self.buffer:",self.buffer)
        # print("self.rx_queue:",self.rx_queue)

    def extract_frames(self):
        """
        MDB is byte-stream based. We reconstruct frames.
        This version assumes:
        - 0x02/0x03/0x04/0x11/0x17 etc are command headers
        - unknown noise ignored
        """
        frames = []

        with self.lock:
            tempqueue = self.rx_queue
            self.rx_queue=b""  
        # print("length:",len(self.rx_queue))
        if len(tempqueue)>0:
            if b'\x03' in tempqueue:
                # print("queue reset:---")
                tempbuf=self.buf+tempqueue
                print("extract buf:",tempbuf)
                self.buf=b""
                # i = 0
                # while i < len(buf):

                #     b = buf[i]

                #     # ignore idle / noise bytes
                #     if b in (0x00, 0xFF):
                #         i += 1
                #         continue

                #     # CONFIG REQUEST example (0x11 ...)
                #     if b == 0x11 and i + 5 < len(buf):
                #         frame = buf[i:i+7]
                #         frames.append(bytes(frame))
                #         i += 7
                #         continue

                #     # EXPANSION REQUEST (0x17 ...)
                #     if b == 0x17 and i + 20 < len(buf):
                #         frame = buf[i:i+30]
                #         frames.append(bytes(frame))
                #         i += 30
                #         continue

                #     # BILL ACTIVITY / generic short packet
                #     if b == 0x0B and i + 2 < len(buf):
                #         frame = buf[i:i+3]
                #         frames.append(bytes(frame))
                #         i += 3
                #         continue

                #     # fallback single-byte junk → discard
                #     i += 1

                return tempbuf
            else:
                self.buf+=tempqueue     
        
        return None

class MDBDevice:
    def __init__(self, port="/dev/ttyUSB0", baud=9600):
        self.ser = serial.Serial(port, baudrate=baud, timeout=0.1)
        self.parser = MDBParser()
        self.running = True
        self.last_config_time = 0

    # ---------------- TX ----------------

    def send(self, data: bytes):
        self.ser.write(data)

    def send_ack(self):
        # correct MDB ACK pattern
        self.send(bytes([0x00]))

    def send_nack(self):
        self.send(bytes([0xFF]))

    def send_config_response(self):
        # FIX: prevent spam loop (critical bug you currently have)
        now = time.time()
        if now - self.last_config_time < 2:
            return
        self.last_config_time = now

        print("TX: CONFIG RESPONSE")
        self.send(bytes.fromhex("01020001320201003D"))

    def send_expansion_identity(self):
        print("TX: EXPANSION IDENTITY")
        self.send(bytes.fromhex(
            "0957544E31313134333634303036362047564331202020202020202083957B"
        ))

    def begin_session(self):
        print("TX: BEGIN SESSION")
        self.send(bytes.fromhex("03FFFF01"))

    def end_session(self):
        print("TX: END SESSION")
        self.send(bytes([0x07]))

    def approve_vend(self):
        print("TX: APPROVE VEND:")
        self.send(bytes.fromhex("0500000308"))

    def deny_vend(self):
        print("TX: DENY VEND:",bytes([0x06]))
        self.send(bytes([0x06]))

    # ---------------- RX HANDLER ----------------

    def handle_frame(self, frame: bytes):

        if not frame:
            return

        # h = frame[0]

        if b'1100' in frame:
            print("CONFIG REQUEST")
            self.send_config_response()
            self.send_ack()
            return

        if b'1700' in frame:
            print("EXPANSION REQUEST")
            self.send_expansion_identity()
            self.send_ack()
            return

        if b'0B0B' in frame:
            print("BILL ACTIVITY")
            self.send_ack()
            return
        
        if b'1401' in frame:
            print("VMC ENABLE")
            self.begin_session()
            return
        
        if b'1300' in frame:
            print("VEND REQUEST")
            self.approve_vend()
            return
        
        if b'1301' in frame:
            print("VEND CANCEL")
            self.deny_vend()
            return
        print("UNKNOWN FRAME:", frame)
        # self.send_ack()

    # ---------------- THREAD ----------------

    def reader_loop(self):
        print("UART reader started")
        global buffer
        while self.running:
            data = self.ser.read(36)
            if data:
                print("UART reader data:", data)
                self.parser.feed(data)

    def processor_loop(self):
        print("Packet processor started")
        while self.running:
            frame = self.parser.extract_frames()

            # for f in frames:
                # print("MDB RX:", f)
            self.handle_frame(frame)
            time.sleep(0.001)

    # ---------------- START ----------------

    def start(self):
        print("MDB CASHLESS STARTED")
        print("=" * 40)

        threading.Thread(target=self.reader_loop, daemon=True).start()
        threading.Thread(target=self.processor_loop, daemon=True).start()

        self.begin_session()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    dev = MDBDevice("/dev/ttyUSB0")
    try:
        dev.start()
    except KeyboardInterrupt:
        print("STOPPING")
        dev.running = False
        dev.send(bytes([0x07, 0x07]))
        print("END SESSION")