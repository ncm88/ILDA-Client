import serial
import time

class UART_Sender:

    def __init__(self, uart_port: str, baud):
        self.uart_port = uart_port
        self.baud = baud
        self.conn = None

    
    def open_connection(self):
        try:
            self.serial_connection = serial.Serial(self.uart_port, self.baud_rate, timeout=1)
            print(f"Opened {self.uart_port} at {self.baud_rate} baud.")
        except serial.SerialException as e:
            print(f"Failed to open serial port {self.uart_port}: {e}")
            self.serial_connection = None


    def send_file(self, file_path):
        if self.serial_connection and self.serial_connection.isOpen():
            try:
                with open(file_path, 'rb') as file:
                    while True:
                        chunk = file.read(1024)  # Read in chunks of 1024 bytes
                        if not chunk:
                            break  # End of file
                        self.serial_connection.write(chunk)
                        time.sleep(0.01)  # Give the receiver time to process the data (adjust as necessary)
                print(f"Finished sending {file_path}.")
            except IOError as e:
                print(f"Error opening file {file_path}: {e}")
        else:
            print("Serial connection not open. Call open_connection() first.")


    def close_connection(self):
        if self.serial_connection and self.serial_connection.isOpen():
            self.serial_connection.close()
            print("Closed serial connection.")


    def __del__(self):
        self.close_connection()

    