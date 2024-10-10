from reedsolo import RSCodec, ReedSolomonError
from .utils import *
from .DNA_BinaryEncoder import DNA_binary_encode, DNA_binary_decode
from .DNA_QaryEncoder import DNA_qary_encode, DNA_qary_decode


def text_encode(original_text, type=0):
    if type == 0:
        length = config.SEGMENT_LEN
    else:
        length = (config.q_SEGMENT_LEN + config.q_ENCODE_LEN) // 2
    utf8_bytes = bytearray(original_text.encode('utf-8'))
    print("1 编码为字节串内容:", len(utf8_bytes), utf8_bytes)
    arr_segments = split_segments(utf8_bytes, length)
    rs_segments = RS_encode(arr_segments)
    quaternary_matrix_1 = byte2quaternary_matrix(rs_segments)
    # 转DNA序列
    DNA_matrix = quaternary2DNA_matrix(quaternary_matrix_1)
    # 对DNA序列编码（结果含人工碱基）
    if type == 0:
        encode_DNA = DNA_binary_encode(DNA_matrix)
    else:
        encode_DNA = DNA_qary_encode(DNA_matrix)
    return encode_DNA


def text_decode(deleted_DNA, arr_length, type=0):
    if type == 0:
        length = config.SEGMENT_LEN
    else:
        length = (config.q_SEGMENT_LEN + config.q_ENCODE_LEN) // 2
    if type == 0:
        decode_DNA = DNA_binary_decode(deleted_DNA)
    else:
        decode_DNA = DNA_qary_decode(deleted_DNA)
    quaternary_matrix = DNA2quaternary_matrix(decode_DNA)
    # 四进制转数组
    byte_matrix = quaternary2byte_matrix(quaternary_matrix)
    # rs译码
    try:
        text_matrix = RS_decode(byte_matrix)
        flag = True
    except ReedSolomonError:
        print("rs译码失败！")
        flag = False
        text_matrix = extractInformationFromRS(byte_matrix)
    # 合并多列
    estimate_arr = merge_segments(text_matrix, length)
    modified_arr = estimate_arr[:arr_length]  # 因为分段的不能整除，最后一个段补0了
    byte_array = bytes(modified_arr)
    return byte_array.decode('utf-8'), flag


def extractInformationFromRS(byte_matrix):
    chunk_size = config.RS_SIZE
    num_chunks = len(byte_matrix) // chunk_size
    result = []
    for i in range(num_chunks):
        start_row = i * chunk_size
        end_row = start_row + chunk_size
        result.append(byte_matrix[start_row:end_row - config.RS_text])
    if len(byte_matrix) % chunk_size != 0:
        remaining_rows = byte_matrix[num_chunks * chunk_size:]
        result.append(remaining_rows[:-config.RS_text])
    return np.vstack(result)
