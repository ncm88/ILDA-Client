import struct
from typing import List, Tuple, Optional, Dict
import os


# Example usage:
# ilda_handler = ILDA_Handler('path_to_your_ilda_file.ild')
# header_info = ilda_handler.read_ilda_header()
# if header_info:
#     print(header_info)
# point_data = ilda_handler.extract_point_data()
# for point in point_data:
#     print(point)
# ilda_handler.create_binary()

class ILDA_Handler:
    
    def __init__(self, ilda_filename: str):
        self.ilda_filename = ilda_filename
        self.header_info: Optional[Dict[str, any]] = None
        self.point_data: List[Tuple[int, int, bool]] = []


    def read_ilda_header(self):
        with open(self.ilda_filename, 'rb') as file:
            header_format = '>4s3xB8s8sHHHBB'
            header_size = struct.calcsize(header_format)
            header_data = file.read(header_size)

            if len(header_data) < header_size:
                return None  # End of file or incomplete header

            header = struct.unpack(header_format, header_data)
            signature, format_type, name_bytes, company_name_bytes, num_points, frame_number, total_frames, scanner_head = header[:8]

            if signature != b'ILDA':
                raise ValueError("File does not start with ILDA signature")

            name = name_bytes.decode('ascii', 'ignore').rstrip('\x00').strip()
            company_name = company_name_bytes.decode('ascii', 'ignore').rstrip('\x00').strip()

            self.header_info = {
                'signature': signature.decode('ascii'),
                'format_type': format_type,
                'name': name,
                'company_name': company_name,
                'num_points': num_points,
                'frame_number': frame_number,
                'total_frames': total_frames,
                'scanner_head': scanner_head,
            }
            return self.header_info


    def extract_point_data(self):
        if self.header_info is None:
            raise ValueError("Header info is not yet read or file is invalid")

        with open(self.ilda_filename, 'rb') as file:
            # Skip the header
            file.seek(struct.calcsize('>4s3xB8s8sHHHBB'))

            points = []
            format_type = self.header_info['format_type']
            num_points = self.header_info['num_points']

            if format_type in [0, 1]:
                point_format = '>hhB'
            else:
                raise ValueError("Unsupported format type for point data")

            point_size = struct.calcsize(point_format)

            for _ in range(num_points):
                point_data = file.read(point_size)
                if len(point_data) < point_size:
                    raise ValueError("Incomplete point data")

                x, y, status_code = struct.unpack(point_format, point_data)
                blanking = (status_code & 0x80) != 0
                points.append((x, y, blanking))

            self.point_data = points
            return self.point_data


    def create_binary(self, output_dir='../output'):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(os.path.join(output_dir, 'ilda.bin'), 'wb') as file:
            for x, y, blank in self.point_data:
                x = self.to_16bit_signed(x)
                y = self.to_16bit_signed(y)
                blank_int = int(blank)
                
                data = struct.pack('<hhBxxx', x, y, blank_int)
                file.write(data)


    @staticmethod
    def to_16bit_signed(value):
        return value & 0xFFFF if value >= 0 else -(0x10000 - (value & 0xFFFF))





'''
def test():
    def read_binary(filename: str) -> List[Tuple[int, int, bool]]:
        points = []
        # The format used for each point in the binary file
        point_format = '<hhBxxx'  # Little endian, 2x 16-bit int, 1x 8-bit int, 3 bytes padding
        point_size = struct.calcsize(point_format)

        with open(filename, 'rb') as file:
            while True:
                data = file.read(point_size)
                if not data:
                    break  # End of file
                
                x, y, blank_int = struct.unpack(point_format, data)
                blank = bool(blank_int)
                points.append((x, y, blank))

        return points
    
    fileIn = '../datafiles/ildatstb.ild'
    handler = ILDA_Handler(fileIn)


    header_info = handler.read_ilda_header()
    if header_info:
        for key, value in header_info.items():
            print(f"{key}: {value}")
    else:
        print("Failed to read ILDA header or end of file reached.")

    out = handler.extract_point_data()
    handler.create_binary()
    test = read_binary("../output/ilda.bin")
    
    ret = (out == test)

    print(ret)
    return ret


test()
'''