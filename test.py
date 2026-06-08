import serial
import time
from threading import Thread
from queue import Queue

# ============================================================
# CONFIG
# ============================================================

PORT = '/dev/ttyUSB0'
BAUDRATE = 9600

# VMC scale factor
VMC_SCALE = 50

# Fast non-blocking timeout
SERIAL_TIMEOUT = 0.001

# ============================================================
# SERIAL
# ============================================================

ser = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=SERIAL_TIMEOUT
)

# ============================================================
# GLOBALS
# ============================================================

running = True

buffer = bytearray()

packet_queue = Queue()

last_vmc_ready = 0
config_done = False


# ============================================================
# UTILITY
# ============================================================

def log(msg):
    print(f"[{time.time():.3f}] {msg}")


def hex_dump(data):
    return ' '.join(f'{b:02X}' for b in data)


def checksum_from_bytes(data):
    return sum(data) & 0xFF


def checksum(hex_str):
    data = bytes.fromhex(hex_str)
    return checksum_from_bytes(data)


# ============================================================
# SEND
# ============================================================

def send(hex_str):

    try:

        cs = checksum(hex_str)

        full = hex_str + f'{cs:02X}'

        data = bytes.fromhex(full)

        ser.write(data)

        # important
        ser.flush()

        log(f"TX: {full}")

    except Exception as e:
        log(f"SEND ERROR: {e}")


def send_raw(data):

    try:

        ser.write(data)

        ser.flush()

        log(f"TX RAW: {hex_dump(data)}")

    except Exception as e:
        log(f"SEND RAW ERROR: {e}")


# ============================================================
# SESSION CONTROL
# ============================================================

def begin_session():

    # global session_active

    # if session_active:
    #     return

    log("BEGIN SESSION")
    send('030064')

    # session_active = True


def approve_vend(price_hex):

    log(f"APPROVE VEND: {price_hex}")

    # 05 = Vend Approved
    # 00 = no surcharge

    send('0500' + price_hex)


def deny_vend():

    log("DENY VEND")

    send('06')


def end_session():

    log("END SESSION")

    send('07')


# ============================================================
# FRAME READER
# ============================================================

def uart_reader():

    global buffer

    log("UART reader started")

    while running:

        try:

            incoming = ser.read(ser.in_waiting or 1)

            if incoming:

                buffer.extend(incoming)

                # Parse STX/ETX framed packets
                while b'\x02' in buffer and b'\x03' in buffer:

                    start = buffer.find(b'\x02')

                    end = buffer.find(b'\x03', start + 1)

                    if start == -1 or end == -1:
                        break

                    frame = bytes(buffer[start + 1:end])

                    # remove processed data
                    buffer = buffer[end + 1:]

                    try:

                        ascii_str = frame.decode('ascii').strip()

                        raw_bytes = bytes.fromhex(ascii_str)

                        cmd = raw_bytes.hex().upper()

                        if cmd and cmd != '1010':

                            packet_queue.put(cmd)

                    except Exception as e:

                        log(f"FRAME PARSE ERROR: {e}")

        except Exception as e:

            log(f"UART ERROR: {e}")


# ============================================================
# VEND HANDLER
# ============================================================

def handle_vend(cmd, offset=4):

    try:

        price_raw = int(cmd[offset:offset + 4], 16)

        item = int(cmd[offset + 6:offset + 8], 16)

        price = (price_raw * VMC_SCALE) / 100

        price_hex = f'{price_raw:04X}'

        log(f"VEND REQUEST -> ITEM:{item} PRICE:${price:.2f}")

        # MDB requires FAST response
        approve_vend(price_hex)

    except Exception as e:

        log(f"VEND ERROR: {e}")


# ============================================================
# PACKET PROCESSOR
# ============================================================
def clean_packet(cmd):

    """
    Remove converter framing/prefix bytes
    """

    # remove common converter RX prefix
    if cmd.startswith('333300'):
        cmd = cmd[6:]

    # remove ACK noise
    if cmd == '00':
        return None

    # remove converter noise
    if cmd == 'EF':
        return None

    # remove empty ACK packet
    if cmd == '1010':
        return None
    
    if cmd == '10101010':
        return None
    return cmd

