from correction.ImageProccess import image_decode, image_encode
from correction.VideoProcess import video_encode, video_decode
from correction.TextProcess import text_encode, text_decode
import correction.channel as channel
import correction.Config as config
import cv2
import sys
import matplotlib.pyplot as plt
import os
import time
import numpy as np


# def imageTest_Correction(image_path, type=0):
#     start_time = time.time()  # 记录开始时间
#     if type not in (0, 1):
#         print("错误的编码类型!")
#         sys.exit()
#     image = plt.imread(image_path)
#     if image is None:
#         print("照片路径不存在!")
#         sys.exit()
#     encode_DNA, _ = image_encode(image, type)
#     # 通过删除信道
#     deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
#     shape = image.shape
#     estimate_image, decode_str = image_decode(deleted_DNA, shape, type)
#     difference = cv2.absdiff(image, estimate_image)
#     save_images(image, estimate_image, difference, image_path)
#     end_time = time.time()  # 记录结束时间
#     elapsed_time = end_time - start_time  # 计算耗时
#     result_str = "图片编解码耗时：" + str(elapsed_time) + "秒\n"
#     result_str = result_str + decode_str
#     print(result_str)
#     return result_str

def imageTest_Correction(image_path, type=0):
    start_time = time.time()  # 记录开始时间
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    image_float = plt.imread(image_path)
    if image_float is None:
        print("照片路径不存在!")
        sys.exit()
    if image_float.dtype == np.float32 or image_float.dtype == np.float64:
        # 将浮点数缩放到0-255的范围，并转换为uint8
        image = (image_float * 255).astype(np.uint8)
    else:
        # 如果已经是整数，不需要转换
        image = image_float
    encode_DNA, _ = image_encode(image, type)
    # 通过删除信道
    deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
    shape = image.shape
    estimate_image, decode_str = image_decode(deleted_DNA, shape, type)
    difference = np.abs(image - estimate_image)
    save_images(image, estimate_image, difference, image_path)
    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算耗时
    result_str = "图片编解码耗时：" + str(elapsed_time) + "秒\n"
    result_str = result_str + decode_str
    print(result_str)
    return result_str



def save_images(img1, img2, img3, image_path):
    # 创建结果的绝对路径
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_correct_estimate{extension}"
    new_image_path = os.path.join(directory, new_filename)

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    axs[0].imshow(img1)
    axs[0].set_title('Input Image')
    axs[0].axis('off')
    axs[1].imshow(img2)
    axs[1].set_title('Output Image')
    axs[1].axis('off')
    axs[2].imshow(img3)
    axs[2].set_title('Difference Image')
    axs[2].axis('off')
    plt.tight_layout()
    # 保存图片到文件
    plt.savefig(new_image_path,dpi=250)
    plt.show()
    plt.close()
    print("译码后的图片路径：" + new_image_path)


def textTest_Correction(origin_text, type=0):
    start_time = time.time()  # 记录开始时间
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    encode_DNA, n = text_encode(origin_text, type)
    # 通过删除信道
    deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
    estimate_str, decode_str = text_decode(deleted_DNA, n, type)
    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算耗时
    result_str = "图片编解码耗时：" + str(elapsed_time) + "秒\n"
    result_str = result_str + decode_str
    print(result_str)
    print("译码后的文本：" + estimate_str)
    return "译码后的文本：" + estimate_str


def videoTest_Correction(video_path, type=0):
    start_time = time.time()  # 记录开始时间
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()
    encode_DNA, n, frame_shape = video_encode(cap, type)
    deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
    estimate_frames, decode_str = video_decode(deleted_DNA, n, frame_shape, type)
    # 创建结果的绝对路径
    directory = os.path.dirname(video_path)
    filename = os.path.basename(video_path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_correct_estimate{extension}"
    new_video_path = os.path.join(directory, new_filename)
    # 将帧数组转换为视频
    print("重构后帧数目:", len(estimate_frames), "开始写入视频......")
    out = cv2.VideoWriter(new_video_path, cv2.VideoWriter_fourcc(*'mp4v'), min(len(estimate_frames), 30),
                          (frame_shape[1], frame_shape[0]))
    for frame in estimate_frames:
        out.write(frame)
    out.release()
    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算耗时
    result_str = "图片编解码耗时：" + str(elapsed_time) + "秒\n"
    result_str = result_str + decode_str
    print(result_str)
    # print(len(estimate_frames))
    return result_str


def compare_specific_frames(video_path1, video_path2, frame_number):
    # 打开两个视频文件
    cap1 = cv2.VideoCapture(video_path1)
    cap2 = cv2.VideoCapture(video_path2)

    if not cap1.isOpened() or not cap2.isOpened():
        print("Error: Could not open one of the videos.")
        return

    # 设置视频文件的当前位置到指定的帧
    cap1.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
    cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # 读取两个视频的指定帧
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        print("Error: Could not read the specified frame from one of the videos.")
        return

    # 使用matplotlib显示帧
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
    plt.title('RS_video = 40')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
    plt.title('RS_video = 60')
    plt.axis('off')
    plt.show()
    # 释放视频捕获对象
    cap1.release()
    cap2.release()

# 通过可视化界面设置参数
def setPara(baseLoss,rsNumber):
    if(baseLoss!=0):
        config.BASE_LOSS_RATE = baseLoss
    if(rsNumber!=0):
        config.RS_image = rsNumber
        config.RS_text = rsNumber
        config.RS_video = rsNumber
    return f"当前获取到参数值参数值: 碱基丢失率 {baseLoss}  RS冗余数目{rsNumber} \n"


if __name__ == "__main__":
    input_str = input("请输入数据类型（0文本、1图片、2视频）：")
    try:
        integer_value = int(input_str)
    except ValueError:
        print(f"错误：'{input_str}' 不是一个有效的整数。")

    if integer_value == 0:
        origin_text = input("请输入需要编码的文本：")
        try:
            type = int(input("请输入编码类型（0二元、1q元）："))
            print(textTest_Correction(origin_text, type))
        except ValueError:
            print(f"错误：'{type}' 不是一个有效的编码类型。")

    elif integer_value == 1:
        image_path = input("请输入需要编码图片的路径：")
        try:
            type = int(input("请输入编码类型（0二元、1q元）："))
            print(imageTest_Correction(image_path, type))
        except ValueError:
            print(f"错误：'{type}' 不是一个有效的编码类型。")

    elif integer_value == 2:
        video_path = input("请输入需要编码视频的路径：")
        try:
            type = int(input("请输入编码类型（0二元、1q元）："))
            print(videoTest_Correction(video_path, type))
        except ValueError:
            print(f"错误：'{type}' 不是一个有效的编码类型。")
    else:
        print(f"错误：'{integer_value}' 不是一个有效的数据类型。")
