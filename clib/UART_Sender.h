typedef struct{
    uint16_t x;
    uint16_t y;
} point;


class UART_Sender {

private:
    std::string uart_port;
    int baud;
    int serial_port;
    point* targ;
    point* curr;


public:
    UART_Sender(const std::string& uart_port, int baud)
        : uart_port(uart_port), baud(baud){};

    void openConnection();
    void streamILDA(const std::string& file_path, int points_per_sec);
    void closeConnection();
    
    uint16_t getCurrX();
    uint16_t getCurrY();
    uint16_t getTargX();
    uint16_t getTargY();

    ~UART_Sender(){
        closeConnection();
    }
};
