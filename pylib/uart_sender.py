import serial
import struct
import time
from . import ilda_handler

class UART_Sender:

    def __init__(self, uart_port: str, baud: int, handler: ilda_handler.ILDA_Handler):
        self.uart_port = uart_port
        self.baud = baud
        self.serial_connection = None
        self.handler = handler
    
    def open_connection(self):
        try:
            self.serial_connection = serial.Serial(self.uart_port, self.baud, timeout=1)
            print(f"Opened {self.uart_port} at {self.baud} baud.")
        except serial.SerialException as e:
            print(f"Failed to open serial port {self.uart_port}: {e}")
            self.serial_connection = None

    def stream_ilda(self, delay):
        while self.serial_connection and self.serial_connection.is_open and self.handler:
            ptDict = self.handler.point_dict
            for ptNum in ptDict.keys():
                pt = ptDict[ptNum]
                data = struct.pack('<HHBBH', int(pt[0]) & 0xFFFF, int(pt[1]) & 0xFFFF, pt[2] ^ 0x1, pt[3] & 0x1, ptNum & 0xFFFF)
                self.serial_connection.write(data)
                time.sleep(delay)


    def close_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Closed serial connection.")


    def __del__(self):
        self.close_connection()

    