import argparse
from pylib.uart_sender import UART_Sender
from pylib.ilda_handler import ILDA_Handler

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Send ILDA file contents to STM32 laser projector over UART.')

    # Add the arguments
    parser.add_argument('ildaPath', type=str, help='Specify path to ILDA file')
    parser.add_argument('port', type=str, help='Specify UART port')
    parser.add_argument('baud', type=int, help='Specify baud rate')

    # Parse the arguments
    args = parser.parse_args()

    # Create instances and perform operations based on the provided arguments
    handler = ILDA_Handler(args.ildaPath)
    targ = handler.create_binary()

    sender = UART_Sender(args.port, args.baud)
    sender.open_connection()
    sender.send_file(targ)
    sender.close_connection()

if __name__ == '__main__':
    main()
