import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 9600
STX  = 0x02
ETX  = 0x03

ser = serial.Serial(port=PORT, baudrate=BAUD,
    bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE, timeout=0.1)

print("Listening for 60 seconds - power cycle machine now...")
print("Showing EVERYTHING received\n")

start = time.time()
buf   = b""

while time.time() - start < 60:
    chunk = ser.read(64)
    if chunk:
        buf += chunk
        while True:
            s = buf.find(bytes([STX]))
            if s == -1:
                buf = b""
                break
            e = buf.find(bytes([ETX]), s+1)
            if e == -1:
                buf = buf[s:]
                break
            inner = buf[s+1:e]
            try:
                decoded = inner.decode("ascii").strip()
            except:
                decoded = inner.hex()
            print(f"[{time.time()-start:.1f}s] {decoded}")
            buf = buf[e+1:]

ser.close()
print("\nDone.")
