import cv2
import numpy as np
import serial
import nrf24car1

car = nrf24car1.nrf24car1("COM3")

car.init_loop()

X = 0
Y = 0

W = 400
H = 400

def ui_event(event, x, y, flags, params):
    global X, Y
    X = (x - (W / 2)) / (W / 2)
    Y = -(y - (H / 2)) / (H / 2)

canvas = np.zeros([W, H, 3])

while True:
    m1 = int(max(min(Y + X, 1), -1) * 255)
    m2 = int(max(min(Y - X, 1), -1) * 255)
    servo = int(90 - X * 60)
    print(X, Y, m1, m2, servo)
    car.set_data(m1,m2,servo)
    cv2.imshow('car', canvas)
    cv2.setMouseCallback('car', ui_event)
    k = cv2.waitKey(1) & 0xFF
    if k == 27: 
        break
