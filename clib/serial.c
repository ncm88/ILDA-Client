#include "serial.h"

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <stdint.h>

#define PORT "/dev/ttyUSB0" //change this as needed
#define FSOURCE "../../output/ilda.bin"
#define BAUD 38400

int init_serial(char* port) {
    struct termios port_settings;

    // Set serial port settings
    bzero(&port_settings, sizeof(port_settings));
    port_settings.c_cflag = CS8 | CLOCAL | CREAD; // 8n1
    port_settings.c_iflag = 0; // raw input mode 
    port_settings.c_oflag = 0; // raw output mode
    port_settings.c_lflag = 0;
    port_settings.c_cc[VMIN]=1;
    port_settings.c_cc[VTIME]=5;

    int fd_serial = open(port, O_RDWR | O_NOCTTY);
    if (fd_serial < 0) return ERR_COULD_NOT_OPEN_PORT; 

    cfsetospeed(&port_settings, BAUD);
    cfsetispeed(&port_settings, BAUD);
    tcflush(fd_serial, TCIFLUSH);
    tcsetattr(fd_serial, TCSANOW, &port_settings);

    return SUCCESS; //success; port open!
}


int serial_fstream(int fd_serial) {
    
    FILE* fp = fopen(FSOURCE, "r");
    if (fp == NULL) return ERR_INVALID_FILE;

    char buffer[CHUNK_SIZE]; // Buffer to hold file data
    size_t bytes_read;

    //Check that point file bytelength is a multiple of 8 (1 point = 8 bytes)
    fseek(fp, 0, SEEK_END); 
    long fileSize = ftell(fp); 
    fseek(fp, 0, SEEK_SET); 
    if (fileSize % CHUNK_SIZE != 0) {
        return ERR_FILE_SIZE; 
    }

    // Read the file in 8-byte chunks and write to the serial port
    while ((bytes_read = fread(buffer, 1, CHUNK_SIZE, fp)) > 0) {
        if (bytes_read < CHUNK_SIZE) {
            // If we read fewer than CHUNK_SIZE bytes, indicate an error
            return ERR_CHUNK_SIZE_MISMATCH; 
        }

        ssize_t bytes_written = write(fd_serial, buffer, bytes_read);
        if (bytes_written < 0) {
            return ERR_BAD_WRITE;
        }
    }

    if (ferror(fp)) {
        return ERR_FILE_READ;
    }

    return SUCCESS;
}