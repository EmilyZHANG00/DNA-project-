from . import Config
import numpy as np
import sys
from reedsolo import RSCodec


def byte2binary_matrix(matrix):
    binary_matrix = []
    for i in range(len(matrix)):
        list = [int(bit) for num in matrix[i] for bit in f'{num:08b}']
        binary_matrix.append(np.array(list))
    return np.array(binary_matrix).astype(np.uint8)


def binary2byte_matrix(binary_matrix):
    byte_matrix = []
    for j in range(len(binary_matrix)):
        int_list = []
        for i in range(0, len(binary_matrix[j]), 8):
            binary_8bit = binary_matrix[j][i:i + 8]
            num = int(''.join(map(str, binary_8bit)), 2)
            int_list.append(num)
        byte_matrix.append(np.array(int_list))
    return np.array(byte_matrix).astype(np.uint8)


def binary2quaternary_matrix(binary_matrix):
    quaternary_matrix = []
    for j in range(len(binary_matrix)):
        quaternary_list = []
        for i in range(0, len(binary_matrix[j]), 2):
            binary_2bit = binary_matrix[j][i:i + 2]
            num = int(''.join(map(str, binary_2bit)), 2)
            quaternary_list.append(num)
        quaternary_matrix.append(np.array(quaternary_list))
    return np.array(quaternary_matrix).astype(np.uint8)


def quaternary2binary_matrix(quaternary_matrix):
    mapping = {
        0: '00',
        1: '01',
        2: '10',
        3: '11'
    }
    binary_matrix = []
    for i in range(len(quaternary_matrix)):
        binary_str = ''.join(mapping[digit] for digit in quaternary_matrix[i])
        binary_matrix.append(np.array([int(bit) for bit in binary_str]))
    return np.array(binary_matrix)


def byte2quaternary_matrix(byte_matrix):
    binary_matrix = byte2binary_matrix(byte_matrix)
    return binary2quaternary_matrix(binary_matrix)


def quaternary2byte_matrix(byte_matrix):
    binary_matrix = quaternary2binary_matrix(byte_matrix)
    return binary2byte_matrix(binary_matrix)


def quaternary2DNA_matrix(quaternary_segments):  # 矩阵
    DNA_segments = []
    mapping = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: Config.delimiterChar}
    for i in range(len(quaternary_segments)):
        segment_list = [mapping[num] for num in quaternary_segments[i]]
        DNA_segments.append("".join(segment_list))
    return np.array(DNA_segments)


def DNA2quaternary_matrix(DNA_segments):  # 矩阵
    quaternary_segments = []
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3, Config.delimiterChar: 4}
    for i in range(len(DNA_segments)):
        DNA_arr = np.array(list(DNA_segments[i]))
        segment_list = [mapping[base] for base in DNA_arr]
        quaternary_segments.append(np.array(segment_list))
    return np.array(quaternary_segments)


def quaternary2DNA_arr(quaternary_arr):
    mapping = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: Config.delimiterChar}
    segment_list = [mapping[num] for num in quaternary_arr]
    return np.array(segment_list)


def byte2DNA_arr(byte_arr):
    conversion = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
    ACGT_str_lists = []
    for bytestr in byte_arr:
        binstr = ''.join(format(byte, '08b') for byte in bytestr)
        ACGT_str = ''
        for i in range(0, len(binstr), 2):
            ACGT_str += conversion[binstr[i:i + 2]]
        ACGT_str_lists.append(ACGT_str)
    return np.array(ACGT_str_lists)


def DNA2byte_arr(DNA_arr):
    conversion = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
    bytes_lines = []
    for str in DNA_arr:
        bin_str = ''
        for ch in str:
            bin_str += conversion[ch]
        bytes_from_bin = [int(bin_str[i:i + 8], 2) for i in range(0, len(bin_str), 8)]
        bytes_lines.append(np.array(bytes_from_bin).astype(np.uint8))
    return np.array(bytes_lines)


def DNA2quaternary_arr(DNA_array):
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3, Config.delimiterChar: 4}
    segment_list = [mapping[base] for base in DNA_array]
    return np.array(segment_list)


def split_segments(arr, segment_length):
    padding_size = segment_length - (len(arr) % segment_length) if len(arr) % segment_length != 0 else 0
    arr = np.pad(arr, (0, padding_size), 'constant', constant_values=0)
    segments = np.array_split(arr, len(arr) // segment_length)
    return np.stack(segments).astype(np.uint8)


def merge_segments(matrix, segment_length):
    flattened = []
    for i in range(len(matrix)):
        if len(matrix[i]) != segment_length:
            print(f"第 {i} 行segment长度有问题，实际长度是 {len(matrix[i])}")
            sys.exit()
        flattened.extend(matrix[i])
    return np.array(flattened)


def RS_encode(segments, param):
    ecc = RSCodec(param)
    segments_T = segments.T
    rs_segments_T = []
    for i in range(len(segments_T)):
        encode_arr = ecc.encode(bytearray(segments_T[i]))
        rs_segments_T.append(np.array(encode_arr))
    return np.array(rs_segments_T).astype(np.uint8).T


def RS_decode(matrix, param):
    ecc = RSCodec(param)
    matrix_T = matrix.T
    result_T = []
    for i in range(len(matrix_T)):
        decode_arr, _, _ = ecc.decode(bytearray(matrix_T[i]))
        result_T.append(np.array(decode_arr))
    return np.array(result_T).astype(np.uint8).T


def simple_progress_bar(current, total, desc, bar_length=40, ):
    """
    简单的进度条函数
    :param current: 当前的进度
    :param total: 总进度
    :param bar_length: 进度条的长度
    """
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(round(bar_length * current) / total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r|{bar}| {percent}% ' + desc)
    sys.stdout.flush()

    # 打印换行，表示进度条结束
    if current == total:
        print()
