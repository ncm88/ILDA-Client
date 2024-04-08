#include <iostream>
#include <fstream>
#include <chrono>
#include <thread>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>
#include <cstring>

#include "UART_Sender.h"
#include <pybind11/pybind11.h>


#define WRITE_BUFFER_SIZE 8
#define READ_BUFFER_SIZE 4

namespace py = pybind11;

PYBIND11_MODULE(uart_sender_module, m){
    py::class_<UART_Sender>(m, "UART_Sender")
        .def(py::init<const std::string &, int>())
        .def("openConnection", &UART_Sender::openConnection)
        .def("streamILDA", &UART_Sender::streamILDA)
        .def("closeConnection", &UART_Sender::closeConnection)
        .def("getCurrX", &UART_Sender::getCurrX)
        .def("getCurrY", &UART_Sender::getCurrY)
        .def("getTargX", &UART_Sender::getTargX)
        .def("getTargY", &UART_Sender::getTargY);
}


void UART_Sender::openConnection() {
    serial_port = open(uart_port.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);

    if (serial_port < 0) {
        std::cerr << "Error " << errno << " opening " << uart_port << ": " << strerror(errno) << std::endl;
        return;
    }

    struct termios tty;
    memset(&tty, 0, sizeof tty);

    if (tcgetattr(serial_port, &tty) != 0) {
        std::cerr << "Error " << errno << " from tcgetattr: " << strerror(errno) << std::endl;
    }

    tty.c_cflag &= ~PARENB; // Clear parity bit, disabling parity (most common)
    tty.c_cflag &= ~CSTOPB; // Clear stop field, ensure only one stop bit is used in communication (most common)
    tty.c_cflag |= CS8; // 8 bits per byte (most common)
    tty.c_cflag |= CRTSCTS; // Enable RTS/CTS hardware flow control (most common)
    tty.c_cflag |= CREAD | CLOCAL; // Turn on READ & ignore ctrl lines (CLOCAL = 1)

    tty.c_lflag &= ~ICANON;
    tty.c_lflag &= ~ECHO; // Disable echo
    tty.c_lflag &= ~ECHOE; // Disable erasure
    tty.c_lflag &= ~ECHONL; // Disable new-line echo
    tty.c_lflag &= ~ISIG; // Disable interpretation of INTR, QUIT and SUSP
    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // Turn off s/w flow ctrl
    tty.c_iflag &= ~(IGNBRK|BRKINT|ISTRIP|INPCK|ICRNL);

    tty.c_oflag &= ~OPOST; // Prevent special interpretation of output bytes (e.g. newline chars)
    tty.c_oflag &= ~ONLCR; // Prevent conversion of newline to carriage return/line feed

    // Set timeouts
    tty.c_cc[VTIME] = 1;    
    tty.c_cc[VMIN] = 0;

    cfsetispeed(&tty, baud);
    cfsetospeed(&tty, baud);

    // Save tty settings, also checking for error
    if (tcsetattr(serial_port, TCSANOW, &tty) != 0) {
        std::cerr << "Error " << errno << " from tcsetattr: " << strerror(errno) << std::endl;
    }
}



void UART_Sender::streamILDA(const std::string& file_path, int points_per_sec) {
    std::ifstream file(file_path, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << file_path << std::endl;
        return;
    }

    while (file) {
        uint16_t x, y, pointNum;
        uint8_t laser, visited;

        // Reading data in the same format as it was packed in Python
        file.read(reinterpret_cast<char*>(&x), sizeof(x));
        file.read(reinterpret_cast<char*>(&y), sizeof(y));
        file.read(reinterpret_cast<char*>(&laser), sizeof(laser));
        file.read(reinterpret_cast<char*>(&visited), sizeof(visited));
        file.read(reinterpret_cast<char*>(&pointNum), sizeof(pointNum));

        // Loop to back to start of image if end reached
        if (file.eof()) {
            file.clear(); 
            file.seekg(0, std::ios::beg); 
            continue;
        }

        // Prepare the buffer (assuming you want to send it in the same format)
        unsigned char wBuff[WRITE_BUFFER_SIZE];
        unsigned char rBuff[READ_BUFFER_SIZE];

        memcpy(wBuff, &x, sizeof(x));
        memcpy(wBuff + 2, &y, sizeof(y));
        memcpy(wBuff + 4, &laser, sizeof(laser));
        memcpy(wBuff + 5, &visited, sizeof(visited));
        memcpy(wBuff + 6, &pointNum, sizeof(pointNum));

        // Write to the serial port
        if (write(serial_port, wBuff, sizeof(wBuff)) == -1) {
            std::cerr << "Failed to write to the serial port: " << strerror(errno) << std::endl;
            break;
        }

        if(read(serial_port, rBuff, sizeof(rBuff)) > 0 ){
            this->curr->x = rBuff[0] | (rBuff[1] << 8);
            this->curr->y = rBuff[2] | (rBuff[3] << 8); 
        }

        // Delay based on the points per second requirement
        std::this_thread::sleep_for(std::chrono::milliseconds(1000 / points_per_sec));
    }

    file.close();
}



void UART_Sender::closeConnection() {
    close(serial_port);
}


uint16_t UART_Sender::getCurrX() { return curr->x; }
uint16_t UART_Sender::getCurrY() { return curr->y; }
uint16_t UART_Sender::getTargX() { return targ->x; }
uint16_t UART_Sender::getTargY() { return targ->y; }