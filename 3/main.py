import cv2
import numpy as np
import serial
import math

ser = serial.Serial("COM3", 115200)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)

detector_params = cv2.aruco.DetectorParameters()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
detector = cv2.aruco.ArucoDetector(dictionary, detector_params)

target_dir = [0, 1]

D_W = 1010
D_H = 905

def listify_array(a, printtype=False):
    if printtype:
        print(type(a))
    if type(a) in [np.array, tuple, np.ndarray]:
        return [ listify_array(i, printtype) for i in list(a) ]
    elif type(a) in [np.float16, np.float32]:
        return float(a)
    elif type(a) in [np.int8, np.int16, np.int32, np.intc]:
        return int(a)
    else:
        return a

def pretty_coord(a):
    return (int(a[0]), int(a[1]))

def aruco_center(c):
    return pretty_coord([ (c[0][0] + c[2][0]) / 2, (c[0][1] + c[2][1]) / 2 ])

def check_for_keys(d, k):
    for i in k:
        if i not in d.keys():
            return False
    return True

def draw_vec(frame, start, vec, mul, color):
    cv2.line(frame, pretty_coord(start), (int(start[0] + vec[0] * mul), int(start[1] + vec[1] * mul)), color, 1)

def get_norm_dot(v1, v2):
    return math.acos(v1[0]*v2[0]+v1[1]*v2[1])

def send_cmd(m1_, m2_, servo_):
    m1 = int(max(min(m1_, 255), -255))
    m2 = int(max(min(m2_, 255), -255))
    servo = int(90 - max(min(servo_, 60), -60))
    ser.write(f"{m1},{m2},{servo};".encode())

I = []

while True:
    k = cv2.waitKey(1) & 0xFF
    if k == 27: 
        break
    
    # READ FRAME
    ret, frame = cap.read()

    # FIND ARUCO
    corners, ids, _ = detector.detectMarkers(frame)

    c_dict = {}

    for i in range(len(corners)):
        c_dict[int(ids[i][0])] = corners[i][0]

    # DETECT EVERYTHING
    if not check_for_keys(c_dict, [1,2,3,4,5]):
        print("C_DICT FAILED")
        continue
    
    p_tl = pretty_coord(c_dict[1][0])
    p_tr = pretty_coord(c_dict[2][1])
    p_br = pretty_coord(c_dict[4][2])
    p_bl = pretty_coord(c_dict[3][3])

    pts1 = np.float32([p_tl, p_tr,
                       p_bl, p_br])
    pts2 = np.float32([[0, 0], [D_W, 0],
                       [0, D_H], [D_W, D_H]])
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    frame1 = cv2.warpPerspective(frame, matrix, (D_W, D_H))

    cv2.imshow('P_FIXED', frame1)

    # FIX PERSP FOR EVERYTHING ELSE
    corners2 = list(corners)
    for i in range(len(corners)):
        corners2[i] = cv2.perspectiveTransform(corners[i], matrix, (D_W, D_H))

    c_dict2 = {}
    for i in range(len(corners2)):
        c_dict2[int(ids[i][0])] = corners2[i][0]

    frame_result = np.zeros([D_H, D_W, 3])

    cv2.aruco.drawDetectedMarkers(frame_result, corners2, ids)
    
    car_aruco = c_dict2[5]
    car_coords = aruco_center(car_aruco)

    # get car direction
    car_dir_vec1 = [ car_aruco[0][0] - car_aruco[3][0], car_aruco[0][1] - car_aruco[3][1] ]
    car_dir_vec2 = [ car_aruco[1][0] - car_aruco[2][0], car_aruco[1][1] - car_aruco[2][1] ]
    car_dir_vec = [car_dir_vec1[0] + car_dir_vec2[0], car_dir_vec1[1] + car_dir_vec2[1]]
    car_dir_vec_dist = math.sqrt(car_dir_vec[0] ** 2 + car_dir_vec[1] ** 2)
    car_dir = [ car_dir_vec[0] / car_dir_vec_dist, car_dir_vec[1] / car_dir_vec_dist ]

    angdiff1 = get_norm_dot(car_dir, [1,0])
    angdiff2 = get_norm_dot(target_dir, [1,0])
    angdiff = angdiff1 - angdiff2

    draw_vec(frame_result, car_coords, car_dir, 50, (0,0,255))
    draw_vec(frame_result, car_coords, target_dir, 50, (255,0,255))

    cv2.circle(frame_result, car_coords, 2, (0,0,255), 2)
    cv2.putText(frame_result, "nrf24car1", car_coords, cv2.FONT_HERSHEY_DUPLEX, .7, (255,255,255), 1)

    cv2.imshow('RESULT', frame_result)

    k = cv2.waitKey(1) & 0xFF
    if k == 27: 
        break

    # COMPOSE CMD
    angdiff2 = get_norm_dot(car_dir, target_dir) * abs(angdiff)/angdiff
    ERR = angdiff2
    CON_SIG = ERR * .3 + max(min(sum(I), 1), -1) * .2
    CON_SIG = max(min(CON_SIG, .5), -.5)
    send_cmd(255 * -CON_SIG, 255 * CON_SIG, 60*CON_SIG * -1.5)
    I.append(ERR)
    if len(I) > 5:
        I.pop(0)
