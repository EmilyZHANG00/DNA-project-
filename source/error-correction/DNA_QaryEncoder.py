import config
import numpy as np
import random
import diff_VTCode
from utils import *
from reedsolo import RSCodec


def solve_linear_system(a_arr, b_arr, a, b):
    length = config.q_ENCODE_LEN
    q = 4
    a_num = diff_VTCode.Syn(diff_VTCode.diff(a_arr), length) % (q * length)
    b_num = diff_VTCode.Syn(diff_VTCode.diff(b_arr), length) % (q * length)
    ecc = RSCodec(2)
    encode_arr = bytearray(4)
    encode_arr[a] = a_num
    encode_arr[b] = b_num
    erase_pos = [x for x in range(4) if x not in (a, b)]
    _, decode, _ = ecc.decode(encode_arr, erase_pos=erase_pos)
    c_num = decode[erase_pos[0]]
    d_num = decode[erase_pos[1]]
    return c_num, d_num


def DNA_qary_encode(DNA_matrix):
    result = []
    for i in range(len(DNA_matrix)):
        arr = sub_encode(np.array(list(DNA_matrix[i])))
        result.append("".join(arr))
    return np.array(result)


def sub_encode(DNA_arr):  # 单个DNA序列进行编码（插入人工碱基）实现2删
    length = config.q_ENCODE_LEN
    seg_length = config.q_SEGMENT_LEN
    quaternary_arr = DNA2quaternary_arr(DNA_arr)
    separator = np.array([4])

    result_quaternary_arr = np.concatenate((quaternary_arr[:length], separator))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, quaternary_arr[length:2 * length]))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, separator))

    c_num, d_num = solve_linear_system(quaternary_arr[:length], quaternary_arr[length:2 * length], 0, 1)
    c_arr = diff_VTCode.enc_diff_vt(quaternary_arr[2 * length:2 * length + seg_length], c_num)
    d_arr = diff_VTCode.enc_diff_vt(quaternary_arr[2 * length + seg_length:2 * length + 2 * seg_length], d_num)

    result_quaternary_arr = np.concatenate((result_quaternary_arr, c_arr))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, separator))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, d_arr))

    result_DNA_arr = quaternary2DNA_arr(result_quaternary_arr)
    return result_DNA_arr


def DNA_qary_decode(encode_DNA):  # 结果移除人工碱基
    result = []
    length = config.q_ENCODE_LEN
    seg_length = config.q_SEGMENT_LEN
    total_length = length * 4 + 3
    for i in range(len(encode_DNA)):
        if len(encode_DNA[i]) == total_length:
            arr = decode_from_no_deletion(np.array(list(encode_DNA[i])))
        elif len(encode_DNA[i]) == total_length - 1:  # 单删
            arr = decode_from_one_deletion(np.array(list(encode_DNA[i])))
        elif len(encode_DNA[i]) == total_length - 2:  # 二删
            arr = decode_from_two_deletions(np.array(list(encode_DNA[i])))
        else:  # 多删
            arr = np.array(['A' for i in range((length + seg_length) * 2)])
        result.append("".join(arr))
    return np.array(result)


def decode_from_no_deletion(DNA_arr):
    indices = np.where(DNA_arr == config.delimiterChar)[0]
    deleted_indices = np.array([1, 4, 16, 64]) - 1

    a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
    b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
    c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:indices[2]])
    d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[2] + 1:])

    c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
    d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)

    ab_DNA = quaternary2DNA_arr(np.concatenate((a_arr, b_arr)))
    cd_DNA = quaternary2DNA_arr(np.concatenate((c_arr, d_arr)))
    return np.concatenate((ab_DNA, cd_DNA))


