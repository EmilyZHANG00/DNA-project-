from . import binary_VTCode
import random
from .utils import *


def VT_decode(d, a):
    modulo = config.BINARY_MODULO
    n = len(d) + 1
    ones_indices = np.where(d == 1)[0] + 1
    zero_indices = np.where(d == 0)[0] + 1
    sum = np.sum(ones_indices) % modulo
    diff = (a - sum) % modulo
    ones = np.sum(d == 1)
    if diff == 0:
        return np.insert(d, n - 1, 0)
    if diff <= ones:
        pos = ones_indices[ones - diff] - 1
        return np.insert(d, pos, 0)
    if ones < diff and diff < n:
        pos = zero_indices[diff - ones - 1] - 1
        return np.insert(d, pos, 1)
    return np.insert(d, n - 1, 1)


def DNA_binary_encode(DNA_matrix):
    result = []
    for i in range(len(DNA_matrix)):
        arr = sub_encode(np.array(list(DNA_matrix[i])))
        result.append("".join(arr))
        simple_progress_bar(i + 1, len(DNA_matrix), "encode")
    return np.array(result)


def sub_encode(DNA_arr):  # 单个DNA序列进行编码（插入人工碱基）实现2删
    length = config.SEGMENT_LEN
    quaternary_arr = DNA2quaternary_arr(DNA_arr)
    separator = np.array([4])

    result_quaternary_arr = np.concatenate((quaternary_arr[:length], separator))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, quaternary_arr[length:2 * length]))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, separator))

    low_c, low_d, high_c, high_d = solve_linear_system(quaternary_arr[:length], quaternary_arr[length:2 * length], 5,
                                                       7, 1, 3)
    encode_low_c = binary_VTCode.vt_encode(quaternary_arr[2 * length:3 * length] & 1, low_c)
    encode_low_d = binary_VTCode.vt_encode(quaternary_arr[3 * length:4 * length] & 1, low_d)

    encode_high_c = binary_VTCode.vt_encode((quaternary_arr[2 * length:3 * length] >> 1) & 1, high_c)
    encode_high_d = binary_VTCode.vt_encode((quaternary_arr[3 * length:4 * length] >> 1) & 1, high_d)
    result_quaternary_arr = np.concatenate((result_quaternary_arr, (encode_high_c << 1) | encode_low_c))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, separator))
    result_quaternary_arr = np.concatenate((result_quaternary_arr, (encode_high_d << 1) | encode_low_d))

    result_DNA_arr = quaternary2DNA_arr(result_quaternary_arr)
    return result_DNA_arr


def DNA_binary_decode(encode_DNA):  # 结果移除人工碱基
    result = []
    length = config.SEGMENT_LEN
    encode_length = config.ENCODE_LEN
    total_length = (length + encode_length) * 2 + 3
    for i in range(len(encode_DNA)):
        if len(encode_DNA[i]) == total_length:
            arr = decode_from_no_deletion(np.array(list(encode_DNA[i])))
        elif len(encode_DNA[i]) == total_length - 1:  # 单删
            arr = decode_from_one_deletion(np.array(list(encode_DNA[i])))
        elif len(encode_DNA[i]) == total_length - 2:  # 二删
            arr = decode_from_two_deletions(np.array(list(encode_DNA[i])))
        else:  # 多删
            arr = decode_from_multi_deletions(np.array(list(encode_DNA[i])))
        result.append("".join(arr))
        simple_progress_bar(i + 1, len(encode_DNA), "decode")
    return np.array(result)


