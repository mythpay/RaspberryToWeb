import spidev
import gpiod
from gpiod.line import Direction, Value
import time
import requests
import threading
from database import rfid_login
from vend import MDBParser

class RFIDCard(threading.Thread):

    # --- Registers ---
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

    GPIO_CHIP = "/dev/gpiochip0"

    def __init__(self, spi_bus=0, spi_device=0, rst_pin=25):

        self.RST_PIN = rst_pin

        # SPI setup
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000
        self.spi.mode = 0
        self.parser = MDBParser()
        # GPIO setup
        self.request = gpiod.request_lines(
            self.GPIO_CHIP,
            consumer="rc522",
            config={
                self.RST_PIN: gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value.ACTIVE
                )
            }
        )

        self.last_uid = None
        self.last_read_time = time.time()

    # --- GPIO ---
    def rst_set(self, val: bool):
        self.request.set_value(
            self.RST_PIN,
            Value.ACTIVE if val else Value.INACTIVE
        )

    # --- SPI Helpers ---
    def write_reg(self, reg, val):
        self.spi.xfer2([((reg << 1) & 0x7E), val])

    def read_reg(self, reg):
        return self.spi.xfer2([((reg << 1) & 0x7E) | 0x80, 0])[1]

    def set_bit_mask(self, reg, mask):
        self.write_reg(reg, self.read_reg(reg) | mask)

    def clear_bit_mask(self, reg, mask):
        self.write_reg(reg, self.read_reg(reg) & (~mask))

    # --- Init ---
    def init(self):
        self.rst_set(0)
        time.sleep(0.05)
        self.rst_set(1)
        time.sleep(0.05)

        self.write_reg(self.TModeReg, 0x80)
        self.write_reg(self.TPrescalerReg, 0xA9)
        self.write_reg(self.TReloadRegH, 0x03)
        self.write_reg(self.TReloadRegL, 0xE8)
        self.write_reg(self.TxASKReg, 0x40)
        self.write_reg(self.ModeReg, 0x3D)
        self.set_bit_mask(self.TxControlReg, 0x03)

        print("RC522 initialized")

    # --- Core Communication ---
    def communicate(self, command, send_data):

        recv_data = []

        self.write_reg(self.ComIEnReg, 0x77)
        self.clear_bit_mask(self.ComIrqReg, 0x80)
        self.set_bit_mask(self.FIFOLevelReg, 0x80)
        self.write_reg(self.CommandReg, 0x00)

        for b in send_data:
            self.write_reg(self.FIFODataReg, b)

        self.write_reg(self.CommandReg, command)

        if command == 0x0C:
            self.set_bit_mask(self.BitFramingReg, 0x80)

        i = 2000

        while True:
            irq = self.read_reg(self.ComIrqReg)
            i -= 1
            if not (i != 0 and not (irq & 0x01) and not (irq & 0x30)):
                break

        self.clear_bit_mask(self.BitFramingReg, 0x80)

        if i == 0:
            return "TIMEOUT", [], 0

        if self.read_reg(self.ErrorReg) & 0x1B:
            return "ERROR", [], 0

        n = self.read_reg(self.FIFOLevelReg)

        for _ in range(n):
            recv_data.append(self.read_reg(self.FIFODataReg))

        return "OK", recv_data, n

    # --- Card functions ---
    def request_card(self):
        self.write_reg(self.BitFramingReg, 0x07)
        status, _, _ = self.communicate(0x0C, [0x26])
        return status

    def read_uid(self):
        self.write_reg(self.BitFramingReg, 0x00)
        status, recv, _ = self.communicate(0x0C, [0x93, 0x20])

        if status == "OK" and len(recv) >= 4:
            return recv[:4]

        return None

    # --- Run loop ---
    def run(self):

        self.init()
        print("\nHold your card near the reader...")

        try:
            while True:
                try:
                    if self.request_card() == "OK":

                        uid = self.read_uid()
                        now=time.time()
                        # print("now time:",(now-self.last_read_time))
                        if uid and (uid != self.last_uid or (now-self.last_read_time)>5):

                            decimal_id = int.from_bytes(uid[:4], byteorder="little")

                            print("\nCard detected!")
                            print("UID:", uid)
                            print("Decimal:", decimal_id)

                            res = rfid_login(decimal_id)
                            print("API response:",res)
                            self.last_uid = uid
                            self.last_read_time = now

                    else:
                        self.last_uid = None

                    time.sleep(0.1)
                except KeyboardInterrupt:
                    break

        except KeyboardInterrupt:
            print("\nStopped.")

        finally:
            self.spi.close()
            self.request.release()
