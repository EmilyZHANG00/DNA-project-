import math
import random
import numpy as np
from collections import Counter

def division_coding_one(vertex_set, edge_set, num,seq_len=20, x=0):
    vertex_len = len(vertex_set[0])
    len_list = []
    print("选取的二元序列为：", bin(num))
    # 进行编码
    # 实现带余除法编码时，我们默认以编号为0的点为起点
    vertex_index = 0
    coding = vertex_set[0]
    length = 0  # 当前段不包含人工碱基的序列的长度
    pre_x = 0  # 如果为1，则上一次编码添加的是X
    num_x = 0  # 已经添加的人工碱基数量
    while num != 0:
        if (length < seq_len or num_x == x) and 'X' in edge_set[vertex_index]:
            divisor = len(edge_set[vertex_index]) - 1
        else:
            divisor = len(edge_set[vertex_index])
        remainder = num % divisor
        vertex_index = vertex_set.index(edge_set[vertex_index][remainder])
        if vertex_set[vertex_index] == 'X':
            length = 0
            coding += 'X'
            pre_x = 1
            num_x += 1
        elif pre_x == 1:
            length += 1
            coding += vertex_set[vertex_index]
            pre_x = 0
        else:
            length += 1
            coding += vertex_set[vertex_index][vertex_len - 1]
        num = num // divisor
        # print(num)
    print('编码结果为：', coding[len(vertex_set[0]):])
    print('编码长度为：', len(coding) - len(vertex_set[0]))
    len_list.append(len(coding) - len(vertex_set[0]))
    # 进行解码
    num = 0
    coding_len = len(coding)
    x_index = [0]
    for i in range(coding_len):
        if coding[i] == 'X':
            x_index.append(i)
    x_index_point = len(x_index) - 1
    i = coding_len - vertex_len - 1
    num_x = len(x_index) - 1
    while i >= 0:
        pre_vertex = coding[i:i + vertex_len]
        next_vertex = coding[i + 1:i + vertex_len + 1]
        if next_vertex[vertex_len - 1] == 'X':
            next_vertex = 'X'
            # 防止X出现在最后一位
            if i == coding_len - vertex_len - 1:
                x_index_point -= 1
                num_x -= 1
        # 如果编码遇到X
        if pre_vertex[0] == 'X':
            pre_vertex = 'X'
            i -= 3
            x_index_point -= 1
            num_x -= 1
        remainder = edge_set[vertex_set.index(pre_vertex)].index(next_vertex)
        if (i - x_index[x_index_point] < seq_len or num_x == x) and 'X' in edge_set[
            vertex_set.index(pre_vertex)]:
            multiplier = len(edge_set[vertex_set.index(pre_vertex)]) - 1
        else:
            multiplier = len(edge_set[vertex_set.index(pre_vertex)])
        num = num * multiplier + remainder
        i -= 1
        # print(num)
    print('解码结果为：', bin(num))
    # 返回编码结果 解码结果 len_list
    return coding[len(vertex_set[0]):],bin(num)[2:],len_list



# def division_coding(vertex_set, edge_set, capacity, run_num=10000, seq_len=20, big_int_len=200, x=0):
#     for ii in range(run_num):
#         num = random.randint(0, pow(2, big_int_len))  # 生成一个二进制下100长的数字
#         # print("选取的二元序列为：", bin(num))
#
#     a,b,len_list =  division_coding_one(vertex_set, edge_set, num,seq_len=20, x=0)
#     keys = list(Counter(len_list).keys())
#     values = list(Counter(len_list).values())
#     sum = 0
#     for i in range(len(keys)):
#         sum += keys[i] * values[i]
#     if run_num > 10:
#         print('变长编码的平均长度为：', sum / run_num,big_int_len * run_num / sum)
#         print('码率的参考上限为：', math.log2(capacity))
#         print('变长编码存储密度为：', big_int_len * run_num / sum)
#     return  big_int_len * run_num / sum



import math
import random
import numpy as np
from collections import Counter


def division_coding(vertex_set, edge_set, capacity, run_num=10000, seq_len=20, big_int_len=200, x=0):
    vertex_len = len(vertex_set[0])
    len_list = []
    for ii in range(run_num):
        num = random.randint(0, pow(2, big_int_len))  # 生成一个二进制下100长的数字
        # print("选取的二元序列为：", bin(num))

        # 进行编码
        # 实现带余除法编码时，我们默认以编号为0的点为起点
        vertex_index = 0
        coding = vertex_set[0]
        length = 0  # 当前段不包含人工碱基的序列的长度
        pre_x = 0  # 如果为1，则上一次编码添加的是X
        num_x = 0  # 已经添加的人工碱基数量
        while num != 0:
            if (length < seq_len or num_x == x) and 'X' in edge_set[vertex_index]:
                divisor = len(edge_set[vertex_index]) - 1
            else:
                divisor = len(edge_set[vertex_index])
            remainder = num % divisor
            vertex_index = vertex_set.index(edge_set[vertex_index][remainder])
            if vertex_set[vertex_index] == 'X':
                length = 0
                coding += 'X'
                pre_x = 1
                num_x += 1
            elif pre_x == 1:
                length += 1
                coding += vertex_set[vertex_index]
                pre_x = 0
            else:
                length += 1
                coding += vertex_set[vertex_index][vertex_len - 1]
            num = num // divisor
            # print(num)
        # print('编码结果为：', coding[len(vertex_set[0]):])
        # print('编码长度为：', len(coding) - len(vertex_set[0]))
        len_list.append(len(coding) - len(vertex_set[0]))
        # 进行解码
        num = 0
        coding_len = len(coding)
        x_index = [0]
        for i in range(coding_len):
            if coding[i] == 'X':
                x_index.append(i)
        x_index_point = len(x_index) - 1
        i = coding_len - vertex_len - 1
        num_x = len(x_index) - 1
        while i >= 0:
            pre_vertex = coding[i:i + vertex_len]
            next_vertex = coding[i + 1:i + vertex_len + 1]
            if next_vertex[vertex_len - 1] == 'X':
                next_vertex = 'X'
                # 防止X出现在最后一位
                if i == coding_len - vertex_len - 1:
                    x_index_point -= 1
                    num_x -= 1
            # 如果编码遇到X
            if pre_vertex[0] == 'X':
                pre_vertex = 'X'
                i -= 3
                x_index_point -= 1
                num_x -= 1
            remainder = edge_set[vertex_set.index(pre_vertex)].index(next_vertex)
            if (i - x_index[x_index_point] < seq_len or num_x == x) and 'X' in edge_set[
                vertex_set.index(pre_vertex)]:
                multiplier = len(edge_set[vertex_set.index(pre_vertex)]) - 1
            else:
                multiplier = len(edge_set[vertex_set.index(pre_vertex)])
            num = num * multiplier + remainder
            i -= 1
            # print(num)
        # print('解码结果为：', bin(num))
    keys = list(Counter(len_list).keys())
    values = list(Counter(len_list).values())
    sum = 0
    for i in range(len(keys)):
        sum += keys[i] * values[i]
    if run_num > 10:
        print('变长编码的平均长度为：', sum / run_num)
        print('码率的参考上限为：', math.log2(capacity))
        print('变长编码存储密度为：', big_int_len * run_num / sum)
    return  big_int_len * run_num / sum
