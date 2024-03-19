import cv2
import numpy as np
import time

target_color = [180,150,80]

def detect_color(image , points, threshold=100):
    point_size=10
    min_val=240
    max_val=256
    sum=0
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Пороговая обработка для поиска белого цвета
    _, mask = cv2.threshold(gray_image, min_val, max_val, cv2.THRESH_BINARY)
    for p in points:
        if (gray_image[p[1]][p[0]] in range(min_val, max_val)):
            sum+=1
        for j in range(p[0]-point_size, p[0]+point_size):
            for i in range(p[1]-point_size, p[1]+point_size):
                image[i][j]=[255,0,0]
    fl = sum>=4
    # Применение маски к исходному изображению
    result = cv2.bitwise_and(image, image, mask=mask)
    """"
    lower_bound = np.array([250, 250, 250])
    upper_bound = np.array([256, 255, 255])
    #mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    """

    return mask, image,fl 

def extract_frames(video_path,output_path, num):
    size_x=1440
    points=[(600,y) for y in range(int(size_x/6), size_x-1, int(size_x/6))]
    cap = cv2.VideoCapture(video_path)  
    count = 0
    num=0
    fl1=0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if True:
            if count>0: 
                count-=1
                continue
            if fl1 and count==0:
                fl1=0
                print(output_path+str(num)+'.jpeg')
                cv2.imwrite(output_path+str(num)+'.jpeg', frame)
            #start = time.time()
            mask, im, fl = detect_color(frame, points,30)
            #finish = time.time()
            #print(finish-start)
            #break
            if fl:
                fl1=1
                count+=15
                num+=1
            cv2.waitKey(0)
            #break

    cap.release()

video_path = "c:/Users/Aser/Documents/GitHub/Detection-of-veneer-defects/1.ts"
output_path = "c:/Users/Aser/Documents/GitHub/Detection-of-veneer-defects/save/"
extract_frames(video_path,output_path, 0)

#input_image = cv2.imread("example_image.jpg")

# Целевой цвет (в формате BGR)

# Определение пикселей близких к целевому цвету
#color_mask = detect_color(input_image, target_color)

# Отображение исходного изображения и маски
#cv2.imshow("Original Image", input_image)
#cv2.imshow("Color Mask", color_mask)
#cv2.waitKey(0)
#cv2.destroyAllWindows()