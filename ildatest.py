import os
import struct
import matplotlib.pyplot as plt
from pylib.ilda_handler import ILDA_Handler

# Generate the binary file first
handler = ILDA_Handler("datafiles/letters/0.ild")

# Path to the binary file
file_path = 'client_output/target.bin'


def abs_to_signed(value, angular_resolution):
    if value > angular_resolution // 2:
        return value - angular_resolution
    return value

if os.path.exists(file_path):
    x_coords = []
    y_coords = []
    colors = []

    # Open the binary file and read the points
    with open(file_path, 'rb') as file:
        # Read all points
        point_data = file.read()

        # Assume each point structure in the binary file is 8 bytes: 2 for x, 2 for y, 1 for status, and 3 padding bytes
        point_format = '<HHBxxx'  # Adjust if the structure changes
        point_size = struct.calcsize(point_format)

        # Iterate over the data by the size of each point data structure
        for i in range(0, len(point_data), point_size):
            # Unpack the data for each point
            x, y, status = struct.unpack(point_format, point_data[i:i + point_size])

            # Convert from absolute values to signed values, based on the handler's angular resolution
            x = abs_to_signed(x, handler.angular_resolution)
            y = abs_to_signed(y, handler.angular_resolution)

            # Append the coordinates and color based on the blank bit
            x_coords.append(x)
            y_coords.append(y)
            colors.append('red' if status & 0x01 else 'blue')


    # Plot the points
    plt.scatter(x_coords, y_coords, c=colors)
    plt.title("Point Plot")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()
else:
    print(f"File {file_path} does not exist.")

print(handler.point_dict)