def decode_from_one_deletion(DNA_arr):
    indices = np.where(DNA_arr == config.delimiterChar)[0]
    length = config.q_ENCODE_LEN
    deleted_indices = np.array([1, 4, 16, 64]) - 1

    if len(indices) == 3:  # 非分隔符发生错误
        a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
        b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
        c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:indices[2]])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[2] + 1:])
        if len(a_arr) == length - 1:  # 错误发生在a段
            a_num, b_num = solve_linear_system(c_encode_arr, d_encode_arr, 2, 3)
            a_arr = diff_VTCode.del_correcting(a_arr, a_num)
            c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
            d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        elif len(b_arr) == length - 1:  # 错误发生在b段
            a_num, b_num = solve_linear_system(c_encode_arr, d_encode_arr, 2, 3)
            b_arr = diff_VTCode.del_correcting(b_arr, b_num)
            c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
            d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        elif len(c_encode_arr) == length - 1:  # 错误发生在c段
            c_num, d_num = solve_linear_system(a_arr, b_arr, 0, 1)
            c_arr = diff_VTCode.dec_diff_vt(c_encode_arr, c_num)
            d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        elif len(d_encode_arr) == length - 1:  # 错误发生在d段
            c_num, d_num = solve_linear_system(a_arr, b_arr, 0, 1)
            c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
            d_arr = diff_VTCode.dec_diff_vt(d_encode_arr, d_num)
        ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
        cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
        return np.concatenate((ab_DNA, cd_DNA))
    if len(indices) == 2:  # 分隔符发生错误
        if indices[0] != length:  # 错误发生在第一个分隔符
            a_arr = DNA_arr[:length]
            b_arr = DNA_arr[length:2 * length]
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
            d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:])
        elif indices[0] == length and indices[1] == 2 * length + 1:  # 错误发生在第三个分隔符
            a_arr = DNA_arr[:indices[0]]
            b_arr = DNA_arr[indices[0] + 1:indices[1]]
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:indices[1] + length + 1])
            d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + length + 1:])
        else:  # 错误发生在第二个分隔符
            a_arr = DNA_arr[:indices[0]]
            b_arr = DNA_arr[indices[0] + 1:indices[0] + length + 1]
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[0] + length + 1:indices[0] + 2 * length + 1])
            d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 2 * length + 2:])
        c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
        d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        ab_DNA = np.concatenate((a_arr, b_arr))
        cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
        return np.concatenate((ab_DNA, cd_DNA))


def decode_from_two_deletions(DNA_arr):  # 参数带人工碱基
    # 找到分隔符的位置
    indices = np.where(DNA_arr == config.delimiterChar)[0]
    # 根据分隔符判断错误类型
    if len(indices) == 1:
        result = decode_remove_two_separators(DNA_arr, indices)
    elif len(indices) == 2:
        result = decode_remove_one_separator(DNA_arr, indices)
    else:
        result = decode_remove_zero_separator(DNA_arr, indices)
    return result


def decode_remove_two_separators(DNA_arr, indices):
    length = config.q_ENCODE_LEN
    a_arr = DNA_arr[:length]
    b_arr = c_encode_arr = d_encode_arr = None
    if indices[0] == length:  # 保留第一个分隔符
        b_arr = DNA_arr[length + 1:2 * length + 1]
        c_encode_arr = DNA2quaternary_arr(DNA_arr[2 * length + 1:3 * length + 1])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[3 * length + 1:])
    elif indices[0] == 2 * length:  # 保留第二个分隔符
        b_arr = DNA_arr[length:2 * length]
        c_encode_arr = DNA2quaternary_arr(DNA_arr[2 * length + 1:3 * length + 1])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[3 * length + 1:])
    elif indices[0] == 3 * length:  # 保留第三个分隔符
        b_arr = DNA_arr[length:2 * length]
        c_encode_arr = DNA2quaternary_arr(DNA_arr[2 * length:3 * length])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[3 * length + 1:])
    deleted_indices = np.array([1, 4, 16, 64]) - 1
    c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
    d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
    ab_arr = np.concatenate((a_arr, b_arr))
    cd_arr = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
    return np.concatenate((ab_arr, cd_arr))


