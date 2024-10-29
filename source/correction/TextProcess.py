from reedsolo import RSCodec, ReedSolomonError
from .utils import *
from .DNA_BinaryEncoder import DNA_binary_encode, DNA_binary_decode
from .DNA_QaryEncoder import DNA_qary_encode, DNA_qary_decode

from . import Config


def text_encode(original_text, type=0):
    if type == 0:
        length = Config.SEGMENT_LEN
    else:
        length = (Config.q_SEGMENT_LEN + Config.q_ENCODE_LEN) // 2
    utf8_bytes = bytearray(original_text.encode('utf-8'))
    date_seq_cnt = len(utf8_bytes)

    # print("1 编码为字节串内容:", len(utf8_bytes), utf8_bytes)
    arr_segments = split_segments(utf8_bytes, length)
    rs_segments = RS_encode(arr_segments, Config.RS_text)
    DNA_matrix = byte2DNA_arr(rs_segments)
    # 对DNA序列编码（结果含人工碱基）
    if type == 0:
        encode_DNA = DNA_binary_encode(DNA_matrix)
    else:
        encode_DNA = DNA_qary_encode(DNA_matrix)
    return encode_DNA, date_seq_cnt


def text_decode(deleted_DNA, arr_length, type=0):
    if type == 0:
        length = Config.SEGMENT_LEN
    else:
        length = (Config.q_SEGMENT_LEN + Config.q_ENCODE_LEN) // 2
    if type == 0:
        decode_DNA, result_str = DNA_binary_decode(deleted_DNA)
    else:
        decode_DNA, result_str = DNA_qary_decode(deleted_DNA)
    byte_matrix = DNA2byte_arr(decode_DNA)
    try:
        text_matrix = RS_decode(byte_matrix, Config.RS_text)
    except ReedSolomonError:
        print("rs译码失败！")
        result_str = result_str + "\nrs译码失败！"
        text_matrix = extractInformationFromRS(byte_matrix)
    # 合并多列
    estimate_arr = merge_segments(text_matrix, length)
    modified_arr = estimate_arr[:arr_length]  # 因为分段的不能整除，最后一个段补0了
    byte_array = bytes(modified_arr)
    return byte_array.decode('utf-8'), result_str


def extractInformationFromRS(byte_matrix):
    chunk_size = Config.RS_SIZE
    num_chunks = len(byte_matrix) // chunk_size
    result = []
    for i in range(num_chunks):
        start_row = i * chunk_size
        end_row = start_row + chunk_size
        result.append(byte_matrix[start_row:end_row - Config.RS_text])
    if len(byte_matrix) % chunk_size != 0:
        remaining_rows = byte_matrix[num_chunks * chunk_size:]
        result.append(remaining_rows[:-Config.RS_text])
    return np.vstack(result)
