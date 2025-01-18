import io
import multiprocessing
import queue
import threading

import redis
import time
import cv2
import numpy as np
import colorspacious
import torch
from PIL import Image
import os
import time
from functools import reduce
from io import BytesIO
import psycopg2
from datetime import datetime

from torchvision.transforms import transforms

j=0



coords = [(21, y) for y in range(750, 1401, 150)]
coords2 = [(2000, y) for y in range(600, 1401, 200)]
target_color = [18, 171, 163]
Images=[]

conn = psycopg2.connect(
    dbname="shpon2",
    user="postgres",
    password="1234",
    host="localhost",  # или IP-адрес сервера
    port="5432"
)
NumberOfPhotos = []
output_path = "C:/Users/Aser/Desktop/Pro/photo/"


r = redis.Redis(host='localhost', port=6379, db=0)

def cut_to_send(image1, image2):
    combined_image = cv2.hconcat([image1, image2])
    return combined_image

def cut_to_ai(image1, image2):
    height1, width1 = image1.shape[:2]
    height1, width1 = image2.shape[:2]
    block_y = 300  # образка по Y сверху
    block_x = 130  # образка по X справа
    b_coef = 120  # смещение в высоте image1 и image2(из-за наклона)
    image1 = image1[block_y:height1 - b_coef - 500, 0:width1 - block_x]
    image2 = image2[block_y + b_coef:height1 - 500, 0:width1 - block_x - 300]
    combined_image = cv2.hconcat([image1, image2])
    combined_image = rotate_image(combined_image, -3.5)
    combined_image = combined_image[230:450]
    return combined_image

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

def merge_images(image1, image2, images_to_ai, image_to_send, image_to_save):
    global j
    # Проверка на успешную загрузку изображений
    if image1 is None or image2 is None:
        print("Ошибка: Переданные изображения некорректны.")
        return
    send_image = cut_to_send(image1, image2)
    ai_image = cut_to_ai(image1, image2)
    #output__path = output_path + f"/image" + str(j) + ".png"
    #cv2.imwrite(output__path, combined_image)
    images_to_ai.put(ai_image)
    image_to_send.put(send_image)
    image_to_save.put(send_image)

def detect(image, reference_color, coord):
    average_delta_e = 0
    for coor in coord:
        reg = image[coor[1]][coor[0]]
        delta_e = delta_e_lab(reference_color, reg)
        average_delta_e += delta_e
    average_delta_e /= 5
    return average_delta_e

def extract_frames(video_path, images):
    cap = cv2.VideoCapture(video_path)
    count = 0
    start_time_out_shpon = 0
    start_time_in_shpon = 0
    time_out_shpon = 0
    skip = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
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
                #while images.qsize() == 2:
                #    print("eror, задержка")
            elif (isEnded):
                end_time_in_shpon = time.time()
                start_time_out_shpon = time.time()
                if ((end_time_in_shpon - start_time_in_shpon) < 0.6 and time_out_shpon < 0.25):
                    skip = int((0.7 - end_time_in_shpon + start_time_in_shpon) * 60)
                    Images.clear()
                if Images:
                    images.put((Images[0], frame))
                    Images.clear()

        count += 1
    cap.release()

def predict(classDict, image, model, valid_transform):
    image = valid_transform(image)
    image = image.cuda()
    pred = model(image[None, ...])
    pred_class = pred.argmax().item()
    if abs(pred[0][0]) < 1:
        res = classDict[2]
    res = classDict[pred_class]
    return res


def save_and_write_in_db(path, image, result, id, conn):
    # Сохранение изображения (если требуется)
    cv2.imwrite(path, image)

    # Получение текущего времени
    time = datetime.now()

    # Создание курсора для выполнения SQL-запросов
    cursor = conn.cursor()

    # Вставка данных в таблицу
    cursor.execute(
        "INSERT INTO shpon (defect, date_time, path) VALUES (%s, %s, %s)",
        (result, time, path)
    )
    # Фиксация изменений в базе данных
    try:
        conn.commit()
        print("written")
    except:
        print("bd bad")
    # Закрытие курсора
    cursor.close()

def send_to_redis(id, result):
    r.rpush('shon_id', id)
    r.rpush('shon_result', str(result))

