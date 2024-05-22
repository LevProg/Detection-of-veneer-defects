import cv2
import numpy as np
import colorspacious
import time

from PIL.Image import Image

leftPoints=[(21, y) for y in range(750, 1401, 150)]
rightPoints=[(2000, y) for y in range(600, 1401, 200)]
target_color = [88, 255, 238]  # in brg


def find_key_points(frame, leftPoints, rightPoints):
    for points in leftPoints, rightPoints:
        for point in points:
            if(delta_e_lab(frame[point[0]][point[1]], target_color)<3):
                past = point[1]
                new_point1 = point[1]
                for index in range(150):
                    if delta_e_lab(frame[point[0]][index + point[1]], target_color) < 1:
                        new_point1 = index + point[1]
                        print(new_point1)
                        break
                if past == new_point1:
                    print("warning")
                else:
                    point[1] = new_point1

            else:
                pass

def find_dominant_color(frame):
    # Преобразуем массив в одномерный массив
    pixels = frame.reshape((-1, 3))

    # Находим преобладающий цвет
    dominant_color_index = np.bincount(np.argmax(pixels, axis=1)).argmax()
    dominant_color = pixels[dominant_color_index]
    return(list(dominant_color))


def delta_e_lab(color1, color2):
    lab_color1 = colorspacious.cspace_convert(color1, "sRGB1", "CAM02-UCS")
    lab_color2 = colorspacious.cspace_convert(color2, "sRGB1", "CAM02-UCS")
    return colorspacious.deltaE(lab_color1, lab_color2)


def detect(image, reference_color, points):
    average_delta_e = 0
    for point in points:
        reg = image[point[1]][point[0]]
        delta_e = delta_e_lab(reference_color, reg)
        average_delta_e += delta_e
    average_delta_e /= 5
    return average_delta_e


def paintPoints(frame, size):
    for points in leftPoints, rightPoints:
        for point in points:
            for j in range(point[0] - size, point[0] + size):
                for i in range(point[1] - size, point[1] + size):
                    frame[i][j] = [255, 0, 0]


def extract_frames(video_path, interval):
    start = time.time()
    cap = cv2.VideoCapture(video_path)
    count = 0
    i = 0
    fl = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % interval == 0:
            #find_key_points(frame, leftPoints, rightPoints)
            delta_E = detect(frame, target_color, rightPoints)
            print("right:", delta_E)
            delta_E = detect(frame, target_color, leftPoints)
            print("left:", delta_E)
            if delta_E < 0.1 and fl == 0:  # Условие по *E, обычно <1
                i += 1
                fl = 1
            if delta_E > 1 and fl == 1:  # Условие по *E, обычно <1
                fl = 0
            paintPoints(frame, size=5)
            count+=1

            # Display the frame
            resized_frame = cv2.resize(frame, (1200, 800))

            # Display the resized frame
            cv2.imshow('Frame', resized_frame)
            while True:
                key = cv2.waitKey(0)  # Wait indefinitely for a key press
                if key == 0xFF & ord('q'):  # If 'q' is pressed, break the loop
                    break
            # Wait for 1 ms and check if 'q' is pressed to quit

        count += 1
        if count == 18000:  # 10 минута
            break
    cap.release()
    finish = time.time()
    all_time = finish - start
    print("Видос кончился, количество шпона: ", i)
    print("Время исполнения кода: ", all_time)
    print("Количество кадров: ", count)
    print("Количество кадров за секунду: ", count / all_time)
    print("Количество секунд видео за секунду работы: ", count / (30 * all_time))


video_path = "D:/tg_download/20240404123810_part14.ts"
extract_frames(video_path, interval=25)