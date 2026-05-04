import spidev
import gpiod
from gpiod import Direction, Value
import threading
import time

# --- Configuration ---
RST_PIN = 25
SPI_BUS = 0
SPI_DEVICE = 0

# --- RC522 Registers ---
CommandReg    = 0x01
ComIEnReg     = 0x02
ComIrqReg     = 0x04
ErrorReg      = 0x06
FIFODataReg   = 0x09
FIFOLevelReg  = 0x0A
BitFramingReg = 0x0D
ModeReg       = 0x11
TxControlReg  = 0x14
TxASKReg      = 0x15
TModeReg      = 0x2A
TPrescalerReg = 0x2B
TReloadRegH   = 0x2C
TReloadRegL   = 0x2D

# --- SPI Setup ---
spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEVICE)
spi.max_speed_hz = 1000000
spi.mode = 0

# --- GPIO Setup (gpiod v2 API) ---
GPIO_CHIP = '/dev/gpiochip0'

request = gpiod.request_lines(
    GPIO_CHIP,
    consumer="rc522",
    config={
        RST_PIN: gpiod.LineSettings(
            direction=Direction.OUTPUT,
            output_value=Value.ACTIVE
        )
    }
)

class RFID(threading.Thread):
    def rst_set(val):
        request.set_value(RST_PIN, Value.ACTIVE if val else Value.INACTIVE)

    # --- SPI Helpers ---
    def write_reg(reg, val):
        spi.xfer2([((reg << 1) & 0x7E), val])

    def read_reg(reg):
        return spi.xfer2([((reg << 1) & 0x7E) | 0x80, 0])[1]

    def set_bit_mask(reg, mask):
        write_reg(reg, read_reg(reg) | mask)

    def clear_bit_mask(reg, mask):
        write_reg(reg, read_reg(reg) & (~mask))

    # --- RC522 Functions ---
    def rc522_init():
        rst_set(0)
        time.sleep(0.05)
        rst_set(1)
        time.sleep(0.05)
        write_reg(TModeReg,     0x80)
        write_reg(TPrescalerReg,0xA9)
        write_reg(TReloadRegH,  0x03)
        write_reg(TReloadRegL,  0xE8)
        write_reg(TxASKReg,     0x40)
        write_reg(ModeReg,      0x3D)
        set_bit_mask(TxControlReg, 0x03)
        print("RC522 initialized")

    def communicate(command, send_data):
        recv_data = []
        write_reg(ComIEnReg, 0x77)
        clear_bit_mask(ComIrqReg, 0x80)
        set_bit_mask(FIFOLevelReg, 0x80)
        write_reg(CommandReg, 0x00)

        for b in send_data:
            write_reg(FIFODataReg, b)

        write_reg(CommandReg, command)
        if command == 0x0C:
            set_bit_mask(BitFramingReg, 0x80)

        i = 2000
        while True:
            irq = read_reg(ComIrqReg)
            i -= 1
            if not (i != 0 and not (irq & 0x01) and not (irq & 0x30)):
                break

        clear_bit_mask(BitFramingReg, 0x80)

        if i == 0:
            return "TIMEOUT", [], 0

        if read_reg(ErrorReg) & 0x1B:
            return "ERROR", [], 0

        n = read_reg(FIFOLevelReg)
        for _ in range(n):
            recv_data.append(read_reg(FIFODataReg))

        return "OK", recv_data, n

    def request_card():
        write_reg(BitFramingReg, 0x07)
        status, _, _ = communicate(0x0C, [0x26])
        return status

    def read_uid():
        write_reg(BitFramingReg, 0x00)
        status, recv, _ = communicate(0x0C, [0x93, 0x20])
        if status == "OK" and len(recv) >= 4:
            return recv[:4]
        return None

    # --- Main ---
    rc522_init()
    print("\nHold your card near the reader...")

try:
    last_uid = None
    while True:
        if request_card() == "OK":
            uid = read_uid()
            if uid and uid != last_uid:
                uid_str = ' '.join([hex(b) for b in uid])
                decimal_id = int.from_bytes(uid[:4], byteorder='little')
                print(f"\n Card detected!")
                print(f"   UID (hex)     : {uid_str}")
                print(f"   UID (decimal) : {decimal_id}")
                last_uid = uid
        else:
            last_uid = None
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopped.")
finally:
    spi.close()
    request.release()
