from pylib.uart_sender import UART_Sender 
from pylib.ilda_handler import ILDA_Handler


handler = ILDA_Handler("datafiles/letters/0.ild")
sender = UART_Sender('/dev/tty.usbmodem1203', 115200, handler)
sender.open_connection()
sender.stream_ilda(10/1000)










'''
def data_step():
    ser = serial.Serial('/dev/tty.usbmodem1203', 115200)  
    # Create a binary file
    with open("data.bin", "wb") as bin_file:
        for index in range(4200):  # Create 4200 points
            x = index
            y = index
            laser = 1
            visited = 0
            data = struct.pack('<HHBBH', x, y, laser, visited, index)
            ser.write(data)
            time.sleep(10/1000)
    ser.close()

    # Open serial connection to the STM32
    # Replace '/dev/ttyUSB0' with your STM32's serial port
    
    # Open the binary file for reading
    #with open("data.bin", "rb") as bin_file:
        #data = bin_file.read()  # Read the binary data

        # Send the data over UART
        #ser.write(data)

    # Close the serial connection
    #ser.close()
data_step()

'''










