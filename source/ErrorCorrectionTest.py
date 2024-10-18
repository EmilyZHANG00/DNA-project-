from correction.ImageProccess import image_decode, image_encode
from correction.TextProcess import text_encode, text_decode
import correction.channel as channel
import correction.config as config
import cv2
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image


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


def testTest_Correction(type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    str = "DNA存储与传统的存储介质不同，DNA存储技术有如下显著优势：" \
          "1)DNA存储密度高。一个DNA分子可以保留一个物种的全部遗传信息，最大的人类染色体含有近2.5亿个碱基对，那么就意味着一条和人手差不多长的DNA链，" \
          "就可以存储1EB（1EB=10.74亿G）数据。与硬盘和闪存的数据存储密度相比，硬盘存储每立方厘米约为1013位，闪存存储约为1016位，" \
          "而DNA存储的密度约为1019位。2）DNA分子存储具有稳定性。" \
          "今年2月，国际顶级学术期刊Nature上的一篇论文称古生物学家在西伯利亚东北部的永久冻土层中提取到距今120万年猛犸象的遗传物质，" \
          "并对其DNA进行了解析，这也进一步刷新了DNA分子的保存年代纪录。据悉，DNA至少可保留上百年的数据，相比之下，硬盘、磁带的数据最多只能保留约10年。" \
          "3）DNA存储维护成本低。以DNA形式存储的数据易于维护，和传统的数据中心不同，不需要大量的人力、财力投入，仅需要保存在低温环境中。" \
          "在能耗方面,1GB的数据硬盘存储能耗约为0.04W,而DNA存储的能耗则小于10-10W。"
    encode_DNA = text_encode(str, type)
    # 通过删除信道
    deleted_DNA = channel.deletion_channel_random(encode_DNA, config.DEL_NUM)
    arr_length = len(str.encode("utf-8"))
    estimate_str, _ = text_decode(deleted_DNA, arr_length, type)
    print(estimate_str==str)
    print(estimate_str)

# imageTest_Correction(0)
# testTest_Correction(1)
# testTest_Correction()
# success=0
# fail =0
# for i in range(9):
#     flag =imageTest_Correction()
#     if flag:
#         success+=1
#     else:
#         fail+=1
# print(success/(success+fail))