def decode_from_multi_deletions(DNA_arr):  # 处理多删
    indices = np.where(DNA_arr == config.delimiterChar)[0]
    DNA_arr = DNA2quaternary_arr(DNA_arr)
    length = config.SEGMENT_LEN
    encode_length = config.ENCODE_LEN
    deleted_indices = np.array([1, 2, 4, 8, 16, 32]) - 1
    if len(indices) == 3:
        a_arr = DNA_arr[:indices[0]]
        b_arr = DNA_arr[indices[0] + 1:indices[1]]
        c_encode_arr = DNA_arr[indices[1] + 1:indices[2]]
        d_encode_arr = DNA_arr[indices[2] + 1:]
    elif len(indices) == 2:
        if indices[0] > length:
            ab_arr = DNA_arr[:indices[0]]
            c_encode_arr = DNA_arr[indices[0] + 1:indices[1]]
            d_encode_arr = DNA_arr[indices[1] + 1:]
            del_size = 2 * length - len(ab_arr)
            a_arr = ab_arr[:length - del_size]
            b_arr = ab_arr[-(length - del_size):]
        elif indices[0] <= length and indices[1] <= 2 * length + 1:
            a_arr = DNA_arr[:indices[0]]
            b_arr = DNA_arr[indices[0] + 1:indices[1]]
            cd_encode_arr = DNA_arr[indices[1] + 1:]
            del_size = 2 * encode_length - len(cd_encode_arr)
            c_encode_arr = cd_encode_arr[:encode_length - del_size]
            d_encode_arr = cd_encode_arr[-(encode_length - del_size):]
        else:
            a_arr = DNA_arr[:indices[0]]
            bc_encode_arr = DNA_arr[indices[0] + 1:indices[1]]
            d_encode_arr = DNA_arr[indices[1] + 1:]
            del_size = length + encode_length - len(bc_encode_arr)
            b_arr = bc_encode_arr[:length - del_size]
            c_encode_arr = bc_encode_arr[-(encode_length - del_size):]
    elif len(indices) == 1:
        if indices[0] <= length:
            a_arr = DNA_arr[:indices[0]]
            bcd_encode_arr = DNA_arr[indices[0] + 1:]
            del_size = length + 2 * encode_length - len(bcd_encode_arr)
            b_arr = bcd_encode_arr[:length - del_size]
            c_encode_arr = bcd_encode_arr[length:length + encode_length - del_size]
            d_encode_arr = bcd_encode_arr[-(encode_length - del_size):]
        elif indices[0] <= 2 * length + 1:
            ab_arr = DNA_arr[:indices[0]]
            del_size = 2 * length - len(ab_arr)
            a_arr = ab_arr[:length - del_size]
            b_arr = ab_arr[-(length - del_size):]
            cd_encode_arr = DNA_arr[indices[0] + 1:]
            del_size = 2 * encode_length - len(cd_encode_arr)
            c_encode_arr = cd_encode_arr[:encode_length - del_size]
            d_encode_arr = cd_encode_arr[-(encode_length - del_size):]
        else:
            abc_encode_arr = DNA_arr[:indices[0]]
            d_encode_arr = DNA_arr[indices[0] + 1:]
            del_size = 2 * length + encode_length - len(abc_encode_arr)
            a_arr = abc_encode_arr[:length - del_size]
            b_arr = abc_encode_arr[length:2 * length - del_size]
            c_encode_arr = abc_encode_arr[-(encode_length - del_size):]
    else:
        abcd_encode_arr = DNA_arr
        del_size = 2 * (length + encode_length) - len(abcd_encode_arr)
        a_arr = abcd_encode_arr[:length - del_size]
        b_arr = abcd_encode_arr[length:2 * length - del_size]
        c_encode_arr = abcd_encode_arr[2 * length:2 * length + encode_length - del_size]
        d_encode_arr = abcd_encode_arr[-(encode_length - del_size):]
    if len(a_arr) < length:
        k = length - len(a_arr)
        positions = np.sort(np.random.choice(len(a_arr) + 1, k, replace=False))
        values_to_insert = np.random.randint(0, 4, k)
        a_arr = np.insert(a_arr, positions, values_to_insert)
    if len(b_arr) < length:
        k = length - len(b_arr)
        positions = np.sort(np.random.choice(len(b_arr) + 1, k, replace=False))
        values_to_insert = np.random.randint(0, 4, k)
        b_arr = np.insert(b_arr, positions, values_to_insert)
    if len(c_encode_arr) < encode_length:
        k = encode_length - len(c_encode_arr)
        positions = np.sort(np.random.choice(len(c_encode_arr) + 1, k, replace=False))
        values_to_insert = np.random.randint(0, 4, k)
        c_encode_arr = np.insert(c_encode_arr, positions, values_to_insert)
    if len(d_encode_arr) < encode_length:
        k = encode_length - len(d_encode_arr)
        positions = np.sort(np.random.choice(len(d_encode_arr) + 1, k, replace=False))
        values_to_insert = np.random.randint(0, 4, k)
        d_encode_arr = np.insert(d_encode_arr, positions, values_to_insert)
    c_arr = np.delete(c_encode_arr, deleted_indices)
    d_arr = np.delete(d_encode_arr, deleted_indices)
    ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
    cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
    return np.concatenate((ab_DNA, cd_DNA))


