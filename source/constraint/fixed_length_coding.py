import math
import random


def fixed_length_coding(vertex_set, edge_set, capacity, run_num, l=8):
    path_set = []
    vertex_len = len(vertex_set[0])
    for i in range(len(vertex_set)):
        path = []
        for vertex in edge_set[i]:
            path.append(vertex_set[i] + vertex[vertex_len - 1])
        path_set.append(path)

    p = 2
    # capacity = 2.573885669550532                          #3-SSA,3-RLL,(4,1)-局部GC约束的稀疏矩阵对应的谱半径
    q = 99999999  # 防止第一次判定循环没设置q
    while p / q < 0.85 * math.log2(capacity):
        p += 1
        p_len = pow(2, p)
        # 统计每个点的出度
        min_path_num = 99999999999
        for i in path_set:
            if min_path_num > len(i):
                min_path_num = len(i)

        # 对矩阵进行迭代，并保存路径
        while min_path_num < p_len:
            new_path_set = []
            for i in range(len(vertex_set)):
                new_path = []
                for path in path_set[i]:
                    last_vertex = path[len(path) - vertex_len:len(path)]
                    last_vertex_index = vertex_set.index(last_vertex)
                    for edge in edge_set[last_vertex_index]:
                        new_path.append(path + edge[len(edge) - 1])
                new_path_set.append(new_path)
            path_set = new_path_set
            min_path_num = 99999999999
            for i in path_set:
                if min_path_num > len(i):
                    min_path_num = len(i)
        q = len(path_set[0][0]) - len(vertex_set[0])
        # print(len(path_set[0][0]) - 4)
        # print(min_path_num)
    print('选取的定长编码比例为：', p, ':', q, sep='')

    # 进行编码
    for ii in range(run_num):
        vertex_index = 0  # 设定第一次进行编码的位置
        num = random.randint(0, pow(2, p * l))
        print('随机选择的大整数为：', num)
        coding = ''
        for i in range(l):
            remainder = num % pow(2, p)
            coding += path_set[vertex_index][remainder][len(vertex_set[0]):q + len(vertex_set[0])]
            vertex_index = vertex_set.index(path_set[vertex_index][remainder][q:q + len(vertex_set[0])])
            num = num >> p
        print('编码结果为：', coding)

        # 进行解码
        num = 0
        coding = vertex_set[0] + coding
        for i in range(l):
            lenc = len(coding)
            path = coding[lenc - len(path_set[0][0]):lenc]
            pre_vertex = path[0:len(vertex_set[0])]
            remainder = path_set[vertex_set.index(pre_vertex)].index(path)
            num = remainder + (num << p)
            coding = coding[0:len(coding) - q]
        print('解码结果为：', num)
    return
