from correction.ImageProccess import image_decode, image_encode
from correction.VideoProcess import video_encode, video_decode
from correction.TextProcess import text_encode, text_decode
import correction.channel as channel
import correction.config as config
import cv2
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation
from PIL import Image
import numpy as np

origin_text = "DNA存储与传统的存储介质不同，DNA存储技术有如下显著优势：" \
              "1)DNA存储密度高。一个DNA分子可以保留一个物种的全部遗传信息，最大的人类染色体含有近2.5亿个碱基对，那么就意味着一条和人手差不多长的DNA链，" \
              "就可以存储1EB（1EB=10.74亿G）数据。与硬盘和闪存的数据存储密度相比，硬盘存储每立方厘米约为1013位，闪存存储约为1016位，" \
              "而DNA存储的密度约为1019位。2）DNA分子存储具有稳定性。" \
              "今年2月，国际顶级学术期刊Nature上的一篇论文称古生物学家在西伯利亚东北部的永久冻土层中提取到距今120万年猛犸象的遗传物质，" \
              "并对其DNA进行了解析，这也进一步刷新了DNA分子的保存年代纪录。据悉，DNA至少可保留上百年的数据，相比之下，硬盘、磁带的数据最多只能保留约10年。" \
              "3）DNA存储维护成本低。以DNA形式存储的数据易于维护，和传统的数据中心不同，不需要大量的人力、财力投入，仅需要保存在低温环境中。" \
              "在能耗方面,1GB的数据硬盘存储能耗约为0.04W,而DNA存储的能耗则小于10-10W。"

image_path = 'image.jpg'  # 替换为你的图片路径
image_output_path = '../data/output_image.jpg'  # 替换为输出图片的路径
image_diff_path = '../result/testB/'  # 替换为差异图片的保存路径

video_path = 'video.mp4'
video_output_path = 'output_video_40_twice.mp4'


def imageTest_Correction(type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    image = cv2.imread(image_path)
    if image is None:
        print("照片路径不存在!")
        sys.exit()
    encode_DNA, _ = image_encode(image, type)
    # 通过删除信道
    deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
    shape = image.shape
    estimate_image, flag = image_decode(deleted_DNA, shape, type)
    cv2.imwrite("estimate_image.jpg", estimate_image)
    difference = cv2.absdiff(image, estimate_image)
    cv2.imwrite("difference.jpg", difference)
    show_images()
    return flag


def show_images():
    img1 = mpimg.imread("image.jpg")
    img2 = mpimg.imread("estimate_image.jpg")
    img3 = mpimg.imread("difference.jpg")
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
    plt.show()


def textTest_Correction(type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    origin_text = "DNA存储与传统的存储介质不同，DNA存储技术有如下显著优势：" \
                  "1)DNA存储密度高。一个DNA分子可以保留一个物种的全部遗传信息，最大的人类染色体含有近2.5亿个碱基对，那么就意味着一条和人手差不多长的DNA链，" \
                  "就可以存储1EB（1EB=10.74亿G）数据。与硬盘和闪存的数据存储密度相比，硬盘存储每立方厘米约为1013位，闪存存储约为1016位，" \
                  "而DNA存储的密度约为1019位。2）DNA分子存储具有稳定性。" \
                  "今年2月，国际顶级学术期刊Nature上的一篇论文称古生物学家在西伯利亚东北部的永久冻土层中提取到距今120万年猛犸象的遗传物质，" \
                  "并对其DNA进行了解析，这也进一步刷新了DNA分子的保存年代纪录。据悉，DNA至少可保留上百年的数据，相比之下，硬盘、磁带的数据最多只能保留约10年。" \
                  "3）DNA存储维护成本低。以DNA形式存储的数据易于维护，和传统的数据中心不同，不需要大量的人力、财力投入，仅需要保存在低温环境中。" \
                  "在能耗方面,1GB的数据硬盘存储能耗约为0.04W,而DNA存储的能耗则小于10-10W。"
    encode_DNA, n = text_encode(origin_text, type)
    # 通过删除信道
    deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
    # deleted_DNA = channel.deletion_channel_random(encode_DNA,1)
    # length = len(origin_text.encode("utf-8"))
    estimate_str, _ = text_decode(deleted_DNA, n, type)
    print(estimate_str == origin_text)
    print(estimate_str)


def videoTest_Correction(type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()
    encode_DNA, n, frame_shape = video_encode(cap, type)
    deleted_DNA = channel.deletion_channel_random(encode_DNA, config.DEL_NUM)
    estimate_frames, _ = video_decode(deleted_DNA, n, frame_shape, type)

    # 将帧数组转换为视频
    print("重构后帧数目:", len(estimate_frames), "开始写入视频......")
    out = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*'mp4v'), min(len(estimate_frames), 30),
                          (frame_shape[1], frame_shape[0]))
    for frame in estimate_frames:
        out.write(frame)
    out.release()
    print(len(estimate_frames))


def compare_specific_frames(video_path1, video_path2, frame_number):
    # 打开两个视频文件
    cap1 = cv2.VideoCapture(video_path1)
    cap2 = cv2.VideoCapture(video_path2)

    if not cap1.isOpened() or not cap2.isOpened():
        print("Error: Could not open one of the videos.")
        return

    # 设置视频文件的当前位置到指定的帧
    cap1.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
    cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_number )

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


# # 使用示例
# video_path1 = 'output_video_40.mp4'  # 替换为你的第一个视频文件路径
# video_path2 = 'output_video_60.mp4'  # 替换为你的第二个视频文件路径
# frame_number = 10  # 指定要比较的帧号
# compare_specific_frames(video_path1, video_path2, frame_number)

# textTest_Correction(1)
# imageTest_Correction(1)
videoTest_Correction(1)