def decode_from_no_deletion(DNA_arr):
    indices = np.where(DNA_arr == config.delimiterChar)[0]
    deleted_indices = np.array([1, 2, 4, 8, 16, 32]) - 1

    a_arr = DNA_arr[:indices[0]]
    b_arr = DNA_arr[indices[0] + 1:indices[1]]
    c_encode_arr = DNA_arr[indices[1] + 1:indices[2]]
    d_encode_arr = DNA_arr[indices[2] + 1:]

    c_arr = np.delete(c_encode_arr, deleted_indices)
    d_arr = np.delete(d_encode_arr, deleted_indices)

    ab_DNA = np.concatenate((a_arr, b_arr))
    cd_DNA = np.concatenate((c_arr, d_arr))
    return np.concatenate((ab_DNA, cd_DNA))


def decode_from_one_deletion(DNA_arr):
    indices = np.where(DNA_arr == config.delimiterChar)[0]
    length = config.SEGMENT_LEN
    encode_length = config.ENCODE_LEN
    deleted_indices = np.array([1, 2, 4, 8, 16, 32]) - 1

    if len(indices) == 3:
        a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
        b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
        c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:indices[2]])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[2] + 1:])
        if len(a_arr) == length - 1:
            c_arr = np.delete(c_encode_arr, deleted_indices)
            d_arr = np.delete(d_encode_arr, deleted_indices)
            low_a, low_b, high_a, high_b = solve_linear_system(c_encode_arr, d_encode_arr, 1, 3, 5, 7)
            low_a_arr = VT_decode(a_arr & 1, low_a)
            high_a_arr = VT_decode((a_arr >> 1) & 1, high_a)
            a_arr = (high_a_arr << 1) | low_a_arr
        elif len(b_arr) == length - 1:
            c_arr = np.delete(c_encode_arr, deleted_indices)
            d_arr = np.delete(d_encode_arr, deleted_indices)
            low_a, low_b, high_a, high_b = solve_linear_system(c_encode_arr, d_encode_arr, 1, 3, 5, 7)
            low_b_arr = VT_decode(b_arr & 1, low_b)
            high_b_arr = VT_decode((b_arr >> 1) & 1, high_b)
            b_arr = (high_b_arr << 1) | low_b_arr
        elif len(c_encode_arr) == encode_length - 1:
            d_arr = np.delete(d_encode_arr, deleted_indices)
            low_c, low_d, high_c, high_d = solve_linear_system(a_arr, b_arr, 5, 7, 1, 3)
            low_c_arr = binary_VTCode.vt_decode(c_encode_arr & 1, low_c)
            high_c_arr = binary_VTCode.vt_decode((c_encode_arr >> 1) & 1, high_c)
            c_arr = (high_c_arr << 1) | low_c_arr
        elif len(d_encode_arr) == encode_length - 1:
            c_arr = np.delete(c_encode_arr, deleted_indices)
            low_c, low_d, high_c, high_d = solve_linear_system(a_arr, b_arr, 5, 7, 1, 3)
            low_d_arr = binary_VTCode.vt_decode(d_encode_arr & 1, low_d)
            high_d_arr = binary_VTCode.vt_decode((d_encode_arr >> 1) & 1, high_d)
            d_arr = (high_d_arr << 1) | low_d_arr
        ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
        cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
        return np.concatenate((ab_DNA, cd_DNA))
    if len(indices) == 2:
        if indices[0] != length:
            a_arr = DNA_arr[:length]
            b_arr = DNA_arr[length:2 * length]
            c_encode_arr = DNA_arr[indices[0] + 1:indices[1]]
            d_encode_arr = DNA_arr[indices[1] + 1:]
        elif indices[0] == length and indices[1] == 2 * length + 1:
            a_arr = DNA_arr[:indices[0]]
            b_arr = DNA_arr[indices[0] + 1:indices[1]]
            c_encode_arr = DNA_arr[indices[1] + 1:indices[1] + encode_length + 1]
            d_encode_arr = DNA_arr[indices[1] + encode_length + 1:]
        else:
            a_arr = DNA_arr[:indices[0]]
            b_arr = DNA_arr[indices[0] + 1:indices[0] + length + 1]
            c_encode_arr = DNA_arr[indices[0] + length + 1:indices[0] + length + encode_length + 1]
            d_encode_arr = DNA_arr[indices[0] + length + encode_length + 2:]
        c_arr = np.delete(c_encode_arr, deleted_indices)
        d_arr = np.delete(d_encode_arr, deleted_indices)
        ab_DNA = np.concatenate((a_arr, b_arr))
        cd_DNA = np.concatenate((c_arr, d_arr))
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


