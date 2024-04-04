import struct
from typing import List, Tuple
import os
#import matplotlib.pyplot as plt



#ASSUMPTIONS MADE: 
#1) ILDA file has valid path
#2) ILDA image is properly centered
class ILDA_Handler:
    
    def __init__(self, ilda_filename: str, output_dir='client_output/', angular_resolution=48959, xMaxAngleDeg=10, yMaxAngleDeg=10): #denotes 10 degrees of travel in either direction (20 degree arc)
        self.ilda_filename = ilda_filename
        self.output_dir = output_dir
        self.angular_resolution = angular_resolution 
        self.xMaxAngleDeg = xMaxAngleDeg
        self.yMaxAngleDeg = yMaxAngleDeg

        self.raw_point_data: List[Tuple[int, int, bool]] = []
        self.formatted_point_data: List[Tuple[int, int, bool]] = []
        self.path_data: List[Tuple[int, int, bool]] = []
        
        self.extract_point_data()
        self.format_point_data()
        self.create_binary()


    def extract_point_data(self):

        points = []
        with open(self.ilda_filename, 'rb') as file:
            while True:
                # Attempt to read and unpack the header for the next frame
                header_format = '>4s3xB8s8sHHHBB'
                header_size = struct.calcsize(header_format)
                header_data = file.read(header_size)

                # Break if there is no header data, indicating end of file
                if len(header_data) < header_size:
                    break

                header = struct.unpack(header_format, header_data)
                signature, format_type, name_bytes, company_name_bytes, num_points, frame_number, total_frames, scanner_head = header[:8]

                # Verify ILDA file signature for each frame
                if signature != b'ILDA':
                    continue

                # Check format type and set point format
                if format_type in [0, 1]:  # Adjust based on supported format types
                    point_format = '>hhB'
                else:
                    continue  # Skip unsupported format types

                point_size = struct.calcsize(point_format)

                for _ in range(num_points):
                    point_data = file.read(point_size)
                    if len(point_data) < point_size:
                        raise ValueError("Incomplete point data")

                    x, y, status_code = struct.unpack(point_format, point_data)
                    blanking = (status_code & 0x80) != 0
                    points.append((x, y, blanking))

        self.raw_point_data = points
        return self.raw_point_data



    def format_point_data(self):
        minX = min(point[0] for point in self.raw_point_data)
        maxX = max(point[0] for point in self.raw_point_data)
        minY = min(point[1] for point in self.raw_point_data)
        maxY = max(point[1] for point in self.raw_point_data)
        
        xTravel = maxX - minX
        yTravel = maxY - minY
        travelScale = max(xTravel, yTravel)
        
        formatted_points = []
        
        for point in self.raw_point_data:
            # Normalize points to the range [0, 1]
            xNormalized = (point[0] - minX) / travelScale
            yNormalized = (point[1] - minY) / travelScale
            
            # Scale points to the encoder resolution, taking into account the maximum angle
            xCoord = xNormalized * self.angular_resolution * (self.xMaxAngleDeg / 180)
            yCoord = yNormalized * self.angular_resolution * (self.yMaxAngleDeg / 180)
            
            # Center the points around the midpoint of the encoder's range
            xCoord = xCoord - (self.angular_resolution * (self.xMaxAngleDeg / 180) / 2)
            yCoord = yCoord - (self.angular_resolution * (self.yMaxAngleDeg / 180) / 2)

            # Apply signed to absolute conversion if necessary
            xCoord = self.signed_to_abs(xCoord)
            yCoord = self.signed_to_abs(yCoord)

            formatted_points.append((xCoord, yCoord, point[2]))

        self.formatted_point_data = formatted_points
        
        '''
        x_coords = [point[0] for point in self.formatted_point_data]
        y_coords = [point[1] for point in self.formatted_point_data]
        colors = ['green' if not point[2] else 'red' for point in self.formatted_point_data]  # Green for active, red for blanked
        plt.figure(figsize=(10, 10))
        plt.scatter(x_coords, y_coords, c=colors)
        plt.title('Formatted ILDA Points')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.grid(True)
        plt.show()
        '''
        return self.formatted_point_data




    def create_binary(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        file_path = os.path.join(self.output_dir, 'target.bin')

        with open(file_path, 'wb') as file:
            for point in self.formatted_point_data:
                data = struct.pack('HHBxxx', int(point[0]) % 65536, int(point[1]) % 65536, point[2]) #Padding added for alignment with STM32's 32-bit memory bus, padding bytes implicitly set to 00000000
                file.write(data)
            return file_path



    def signed_to_abs(self, angle):
        if angle >= 0:
            return angle
        else:
            return self.angular_resolution + angle
        


    @staticmethod
    def to_16bit_unsigned(value):
        return int(value) & 0xFFFF