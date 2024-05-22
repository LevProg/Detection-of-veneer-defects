import cv2
import numpy as np
import colorspacious
from PIL import Image
import os

j=0
def delta_e_lab(color1, color2):
    lab_color1 = colorspacious.cspace_convert(color1, "sRGB1", "CAM02-UCS")
    lab_color2 = colorspacious.cspace_convert(color2, "sRGB1", "CAM02-UCS")
    return colorspacious.deltaE(lab_color1, lab_color2)
def merge_images(image1, image2):
    global j
    # Проверка на успешную загрузку изображений
    if image1 is None or image2 is None:
        print("Ошибка: Переданные изображения некорректны.")
        return
    # Получение размеров первого изображения
    height1, width1 = image1.shape[:2]
    height1, width1 = image2.shape[:2]
    block_y=300#образка по Y сверху
    block_x=130#образка по X справа
    b_coef=120#смещение в высоте image1 и image2(из-за наклона)
    image1 = image1[block_y:height1-b_coef, 0:width1-block_x]
    image2 = image2[block_y+b_coef:height1, 0:width1-block_x]
    combined_image = cv2.hconcat([image1, image2])
    output__path = output_path + f"/image" + str(j) + ".png"
    j += 1
    cv2.imwrite(output__path, combined_image)
    print(output__path)



coords = [(21, y) for y in range(750, 1401, 150)]
coords2 = [(2000, y) for y in range(600, 1401, 200)]
target_color = [88, 255, 238]
Images=[]

def detect(image, reference_color, coord):
    average_delta_e = 0
    for coor in coord:
        reg = image[coor[1]][coor[0]]
        delta_e = delta_e_lab(reference_color, reg)
        average_delta_e += delta_e
    average_delta_e /= 5
    return average_delta_e

def extract_frames(video_path, interval):
    cap = cv2.VideoCapture(video_path)
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if count % interval == 0:
            isStarted=detect(frame, target_color, coords)<0.1
            isEnded=detect(frame, target_color, coords2)>0.1
            #print(detect(frame, target_color, coords), detect(frame, target_color, coords2), bool(Images))
            if (isStarted and not isEnded and len(Images)==0):
                Images.append(frame)
            elif(isEnded):
                if Images:
                    merge_images(Images[0], frame)
                    Images.clear()
        count += 1
    cap.release()

video_path = "D:/tg_download/20240404123810_part16.ts"
output_path = "C:/Users/burla/Pictures/2_13_16"

extract_frames(video_path, interval=1)