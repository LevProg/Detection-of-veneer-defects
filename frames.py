import cv2
import numpy as np


target_color = [225,187,126]

def detect_color(image, target_color, threshold=30):
    """
    Определение пикселей, близких к целевому цвету.

    Параметры:
    - image: изображение в формате BGR (OpenCV).
    - target_color: целевой цвет в формате BGR.
    - threshold: пороговое значение для определения близости к целевому цвету.

    Возвращает:
    - mask: бинарная маска, где белые пиксели соответствуют пикселям близким к целевому цвету.
    """

    try:
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    except Exception as e:
        print("Ошибка при конвертации цветового пространства:", e)
    # Преобразование изображения в формат HSV
    #hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Преобразование целевого цвета в формат HSV
    target_color_hsv = cv2.cvtColor(np.uint8([[target_color]]), cv2.COLOR_BGR2HSV)[0][0]

    # Создание диапазона цвета с учетом порогового значения
    lower_bound = np.array([target_color_hsv[0] - threshold, 50, 50])
    upper_bound = np.array([target_color_hsv[0] + threshold, 255, 255])

    # Создание маски, где белые пиксели соответствуют цветам в заданном диапазоне
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    return mask

def extract_frames(video_path, interval):
    cap = cv2.VideoCapture(video_path)  
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval == 0:
            #cv2.imshow("Image", frame)
            detect_color(frame, target_color,30)
             
            break
        count += 1

    cap.release()

video_path = "C:/Users/Aser/Desktop/Pro/2.mp4"
output_path = ""
extract_frames(video_path, interval=10)

input_image = cv2.imread("example_image.jpg")

# Целевой цвет (в формате BGR)

# Определение пикселей близких к целевому цвету
color_mask = detect_color(input_image, target_color)

# Отображение исходного изображения и маски
cv2.imshow("Original Image", input_image)
cv2.imshow("Color Mask", color_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
