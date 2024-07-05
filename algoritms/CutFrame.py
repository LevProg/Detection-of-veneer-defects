import cv2
import numpy as np
import colorspacious
from PIL import Image
import os
import time
from functools import reduce

j=0

NumberOfPhotos = []

def delta_e_lab(color1, color2):
    lab_color1 = colorspacious.cspace_convert(color1, "sRGB1", "CAM02-UCS")
    lab_color2 = colorspacious.cspace_convert(color2, "sRGB1", "CAM02-UCS")
    return colorspacious.deltaE(lab_color1, lab_color2)


def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w / 2, h / 2)

    # Получение матрицы поворота
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Вычисление новых размеров изображения после поворота
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Настройка матрицы поворота для учета смещения центра
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # Поворот изображения
    rotated = cv2.warpAffine(image, M, (new_w, new_h))
    return rotated
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
    image1 = image1[block_y:height1-b_coef-500, 0:width1-block_x]
    image2 = image2[block_y+b_coef:height1-500, 0:width1-block_x-300]
    combined_image = cv2.hconcat([image1, image2])
    combined_image = rotate_image(combined_image, -3.5)
    combined_image = combined_image[230:450]
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

def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    global j
    count = 0
    start_time_out_shpon = 0
    start_time_in_shpon = 0
    flag = True
    time_out_shpon = 0
    skip = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if skip > 0:
            skip -= 1
        if skip<=0:
            isStarted = detect(frame, target_color, coords) < 0.1
            isEnded = detect(frame, target_color, coords2) > 0.1
            if (isStarted and not isEnded and len(Images) == 0):
                end_time_out_shpon = time.time()
                time_out_shpon = end_time_out_shpon - start_time_out_shpon
                start_time_in_shpon = time.time()
                Images.append(frame)
            elif (isEnded):
                end_time_in_shpon = time.time()
                start_time_out_shpon = time.time()
                if ((end_time_in_shpon - start_time_in_shpon) < 0.6 and time_out_shpon < 0.25):
                    skip = int((0.7 - end_time_in_shpon + start_time_in_shpon) * 60)
                    Images.clear()
                if Images:
                    merge_images(Images[0], frame)
                    Images.clear()
        count += 1
    cap.release()

video_path = "D:/tg_download/20240404123810_part16.ts"
output_path = "D:/test"

extract_frames(video_path)