def decode_remove_one_separator(DNA_arr, indices):
    length = config.q_ENCODE_LEN
    deleted_indices = np.array([1, 4, 16, 64]) - 1

    if indices[0] != length and indices[0] != length - 1:  # 删除第一个分隔符
        c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:])
        if len(c_encode_arr) == length and len(d_encode_arr) == length:
            # ab块发生删除
            a_arr = DNA2quaternary_arr(DNA_arr[:length - 1])
            b_arr = DNA2quaternary_arr(DNA_arr[length:2 * length - 1])
            a_num, b_num = solve_linear_system(c_encode_arr, d_encode_arr, 2, 3)
            c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
            d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
            a_arr = diff_VTCode.del_correcting(a_arr, a_num)
            b_arr = diff_VTCode.del_correcting(b_arr, b_num)
        else:
            # cd块发生删除
            a_arr = DNA2quaternary_arr(DNA_arr[:length])
            b_arr = DNA2quaternary_arr(DNA_arr[length: 2 * length])
            c_num, d_num = solve_linear_system(a_arr, b_arr, 0, 1)
            if len(c_encode_arr) == length - 1:
                c_arr = diff_VTCode.dec_diff_vt(c_encode_arr, c_num)
                d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
            elif len(d_encode_arr) == length - 1:
                c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
                d_arr = diff_VTCode.dec_diff_vt(d_encode_arr, d_num)
    elif indices[1] != 2 * length and indices[1] != 2 * length + 1:  # 删除第二个分隔符
        a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:])
        if len(a_arr) == length and len(d_encode_arr) == length:
            # bc块发生删除
            d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
            b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[0] + length])
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] - length + 1: indices[1]])
            b_num, c_num = solve_linear_system(a_arr, d_encode_arr, 0, 3)
            b_arr = diff_VTCode.del_correcting(b_arr, b_num)
            c_arr = diff_VTCode.dec_diff_vt(c_encode_arr, c_num)
        else:
            # ad块发生删除
            b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[0] + length + 1])
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] - length: indices[1]])
            c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
            a_num, d_num = solve_linear_system(b_arr, c_encode_arr, 1, 2)
            if len(a_arr) == length - 1:
                a_arr = diff_VTCode.del_correcting(a_arr, a_num)
                d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
            elif len(d_encode_arr) == length - 1:
                d_arr = diff_VTCode.dec_diff_vt(d_encode_arr, d_num)

    else:  # 删除第三个分隔符
        a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
        b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
        if len(a_arr) == length and len(b_arr) == length:
            # cd块发生删除
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1: indices[1] + length])
            d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + length + 1:])
            c_num, d_num = solve_linear_system(a_arr, b_arr, 0, 1)
            c_arr = diff_VTCode.dec_diff_vt(c_encode_arr, c_num)
            d_arr = diff_VTCode.dec_diff_vt(d_encode_arr, d_num)
        else:
            # ab块发生删除
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1: indices[1] + length + 1])
            d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + length + 1:])
            a_num, b_num = solve_linear_system(c_encode_arr, d_encode_arr, 2, 3)
            c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
            d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
            if len(a_arr) == length - 1:
                a_arr = diff_VTCode.del_correcting(a_arr, a_num)
            elif len(b_arr) == length - 1:
                b_arr = diff_VTCode.del_correcting(b_arr, b_num)
    ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
    cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
    return np.concatenate((ab_DNA, cd_DNA))


