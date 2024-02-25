import struct
from typing import List, Tuple 
import numpy as np
from math import asin

def read_ilda_header(file):
    # ILDA header format according to the provided structure
    # Signature (4 bytes), Not used (3 bytes), Format type (1 byte), Name (8 bytes),
    # Company name (8 bytes), Total number of entries (2 bytes), Current frame number (2 bytes),
    # Total number of frames (2 bytes), Scanner head (1 byte), Not used (1 byte)
    header_format = '>4s3xB8s8sHHHBB'
    header_size = struct.calcsize(header_format)
    header_data = file.read(header_size)

    if len(header_data) < header_size:
        return None  # End of file or incomplete header

    header = struct.unpack(header_format, header_data)
    signature, format_type, name_bytes, company_name_bytes, num_points, frame_number, total_frames, scanner_head = header[:8]

    # Ensure the signature matches "ILDA"
    if signature != b'ILDA':
        raise ValueError("File does not start with ILDA signature")

    # Decode and clean up the name and company name fields
    name = name_bytes.decode('ascii', 'ignore').rstrip('\x00').strip()
    company_name = company_name_bytes.decode('ascii', 'ignore').rstrip('\x00').strip()

    return {
        'signature': signature.decode('ascii'),
        'format_type': format_type,
        'name': name,
        'company_name': company_name,
        'num_points': num_points,
        'frame_number': frame_number,
        'total_frames': total_frames,
        'scanner_head': scanner_head,
    } 


def extract_point_data(file, num_points, format_type):
    points = []

    # Define the point data format
    # We ignore Z for 3D and color index for both 2D and 3D.
    if format_type in [0, 1]:  # For both 3D (ignoring Z) and 2D coordinate sections
        point_format = '>hhB'  # X, Y, status code
    else:
        raise ValueError("Unsupported format type for point data")

    point_size = struct.calcsize(point_format)

    for _ in range(num_points):
        point_data = file.read(point_size)
        if len(point_data) < point_size:
            raise ValueError("Incomplete point data")

        point = struct.unpack(point_format, point_data)
        x, y, status_code = point
        blanking = (status_code & 0x80) != 0  # Extract blanking bit, Value of 1 indicates
        points.append((x, y, blanking))

    return points


def create_binary(pointData: List[Tuple[int, int, bool]])->None:

    return











fileIn = '../datafiles/ildatstb.ild'
fin = open(fileIn, 'rb')

header_info = read_ilda_header(fin)
if header_info:
    for key, value in header_info.items():
        print(f"{key}: {value}")
else:
    print("Failed to read ILDA header or end of file reached.")

out = extract_point_data(fin, header_info["num_points"], header_info["format_type"])
for point in out:
    print(point)






















"""

def process_point_data(file, is_3d, num_points, output_file):
    point_format_3d = '>hhhbB'
    point_format_2d = '>hhbB'
    point_size = struct.calcsize(point_format_3d if is_3d else point_format_2d)
    
    for _ in range(num_points):
        point_data = file.read(point_size)
        if is_3d:
            x, y, _, status_code, _ = struct.unpack(point_format_3d, point_data)
        else:
            x, y, status_code, _ = struct.unpack(point_format_2d, point_data)
        
        blank_bit = status_code & 0x01
        output_file.write(struct.pack('>hhB', x, y, blank_bit))

def process_ilda_file(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as ilda_file, open(output_file_path, 'wb') as output_file:
        while True:
            frame_header = read_frame_header(ilda_file)
            if frame_header is None:
                break  # End of file
            
            process_point_data(ilda_file, frame_header['is_3d'], frame_header['num_points'], output_file)

if __name__ == "__main__":
    input_file_path = 'input.ild'  # Update this to the path of your ILDA file
    output_file_path = 'output.bin'  # The path where you want to save the new binary file
    process_ilda_file(input_file_path, output_file_path)

"""


