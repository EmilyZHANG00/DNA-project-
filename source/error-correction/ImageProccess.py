import cv2
import numpy as np
from reedsolo import RSCodec, ReedSolomonError
import sys
import math
import channel
from utils import *
import config
from DNA_BinaryEncoder import DNA_binary_encode, DNA_binary_decode
from DNA_QaryEncoder import DNA_qary_encode, DNA_qary_decode


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


def extractInformationFromRS(byte_matrix):
    chunk_size = config.RS_SIZE
    num_chunks = len(byte_matrix) // chunk_size
    result = []
    for i in range(num_chunks):
        start_row = i * chunk_size
        end_row = start_row + chunk_size
        result.append(byte_matrix[start_row:end_row - config.RS_NUMBER])
    if len(byte_matrix) % chunk_size != 0:
        remaining_rows = byte_matrix[num_chunks * chunk_size:]
        result.append(remaining_rows[:-config.RS_NUMBER])
    return np.vstack(result)


def ImageProcess(filepath, type=0):
    if type not in (0, 1):
        print("错误的编码类型!")
        sys.exit()
    # # 获取一维图像数组
    if type == 0:
        length = config.SEGMENT_LEN
    else:
        length = (config.q_SEGMENT_LEN + config.q_ENCODE_LEN) // 2
    arr = image2array(filepath)
    if arr is None:
        print("文件路径无效!")
        sys.exit()
    # 分段（n段）
    arr_segments = split_segments(arr, length)
    # rs编码（n+k段）
    rs_segments = RS_encode(arr_segments)
    # 数组转四进制
    quaternary_matrix_1 = byte2quaternary_matrix(rs_segments)
    # 转DNA序列
    DNA_matrix = quaternary2DNA_matrix(quaternary_matrix_1)
    # 对DNA序列编码（结果含人工碱基）
    if type == 0:
        encode_DNA = DNA_binary_encode(DNA_matrix)
    else:
        encode_DNA = DNA_qary_encode(DNA_matrix)

    # 通过删除信道
    deleted_DNA = channel.deletion_channel_random(encode_DNA, config.DEL_NUM)
    # 译码
    if type == 0:
        decode_DNA = DNA_binary_decode(deleted_DNA)
    else:
        decode_DNA = DNA_qary_decode(deleted_DNA)
    # print(np.array_equal(decode_DNA, DNA_matrix))
    quaternary_matrix = DNA2quaternary_matrix(decode_DNA)
    # 四进制转数组

    byte_matrix = quaternary2byte_matrix(quaternary_matrix)
    shape = [128, 128, 3]
    # rs译码
    try:
        rs_decode = RS_decode(byte_matrix)
    except ReedSolomonError:
        print("rs译码失败！")
        image_matrix = extractInformationFromRS(byte_matrix)
        estimate_arr = merge_segments(image_matrix, length)
        modified_arr = estimate_arr[:np.prod(shape)]  # 因为分段的不能整除，最后一个段补0了

        estimate_image = array2image(modified_arr, shape)
        cv2.imshow("test", estimate_image)
        cv2.waitKey(0)
        sys.exit()

    # 合并多列
    estimate_arr = merge_segments(rs_decode, length)
    modified_arr = estimate_arr[:np.prod(shape)]  # 因为分段的不能整除，最后一个段补0了
    estimate_image = array2image(modified_arr, shape)
    cv2.imshow("test", estimate_image)
    cv2.waitKey(0)


# for i in range(10):
ImageProcess("image.jpeg", 1)