def mod_inverse(a, m):  # 求逆元
    m0 = m
    y = 0
    x = 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
    if x < 0:
        x = x + m0
    return x


def solve_linear_congruence(A, B):  # 解带余二元一次方程组
    # 计算系数的模逆元
    a1 = A[0][0]
    b1 = A[0][1]
    a2 = A[1][0]
    b2 = A[1][1]
    c1 = B[0]
    c2 = B[1]
    p = config.BINARY_MODULO
    inv_a1 = mod_inverse(a1, p)
    inv_a2 = mod_inverse(a2, p)
    # 从第一个方程解出 x
    if b1 * inv_a1 > b2 * inv_a2:
        b = (b1 * inv_a1 - b2 * inv_a2) % p
        c = (c1 * inv_a1 - c2 * inv_a2) % p
    else:
        b = (b2 * inv_a2 - b1 * inv_a1) % p
        c = (c2 * inv_a2 - c1 * inv_a1) % p
    inv_b = mod_inverse(b, p)
    y = (c * inv_b) % p
    x = (((c1 - b1 * y) % p) * inv_a1) % p
    return x, y


def solve_linear_system(a_arr, b_arr, a, b, c, d):
    Belta = config.Belta
    Gamma = config.Gamma
    modulo = config.BINARY_MODULO
    indices = np.where((a_arr & 1) == 1)[0] + 1
    low_a = np.sum(indices) % modulo
    indices = np.where(((a_arr >> 1) & 1) == 1)[0] + 1
    high_a = np.sum(indices) % modulo
    indices = np.where((b_arr & 1) == 1)[0] + 1
    low_b = np.sum(indices) % modulo
    indices = np.where(((b_arr >> 1) & 1) == 1)[0] + 1
    high_b = np.sum(indices) % modulo

    A = np.array([[1, 1],
                  [a, b]])
    B = np.array([Belta - low_a - low_b, Gamma - c * low_a - d * low_b])
    low_c, low_d = solve_linear_congruence(A, B)

    B = np.array([Belta - high_a - high_b, Gamma - c * high_a - d * high_b])
    high_c, high_d = solve_linear_congruence(A, B)
    return low_c, low_d, high_c, high_d


def decode_remove_two_separators(DNA_arr, indices):
    length = config.SEGMENT_LEN
    encode_length = config.ENCODE_LEN
    a_arr = DNA_arr[:length]
    b_arr = c_encode_arr = d_encode_arr = None
    if indices[0] == length:
        b_arr = DNA_arr[length + 1:2 * length + 1]
        c_encode_arr = DNA_arr[2 * length + 1:2 * length + encode_length + 1]
        d_encode_arr = DNA_arr[2 * length + encode_length + 1:]
    elif indices[0] == 2 * length:
        b_arr = DNA_arr[length:2 * length]
        c_encode_arr = DNA_arr[2 * length + 1:2 * length + encode_length + 1]
        d_encode_arr = DNA_arr[2 * length + encode_length + 1:]
    elif indices[0] == 2 * length + encode_length:
        b_arr = DNA_arr[length:2 * length]
        c_encode_arr = DNA_arr[2 * length:2 * length + encode_length]
        d_encode_arr = DNA_arr[2 * length + encode_length + 1:]
    # 把c_encode_arr和d_encode_arr的1、2、4、8、16、32扔掉
    deleted_indices = np.array([1, 2, 4, 8, 16, 32]) - 1
    c_arr = np.delete(c_encode_arr, deleted_indices)
    d_arr = np.delete(d_encode_arr, deleted_indices)
    ab_arr = np.concatenate((a_arr, b_arr))
    cd_arr = np.concatenate((c_arr, d_arr))
    return np.concatenate((ab_arr, cd_arr))


