import cv2
import numpy as np
import colorspacious


leftPoints=[(21, y) for y in range(750, 1401, 150)]
rightPoints=[(2000, y) for y in range(600, 1401, 200)]
target_color = [173, 234, 242]#in brg

def delta_e_lab(color1, color2):
    lab_color1 = colorspacious.cspace_convert(color1, "sRGB1", "CAM02-UCS")
    lab_color2 = colorspacious.cspace_convert(color2, "sRGB1", "CAM02-UCS")
    return colorspacious.deltaE(lab_color1, lab_color2)

def detect(image, reference_color, points):
    average_delta_e = 0
    for point in points:
        reg=image[point[1]][point[0]]
        delta_e = delta_e_lab(reference_color, reg)
        average_delta_e += delta_e
    average_delta_e /= 5
    #print("Среднее значение Delta E на выбранных точек:", average_delta_e, reference_color, reg)
    return average_delta_e

def paintPoints(frame, size):
    for points in leftPoints,rightPoints:
        for point in points:
            for j in range(point[0]-size, point[0]+size):
                for i in range(point[1]-size, point[1]+size):
                    frame[i][j]=[255,0,0]

def extract_frames(video_path, interval):
    cap = cv2.VideoCapture(video_path)  
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()   
        if count % interval == 0:
            isStarted=detect(frame, target_color, leftPoints)
            isEnded=detect(frame, target_color, rightPoints)
            print(isStarted, isEnded)
            if (detect(frame, target_color, rightPoints)):#Условие по *E, обычно <1
                paintPoints(frame, 10)
                frame = cv2.resize(frame, (0,0), fx=0.4, fy=0.4) 
                cv2.imshow("Image", frame)
                cv2.waitKey(0)
        if count==100:
            break
        count += 1

    cap.release()

video_path = "C:/Users/Aser/Desktop/Pro/vid.ts"
output_path = ""
extract_frames(video_path, interval=1)
