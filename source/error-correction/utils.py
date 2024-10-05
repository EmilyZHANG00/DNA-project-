import config
import numpy as np
import sys


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
    mapping = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
    for i in range(len(quaternary_segments)):
        segment_list = [mapping[num] for num in quaternary_segments[i]]
        DNA_segments.append("".join(segment_list))
    return np.array(DNA_segments)


def DNA2quaternary_matrix(DNA_segments):  # 矩阵
    quaternary_segments = []
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    for i in range(len(DNA_segments)):
        DNA_arr = np.array(list(DNA_segments[i]))
        segment_list = [mapping[base] for base in DNA_arr]
        quaternary_segments.append(np.array(segment_list))
    return np.array(quaternary_segments)


def quaternary2DNA_arr(quaternary_arr):
    mapping = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: config.delimiterChar}
    segment_list = [mapping[num] for num in quaternary_arr]
    return np.array(segment_list)


def DNA2quaternary_arr(DNA_array):
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
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