def ai_part(images_to_ai, results_to_send, results_to_save):
    try:
        # Load model on CPU with map_location argument
        model = torch.load("C:/Users/Aser/Desktop/Pro/98.4(yellow).pt")  # Загружаем
        print("Model loaded successfully.")
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
    except MemoryError:
        print("MemoryError: Not enough memory to load the model.")
    classDict = {0: True,
                 1: False,
                 2: 'Не получилось определить'
                 }
    valid_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    model = model.cuda()
    model.eval()
    while True:
        if not images_to_ai.empty():
            res = predict(classDict, images_to_ai.get(), model, valid_transform)
            results_to_send.put(res)
            results_to_save.put(res)

def test_part(images_to_ai, results_to_send, results_to_save):
    while True:
        if not images_to_ai.empty():
            images_to_ai.get()
            print("test")
            results_to_send.put(1)
            results_to_save.put(True)
            print(results_to_save.empty())

def extract_frames_part(images):

    extract_frames("C:/Users/Aser/Downloads/Telegram Desktop/20240404123810_part115.ts", images)

def merge_images_part(images, images_to_ai, image_to_send, image_to_save, id, id_to_send,id_to_save):
    while True:
        if not images.empty():
            cur_image = images.get()
            id = int(id)
            id += 1
            id_to_send.put(id)
            id_to_save.put(id)
            merge_images(cur_image[0], cur_image[1], images_to_ai, image_to_send, image_to_save)

def send_to_web_image_part(image_to_send, results_to_send,id_to_send):
    while True:
        if not image_to_send.empty():
            message = image_to_send.get()
            image_rgb = cv2.cvtColor(message, cv2.COLOR_BGR2RGB)

            # Convert the image to bytes
            pil_image = Image.fromarray(image_rgb)
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')  # You can use other formats like 'JPEG'
            img = img_byte_arr.getvalue()
            #image_stream = io.BytesIO(img)
            #image = Image.open(image_stream)

            while r.llen('shpon_queue') >= 5:
                r.lpop('shpon_queue')
            r.rpush('shpon_queue', img)
        if not results_to_send.empty():
            r.rpush('result', str(results_to_send.get()))
        if not id_to_send.empty():
            r.rpush('id',id_to_send.get() )

def save_data_part(image_to_save, results_to_save, id_to_save):
    while True:
        if not image_to_save.empty() and not results_to_save.empty():
            id = id_to_save.get()
            img = image_to_save.get()
            res = results_to_save.get()
            send_to_redis(id,str(res))
            path = f"C:/Users/Aser/Desktop/Pro/photo/image{id}.png"
            save_and_write_in_db(path, img, res, id, conn)

def get_cur_id():
    conn = psycopg2.connect(
        dbname="shpon2",
        user="postgres",
        password="1234",
        host="localhost",  # или IP-адрес сервера
        port="5432"  # стандартный порт PostgreSQL
    )
    cursor = conn.cursor()
    try:
        # Запрос для получения значения последней записи
        query = f"SELECT shpon FROM Shpon ORDER BY shpon_id DESC LIMIT 1"
        cursor.execute(query)

        # Извлечение значения
        last_record = cursor.fetchone()
        if last_record:
            return last_record[0].strip('()').split(',')[-1]
        else:
            return None
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        cursor.close()


if __name__ == "__main__":
    id = get_cur_id()
    images = multiprocessing.Queue()
    images_to_ai = multiprocessing.Queue()
    image_to_send = multiprocessing.Queue()
    results_to_send = multiprocessing.Queue()
    image_to_save = multiprocessing.Queue()
    results_to_save = multiprocessing.Queue()
    id_to_send = multiprocessing.Queue()
    id_to_save = multiprocessing.Queue()

    p1 = multiprocessing.Process(target=extract_frames_part, args = (images,))
    p2 = multiprocessing.Process(target=merge_images_part, args = (images, images_to_ai, image_to_send, image_to_save, id, id_to_send, id_to_save,))
    p3 = multiprocessing.Process(target=ai_part, args = (images_to_ai, results_to_send, results_to_save,))
    p4 = multiprocessing.Process(target=send_to_web_image_part, args=(image_to_send, results_to_send, id_to_send,))
    p5 = multiprocessing.Process(target=save_data_part, args= (image_to_save, results_to_save, id_to_save,))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
