import serial
import threading

class nrf24car1:
    m1:int = 0
    m2:int = 0
    servo = 90

    def __init__(self, com_port):
        self.ser = serial.Serial(com_port, 115200)

    def loop(self):
        while True:
            self.send_report(self.m1, self.m2, self.servo)

    def init_loop(self):
        threading.Thread(target=self.loop).start()
    
    def set_data(self, m1_, m2_, servo_):
        self.m1 = m1_
        self.m2 = m2_
        self.servo = servo_

    def send_report(self, m1_, m2_, servo_):
        self.ser.write(f"{m1_},{m2_},{servo_};".encode())