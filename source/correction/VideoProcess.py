import cv2
import numpy as np

import ImageProccess
import sys


def video_encode(cap, type=0):
    encode_video = []
    while True:  # 循环处理每一帧
        ret, frame = cap.read()
        encode_image2DNA = ImageProccess.image_encode(frame, type)  # 返回值是一个一维数组，每个元素是一个DNA字符串
        encode_video.append(encode_image2DNA)
        if not ret:
            break
    return np.array(encode_video)


def video_decode(deleted_DNA):
    estimate_frame = []
    for i in range(len(deleted_DNA)):
        estimate_image, flag = ImageProccess.image_decode(deleted_DNA[i], type)
        if i != 0 and flag == False:  #
            estimate_frame.append(estimate_frame[i - 1])
        else:
            estimate_frame.append(estimate_image)
    return np.array(estimate_frame)


def VideoProcess(filepath, type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()
    encode_video2DNA = video_encode(cap, type)
    # flatten
    # 通过删除信道
    # 译码

    # imshow显示每一帧
