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
    parser.add_argument('points_per_second', type=int, help='Specify points per second')
    parser.add_argument('travel', type=float, help='Specify travel')

    # Parse the arguments
    args = parser.parse_args()

    # Create instances and perform operations based on the provided arguments
    handler = ILDA_Handler(args.ildaPath, args.travel, args.travel)
    sender = UART_Sender(args.port, args.baud, handler)
    sender.open_connection()
    sender.stream_ilda(args.points_per_second)

if __name__ == '__main__':
    main()