def add_checksum(hex_str):
    data = bytes.fromhex(hex_str)
    cs = sum(data) & 0xFF
    return hex_str + f"{cs:02X}"

def packet_processor():

    global last_vmc_ready
    log("Packet processor started")

    while running:

        try:

            raw_cmd = packet_queue.get()

            log(f"RAW RX: {raw_cmd}")

            # --------------------------------------------
            # CLEAN CONVERTER PREFIXES
            # --------------------------------------------

            cmd = clean_packet(raw_cmd)

            if not cmd:
                continue

            log(f"MDB RX: {cmd}")

            # --------------------------------------------
            # CONFIG
            # --------------------------------------------

            if cmd.startswith('11000204010018'):

                global config_done
                if not config_done:
                    send('0102000132020500')
                    config_done = True

            # --------------------------------------------
            # EXPANSION REQUEST
            # --------------------------------------------

            elif cmd.startswith('170057544'):

                log("EXPANSION REQUEST")
                expansion = "0957544E313131343336343030363620475643312020202020202020"
                send(add_checksum(expansion))

            # --------------------------------------------
            # VMC READY
            # --------------------------------------------

            elif cmd.startswith('140115'):

                log("VMC READY")

                # session_active = False
                begin_session()
            # --------------------------------------------
            # PRICE RANGE
            # --------------------------------------------

            elif cmd.startswith('1101'):

                max_raw = int(cmd[4:8], 16)
                min_raw = int(cmd[8:12], 16)

                max_p = (max_raw * VMC_SCALE) / 100
                min_p = (min_raw * VMC_SCALE) / 100

                log(f"PRICE RANGE ${min_p:.2f} - ${max_p:.2f}")
                # ACK
                ser.write(b'\x00')
                log("TX: ACK 00")

            # --------------------------------------------
            # VEND REQUEST
            # --------------------------------------------

            elif cmd.startswith('1300') and len(cmd) >= 12:

                handle_vend(cmd, 4)

            # --------------------------------------------
            # VEND DENIED
            # --------------------------------------------

            elif cmd.startswith('1301'):

                log("VEND DENIED")

            # --------------------------------------------
            # VEND SUCCESS
            # --------------------------------------------

            elif cmd.startswith('1302'):

                try:

                    item = int(cmd[4:8], 16)

                    log(f"VEND SUCCESS ITEM:{item}")

                except:

                    log("VEND SUCCESS")

            # --------------------------------------------
            # SESSION COMPLETE
            # --------------------------------------------

            elif cmd.startswith('130417'):

                log("SESSION COMPLETE")
                # session_active = False

                end_session()

                begin_session()

            # --------------------------------------------
            # OUT OF SEQUENCE
            # --------------------------------------------

            elif cmd.startswith('0B0B'):

                log("OUT OF SEQUENCE")

            # --------------------------------------------
            # BILL ACTIVITY
            # --------------------------------------------

            elif cmd.startswith('3333'):

                log("BILL ACTIVITY")

            # --------------------------------------------
            # UNKNOWN
            # --------------------------------------------

            else:

                log(f"UNKNOWN MDB: {cmd}")

        except Exception as e:

            log(f"PROCESS ERROR: {e}")

# ============================================================
# STARTUP
# ============================================================




# ============================================================
# MAIN
# ============================================================

def main():

    log("====================================")
    log("MDB CASHLESS STARTED")
    log("====================================")


    reader_thread = Thread(target=uart_reader, daemon=True)

    processor_thread = Thread(target=packet_processor, daemon=True)

    reader_thread.start()

    processor_thread.start()

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        global running

        running = False

        log("STOPPING")

        try:
            end_session()
        except:
            pass

        ser.close()


# ============================================================
# ENTRY
# ============================================================

if __name__ == '__main__':
    main()