def decode_remove_zero_separator(DNA_arr, indices):
    length = config.q_ENCODE_LEN
    deleted_indices = np.array([1, 4, 16, 64]) - 1
    a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
    b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
    c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:indices[2]])
    d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[2] + 1:])
    if len(a_arr) == length - 2 or len(b_arr) == length - 2 or len(c_encode_arr) == length - 2 or len(
            d_encode_arr) == length - 2:
        if len(a_arr) == length - 2:
            pos1, pos2 = sorted(random.sample(range(len(a_arr) + 1), 2))
            a_arr = np.concatenate(
                (a_arr[:pos1], [random.randint(0, 3)], a_arr[pos1:pos2], [random.randint(0, 3)], a_arr[pos2:]))
        elif len(b_arr) == length - 2:
            pos1, pos2 = sorted(random.sample(range(len(b_arr) + 1), 2))
            b_arr = np.concatenate(
                (b_arr[:pos1], [random.randint(0, 3)], b_arr[pos1:pos2], [random.randint(0, 3)], b_arr[pos2:]))
        elif len(c_encode_arr) == length - 2:
            pos1, pos2 = sorted(random.sample(range(len(c_encode_arr) + 1), 2))
            c_encode_arr = np.concatenate(
                (c_encode_arr[:pos1], [random.randint(0, 3)], c_encode_arr[pos1:pos2], [random.randint(0, 3)],
                 c_encode_arr[pos2:]))
        elif len(d_encode_arr) == length - 2:
            pos1, pos2 = sorted(random.sample(range(len(d_encode_arr) + 1), 2))
            d_encode_arr = np.concatenate(
                (d_encode_arr[:pos1], [random.randint(0, 3)], d_encode_arr[pos1:pos2], [random.randint(0, 3)],
                 d_encode_arr[pos2:]))
        c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
        d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
        cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
        return np.concatenate((ab_DNA, cd_DNA))
    if len(a_arr) == length - 1 and len(b_arr) == length - 1:
        c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
        d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        a_num, b_num = solve_linear_system(c_encode_arr, d_encode_arr, 2, 3)
        a_arr = diff_VTCode.del_correcting(a_arr, a_num)
        b_arr = diff_VTCode.del_correcting(b_arr, b_num)
    elif len(a_arr) == length - 1 and len(c_encode_arr) == length - 1:
        a_num, c_num = solve_linear_system(b_arr, d_encode_arr, 1, 3)
        d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        a_arr = diff_VTCode.del_correcting(a_arr, a_num)
        c_arr = diff_VTCode.dec_diff_vt(c_encode_arr, c_num)
    elif len(a_arr) == length - 1 and len(d_encode_arr) == length - 1:
        a_num, d_num = solve_linear_system(b_arr, c_encode_arr, 1, 2)
        c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
        a_arr = diff_VTCode.del_correcting(a_arr, a_num)
        d_arr = diff_VTCode.dec_diff_vt(d_encode_arr, d_num)
    elif len(b_arr) == length - 1 and len(c_encode_arr) == length - 1:
        b_num, c_num = solve_linear_system(a_arr, d_encode_arr, 0, 3)
        d_arr = np.delete(diff_VTCode.diff(d_encode_arr), deleted_indices)
        b_arr = diff_VTCode.del_correcting(b_arr, b_num)
        c_arr = diff_VTCode.dec_diff_vt(c_encode_arr, c_num)
    elif len(b_arr) == length - 1 and len(d_encode_arr) == length - 1:
        b_num, d_num = solve_linear_system(a_arr, c_encode_arr, 0, 2)
        c_arr = np.delete(diff_VTCode.diff(c_encode_arr), deleted_indices)
        b_arr = diff_VTCode.del_correcting(b_arr, b_num)
        d_arr = diff_VTCode.dec_diff_vt(d_encode_arr, d_num)
    elif len(c_encode_arr) == length - 1 and len(d_encode_arr) == length - 1:
        c_num, d_num = solve_linear_system(a_arr, b_arr, 0, 1)
        c_arr = diff_VTCode.dec_diff_vt(c_encode_arr, c_num)
        d_arr = diff_VTCode.dec_diff_vt(d_encode_arr, d_num)
    ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
    cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
    return np.concatenate((ab_DNA, cd_DNA))
