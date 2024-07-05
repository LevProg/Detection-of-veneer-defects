import cv2

cap = cv2.VideoCapture("rtsp://admin:SVEZA14!ST@10.12.37.234:554/media/video1")

while(cap.isOpened()):
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()