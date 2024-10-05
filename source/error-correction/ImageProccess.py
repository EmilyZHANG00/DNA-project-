import cv2
import numpy as np
from reedsolo import RSCodec, ReedSolomonError
import sys
import channel
from utils import *
import config
from DNA_BinaryEncoder import DNA_binary_encode, DNA_binary_decode


def image2array(image_path):
    image = cv2.imread(image_path)
    if image is not None:
        image_arr = image.ravel()
        return image_arr
    return None


def array2image(flattened_array, original_shape):  # 通过imshow函数展示照片
    image_reconstructed = np.reshape(flattened_array, original_shape)
    return image_reconstructed


def RS_encode(segments):
    ecc = RSCodec(config.RS_NUMBER)
    segments_T = segments.T
    rs_segments_T = []
    for i in range(len(segments_T)):
        encode_arr = ecc.encode(bytearray(segments_T[i]))
        rs_segments_T.append(np.array(encode_arr))
    return np.array(rs_segments_T).astype(np.uint8).T


def RS_decode(matrix):
    ecc = RSCodec(config.RS_NUMBER)
    matrix_T = matrix.T
    result_T = []
    for i in range(len(matrix_T)):
        decode_arr, _, _ = ecc.decode(bytearray(matrix_T[i]))
        result_T.append(np.array(decode_arr))
    return np.array(result_T).astype(np.uint8).T


def ImageProcess(filepath):
    # # 获取一维图像数组
    length = config.SEGMENT_LEN
    arr = image2array("image.png")
    if arr is None:
        print("文件路径无效!")
        sys.exit()
    # 分段（n段）
    arr_segments = split_segments(arr, length)
    # rs编码（n+k段）
    # rs_segments = RS_encode(arr_segments)
    # 数组转四进制
    quaternary_matrix = byte2quaternary_matrix(arr_segments)
    # 转DNA序列
    DNA_matrix = quaternary2DNA_matrix(quaternary_matrix)
    # 对DNA序列编码（结果含人工碱基）
    encode_DNA = DNA_binary_encode(DNA_matrix)

    deleted_indices = np.array([70, 170])
    # 通过删除信道
    deleted_DNA = channel.deletion_channel_random(encode_DNA)
    # 译码
    decode_DNA = DNA_binary_decode(deleted_DNA)
    print([(i) for i in range(len(decode_DNA)) if decode_DNA[i] != DNA_matrix[i]])
    quaternary_matrix = DNA2quaternary_matrix(decode_DNA)
    # 四进制转数组
    byte_matrix = quaternary2byte_matrix(quaternary_matrix)
    # rs译码
    # try:
    #     rs_decode = RS_decode(byte_matrix)
    # except ReedSolomonError:
    #     print("rs译码失败！")
    #     sys.exit()

    # 合并多列
    shape = [128, 128, 3]
    estimate_arr = merge_segments(byte_matrix, length)
    modified_arr = estimate_arr[:shape[0] * shape[1] * shape[2]]  # 因为分段的不能整除，最后一个段补0了

    estimate_image = array2image(modified_arr, shape)
    cv2.imshow("test", estimate_image)
    cv2.waitKey(0)


ImageProcess("image.png")
