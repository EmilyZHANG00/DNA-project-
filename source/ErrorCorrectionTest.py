from correction.ImageProccess import image_decode, image_encode
import correction.channel as channel
import correction.config as config
import cv2
import sys


def imageTest_Correction(type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    image = cv2.imread("image.jpg")
    if image is None:
        print("照片路径不存在!")
        sys.exit()
    encode_DNA = image_encode(image, type)
    # 通过删除信道
    deleted_DNA = channel.deletion_channel_random(encode_DNA, config.DEL_NUM)
    shape = image.shape
    estimate_image, _ = image_decode(deleted_DNA, shape, type)
    cv2.imshow("test", estimate_image)
    cv2.waitKey(0)


imageTest_Correction()