def decode_remove_one_separator(DNA_arr, indices):
    length = config.SEGMENT_LEN
    encode_length = config.ENCODE_LEN
    deleted_indices = np.array([1, 2, 4, 8, 16, 32]) - 1
    a_arr = b_arr = c_arr = d_arr = None
    if indices[0] != length and indices[0] != length - 1:
        # 删除第一个分隔符
        c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:])
        if len(c_encode_arr) == encode_length and len(d_encode_arr) == encode_length:
            # ab块发生删除
            a_arr = DNA2quaternary_arr(DNA_arr[:length - 1])
            b_arr = DNA2quaternary_arr(DNA_arr[length:2 * length - 1])
            c_arr = np.delete(c_encode_arr, deleted_indices)
            d_arr = np.delete(d_encode_arr, deleted_indices)
            low_a, low_b, high_a, high_b = solve_linear_system(c_encode_arr, d_encode_arr, 1, 3, 5, 7)
            low_a_arr = VT_decode(a_arr & 1, low_a)
            low_b_arr = VT_decode(b_arr & 1, low_b)
            high_a_arr = VT_decode((a_arr >> 1) & 1, high_a)
            high_b_arr = VT_decode((b_arr >> 1) & 1, high_b)
            a_arr = (high_a_arr << 1) | low_a_arr
            b_arr = (high_b_arr << 1) | low_b_arr
        else:
            # cd块发生删除
            a_arr = DNA2quaternary_arr(DNA_arr[:length])
            b_arr = DNA2quaternary_arr(DNA_arr[length: 2 * length])
            low_c, low_d, high_c, high_d = solve_linear_system(a_arr, b_arr, 5, 7, 1, 3)
            if len(c_encode_arr) == encode_length - 1:
                d_arr = np.delete(d_encode_arr, deleted_indices)
                low_c_arr = binary_VTCode.vt_decode(c_encode_arr & 1, low_c)
                high_c_arr = binary_VTCode.vt_decode((c_encode_arr >> 1) & 1, high_c)
                c_arr = (high_c_arr << 1) | low_c_arr
            elif len(d_encode_arr) == encode_length - 1:
                c_arr = np.delete(c_encode_arr, deleted_indices)
                low_d_arr = binary_VTCode.vt_decode(d_encode_arr & 1, low_d)
                high_d_arr = binary_VTCode.vt_decode((d_encode_arr >> 1) & 1, high_d)
                d_arr = (high_d_arr << 1) | low_d_arr
    elif indices[1] != 2 * length and indices[1] != 2 * length + 1:
        # 删除第二个分隔符
        a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
        d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:])
        if len(a_arr) == length and len(d_encode_arr) == encode_length:
            # bc块发生删除
            d_arr = np.delete(d_encode_arr, deleted_indices)
            b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[0] + length])
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] - encode_length + 1: indices[1]])
            low_b, low_c, high_b, high_c = solve_linear_system(a_arr, d_encode_arr, 3, 5, 1, 7)
            low_b_arr = VT_decode(b_arr & 1, low_b)
            low_c_arr = binary_VTCode.vt_decode(c_encode_arr & 1, low_c)
            high_b_arr = VT_decode((b_arr >> 1) & 1, high_b)
            high_c_arr = binary_VTCode.vt_decode((c_encode_arr >> 1) & 1, high_c)
            b_arr = (high_b_arr << 1) | low_b_arr
            c_arr = (high_c_arr << 1) | low_c_arr
        else:
            # ad块发生删除
            b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[0] + length + 1])
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] - encode_length: indices[1]])
            c_arr = np.delete(c_encode_arr, deleted_indices)
            low_a, low_d, high_a, high_d = solve_linear_system(b_arr, c_encode_arr, 1, 7, 3, 5)
            if len(a_arr) == length - 1:
                low_a_arr = VT_decode(a_arr & 1, low_a)
                high_a_arr = VT_decode((a_arr >> 1) & 1, high_a)
                a_arr = (high_a_arr << 1) | low_a_arr
                d_arr = np.delete(d_encode_arr, deleted_indices)
            elif len(d_encode_arr) == encode_length - 1:
                low_d_arr = binary_VTCode.vt_decode(d_encode_arr & 1, low_d)
                high_d_arr = binary_VTCode.vt_decode((d_encode_arr >> 1) & 1, high_d)
                d_arr = (high_d_arr << 1) | low_d_arr

    else:
        # 删除第三个分隔符
        a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
        b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
        if len(a_arr) == length and len(b_arr) == length:
            # cd块发生删除
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1: indices[1] + encode_length])
            d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + encode_length + 1:])
            low_c, low_d, high_c, high_d = solve_linear_system(a_arr, b_arr, 5, 7, 1, 3)

            low_c_arr = binary_VTCode.vt_decode(c_encode_arr & 1, low_c)
            low_d_arr = binary_VTCode.vt_decode(d_encode_arr & 1, low_d)
            high_c_arr = binary_VTCode.vt_decode((c_encode_arr >> 1) & 1, high_c)
            high_d_arr = binary_VTCode.vt_decode((d_encode_arr >> 1) & 1, high_d)

            c_arr = (high_c_arr << 1) | low_c_arr
            d_arr = (high_d_arr << 1) | low_d_arr
        else:
            # ab块发生删除
            c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1: indices[1] + encode_length + 1])
            d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + encode_length + 1:])
            c_arr = np.delete(c_encode_arr, deleted_indices)
            d_arr = np.delete(d_encode_arr, deleted_indices)
            low_a, low_b, high_a, high_b = solve_linear_system(c_encode_arr, d_encode_arr, 1, 3, 5, 7)
            if len(a_arr) == length - 1:
                low_a_arr = VT_decode(a_arr & 1, low_a)
                high_a_arr = VT_decode((a_arr >> 1) & 1, high_a)
                a_arr = (high_a_arr << 1) | low_a_arr
            elif len(b_arr) == length - 1:
                low_b_arr = VT_decode(b_arr & 1, low_b)
                high_b_arr = VT_decode((b_arr >> 1) & 1, high_b)
                b_arr = (high_b_arr << 1) | low_b_arr
    ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
    cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
    return np.concatenate((ab_DNA, cd_DNA))


