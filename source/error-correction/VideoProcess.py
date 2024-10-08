import cv2


def VideoProcess(filepath):
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()
    while True:  # 循环处理每一帧
        ret, frame = cap.read()
        if not ret:
            break
        
