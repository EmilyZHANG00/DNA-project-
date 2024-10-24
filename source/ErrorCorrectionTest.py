from correction.ImageProccess import image_decode, image_encode
from correction.VideoProcess import video_encode, video_decode
from correction.TextProcess import text_encode, text_decode
import correction.channel as channel
import correction.Config as config
import cv2
import sys
import matplotlib.pyplot as plt


def imageTest_Correction(image_path, type=0):
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
    difference = cv2.absdiff(image, estimate_image)
    show_images(image, estimate_image, difference)
    return flag


def show_images(img1, img2, img3):
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


def textTest_Correction(origin_text, type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    encode_DNA, n = text_encode(origin_text, type)
    # 通过删除信道
    deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
    estimate_str, _ = text_decode(deleted_DNA, n, type)
    print("译码后的文本：" + estimate_str)


def videoTest_Correction(video_path, type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()
    encode_DNA, n, frame_shape = video_encode(cap, type)
    deleted_DNA = channel.random_channel_Probabilistic(encode_DNA, config.BASE_LOSS_RATE)
    estimate_frames, _ = video_decode(deleted_DNA, n, frame_shape, type)

    # 将帧数组转换为视频
    print("重构后帧数目:", len(estimate_frames), "开始写入视频......")
    out = cv2.VideoWriter(video_path + "_output.mp4", cv2.VideoWriter_fourcc(*'mp4v'), min(len(estimate_frames), 30),
                          (frame_shape[1], frame_shape[0]))
    for frame in estimate_frames:
        out.write(frame)
    out.release()
    # print(len(estimate_frames))


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
            textTest_Correction(origin_text, type)
        except ValueError:
            print(f"错误：'{type}' 不是一个有效的编码类型。")

    elif integer_value == 1:
        image_path = input("请输入需要编码图片的路径：")
        try:
            type = int(input("请输入编码类型（0二元、1q元）："))
            imageTest_Correction(image_path, type)
        except ValueError:
            print(f"错误：'{type}' 不是一个有效的编码类型。")

    elif integer_value == 2:
        video_path = input("请输入需要编码视频的路径：")
        try:
            type = int(input("请输入编码类型（0二元、1q元）："))
            videoTest_Correction(video_path, type)
        except ValueError:
            print(f"错误：'{type}' 不是一个有效的编码类型。")
    else:
        print(f"错误：'{integer_value}' 不是一个有效的数据类型。")