def decode_remove_zero_separator(DNA_arr, indices):
    length = config.SEGMENT_LEN
    encode_length = config.ENCODE_LEN
    deleted_indices = np.array([1, 2, 4, 8, 16, 32]) - 1
    a_arr = DNA2quaternary_arr(DNA_arr[:indices[0]])
    b_arr = DNA2quaternary_arr(DNA_arr[indices[0] + 1:indices[1]])
    c_encode_arr = DNA2quaternary_arr(DNA_arr[indices[1] + 1:indices[2]])
    d_encode_arr = DNA2quaternary_arr(DNA_arr[indices[2] + 1:])
    if len(a_arr) == length - 2 or len(b_arr) == length - 2 or len(c_encode_arr) == encode_length - 2 or len(
            d_encode_arr) == encode_length - 2:
        if len(a_arr) == length - 2:
            pos1, pos2 = sorted(random.sample(range(len(a_arr) + 1), 2))
            a_arr = np.concatenate(
                (a_arr[:pos1], [random.randint(0, 3)], a_arr[pos1:pos2], [random.randint(0, 3)], a_arr[pos2:]))
        elif len(b_arr) == length - 2:
            pos1, pos2 = sorted(random.sample(range(len(b_arr) + 1), 2))
            b_arr = np.concatenate(
                (b_arr[:pos1], [random.randint(0, 3)], b_arr[pos1:pos2], [random.randint(0, 3)], b_arr[pos2:]))
        elif len(c_encode_arr) == encode_length - 2:
            pos1, pos2 = sorted(random.sample(range(len(c_encode_arr) + 1), 2))
            c_encode_arr = np.concatenate(
                (c_encode_arr[:pos1], [random.randint(0, 3)], c_encode_arr[pos1:pos2], [random.randint(0, 3)],
                 c_encode_arr[pos2:]))
        elif len(d_encode_arr) == encode_length - 2:
            pos1, pos2 = sorted(random.sample(range(len(d_encode_arr) + 1), 2))
            d_encode_arr = np.concatenate(
                (d_encode_arr[:pos1], [random.randint(0, 3)], d_encode_arr[pos1:pos2], [random.randint(0, 3)],
                 d_encode_arr[pos2:]))
        c_arr = np.delete(c_encode_arr, deleted_indices)
        d_arr = np.delete(d_encode_arr, deleted_indices)
        ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
        cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
        return np.concatenate((ab_DNA, cd_DNA))
    if len(a_arr) == length - 1 and len(b_arr) == length - 1:
        c_arr = np.delete(c_encode_arr, deleted_indices)
        d_arr = np.delete(d_encode_arr, deleted_indices)

        low_a, low_b, high_a, high_b = solve_linear_system(c_encode_arr, d_encode_arr, 1, 3, 5, 7)
        low_a_arr = VT_decode(a_arr & 1, low_a)
        low_b_arr = VT_decode(b_arr & 1, low_b)
        high_a_arr = VT_decode((a_arr >> 1) & 1, high_a)
        high_b_arr = VT_decode((b_arr >> 1) & 1, high_b)

        a_arr = (high_a_arr << 1) | low_a_arr
        b_arr = (high_b_arr << 1) | low_b_arr
    elif len(a_arr) == length - 1 and len(c_encode_arr) == encode_length - 1:
        d_arr = np.delete(d_encode_arr, deleted_indices)
        low_a, low_c, high_a, high_c = solve_linear_system(b_arr, d_encode_arr, 1, 5, 3, 7)

        low_a_arr = VT_decode(a_arr & 1, low_a)
        low_c_arr = binary_VTCode.vt_decode(c_encode_arr & 1, low_c)
        high_a_arr = VT_decode((a_arr >> 1) & 1, high_a)
        high_c_arr = binary_VTCode.vt_decode((c_encode_arr >> 1) & 1, high_c)

        a_arr = (high_a_arr << 1) | low_a_arr
        c_arr = (high_c_arr << 1) | low_c_arr
    elif len(a_arr) == length - 1 and len(d_encode_arr) == encode_length - 1:
        c_arr = np.delete(c_encode_arr, deleted_indices)
        low_a, low_d, high_a, high_d = solve_linear_system(b_arr, c_encode_arr, 1, 7, 3, 5)

        low_a_arr = VT_decode(a_arr & 1, low_a)
        low_d_arr = binary_VTCode.vt_decode(d_encode_arr & 1, low_d)
        high_a_arr = VT_decode((a_arr >> 1) & 1, high_a)
        high_d_arr = binary_VTCode.vt_decode((d_encode_arr >> 1) & 1, high_d)

        a_arr = (high_a_arr << 1) | low_a_arr
        d_arr = (high_d_arr << 1) | low_d_arr
    elif len(b_arr) == length - 1 and len(c_encode_arr) == encode_length - 1:
        d_arr = np.delete(d_encode_arr, deleted_indices)
        low_b, low_c, high_b, high_c = solve_linear_system(a_arr, d_encode_arr, 3, 5, 1, 7)

        low_b_arr = VT_decode(b_arr & 1, low_b)
        low_c_arr = binary_VTCode.vt_decode(c_encode_arr & 1, low_c)
        high_b_arr = VT_decode((b_arr >> 1) & 1, high_b)
        high_c_arr = binary_VTCode.vt_decode((c_encode_arr >> 1) & 1, high_c)

        b_arr = (high_b_arr << 1) | low_b_arr
        c_arr = (high_c_arr << 1) | low_c_arr
    elif len(b_arr) == length - 1 and len(d_encode_arr) == encode_length - 1:
        c_arr = np.delete(c_encode_arr, deleted_indices)
        low_b, low_d, high_b, high_d = solve_linear_system(a_arr, c_encode_arr, 3, 7, 1, 5)

        low_b_arr = VT_decode(b_arr & 1, low_b)
        low_d_arr = binary_VTCode.vt_decode(d_encode_arr & 1, low_d)
        high_b_arr = VT_decode((b_arr >> 1) & 1, high_b)
        high_d_arr = binary_VTCode.vt_decode((d_encode_arr >> 1) & 1, high_d)

        b_arr = (high_b_arr << 1) | low_b_arr
        d_arr = (high_d_arr << 1) | low_d_arr
    elif len(c_encode_arr) == encode_length - 1 and len(d_encode_arr) == encode_length - 1:
        low_c, low_d, high_c, high_d = solve_linear_system(a_arr, b_arr, 5, 7, 1, 3)
        low_c_arr = binary_VTCode.vt_decode(c_encode_arr & 1, low_c)
        low_d_arr = binary_VTCode.vt_decode(d_encode_arr & 1, low_d)
        high_c_arr = binary_VTCode.vt_decode((c_encode_arr >> 1) & 1, high_c)
        high_d_arr = binary_VTCode.vt_decode((d_encode_arr >> 1) & 1, high_d)

        c_arr = (high_c_arr << 1) | low_c_arr
        d_arr = (high_d_arr << 1) | low_d_arr
    ab_DNA = np.concatenate((quaternary2DNA_arr(a_arr), quaternary2DNA_arr(b_arr)))
    cd_DNA = np.concatenate((quaternary2DNA_arr(c_arr), quaternary2DNA_arr(d_arr)))
    return np.concatenate((ab_DNA, cd_DNA))
