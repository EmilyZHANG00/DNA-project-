from itertools import product
import math
import numpy

dict = 'ACGT'


# 生成m长的所有序列
def generate_strings(dict, m):
    # 使用 itertools.product 生成所有可能的组合
    return [''.join(p) for p in product(dict, repeat=m)]


# 进行RLL约束
def RLL_constraint(vertex_set, r):
    vertex_num = len(vertex_set)  # 统计当前点集中的点对应碱基序列的长度
    i = 0
    while i < vertex_num:
        # 如果存在r长的相同游程，删除
        if 'A' * r in vertex_set[i] or 'C' * r in vertex_set[i] or 'G' * r in vertex_set[i] or 'T' * r in vertex_set[i]:
            vertex_set.remove(vertex_set[i])
            vertex_num -= 1
        else:
            i += 1
    return


# 进行SSA约束
def SSA_constraint(vertex_set, m):
    vertex_num = len(vertex_set)  # 统计当前点集中的点对应碱基序列的长度
    i = 0
    while i < vertex_num:
        num = 0
        # 统计每个点对应的碱基序列AC的个数之和，如果低于一半，将这个点从点集中删除
        for j in vertex_set[i]:
            if j == 'A' or j == 'C':
                num += 1
        if num < m / 2:
            vertex_set.remove(vertex_set[i])
            vertex_num -= 1
        else:
            i += 1
    return


# 进行GC局部约束
def GC_constraint(vertex_set, l, e):
    vertex_num = len(vertex_set)  # 统计当前点集中的点对应碱基序列的长度
    vertex_length = len(vertex_set[0])
    i = 0
    while i < vertex_num:
        GC = 0
        for j in range(vertex_length - l + 1):
            vertex = vertex_set[i][j:j + l]
            gc_num = 0  # 记录GC和AT的差值
            for k in vertex:
                if k == 'G' or k == 'C':
                    gc_num += 1
                else:
                    gc_num -= 1
            # 如果存在一个序列GC和AT数量的差值超过2e，则删除该元素
            if abs(gc_num) > 2 * e:
                GC = 1
                break
        if GC == 0:
            i += 1
        else:
            vertex_set.remove(vertex_set[i])
            vertex_num -= 1
    return


# 矩阵迭代
def matrix_iterative(vertex_set, iterative_num):
    for i in range(iterative_num):
        vertex_len = len(vertex_set[0])
        new_vertex_set = []
        # 记录德布罗因图中对应的边
        # 利用已经记录的边推出长度++的德布罗因图
        for vertex in vertex_set:
            for j in 'ACGT':
                # 寻找以点vertex为起点的边对应的终点
                temp_vertex = vertex[1:vertex_len] + j
                # 如果终点在原本的德布罗因图中，就将这条边对应的路径放到放到新的德布罗因图的点集中
                if temp_vertex in vertex_set:
                    new_vertex_set.append(vertex + j)
        vertex_set = new_vertex_set
    return vertex_set


# 幂法计算谱半径
def spectral_radii_cal(vertex_set, edge_set, sub):
    eigenvector = [1] * len(vertex_set)
    test = 1
    while test == 1:
        # for i in range(100):
        # 以后改成while循环
        new_eigenvector = [0] * len(vertex_set)
        for i in range(len(vertex_set)):
            for vertex in edge_set[i]:
                j = vertex_set.index(vertex)  # 代表矩阵的第i行第j列为1
                new_eigenvector[i] += eigenvector[j]
        sum1 = 0  # 用来计算v(k+1)点乘v(k)
        sum2 = 0  # 用来计算v(k)点乘v(k)
        # 计算本次迭代对应的特征值估计
        sum1 = numpy.dot(numpy.array(new_eigenvector), numpy.array(eigenvector).T)
        sum2 = numpy.dot(numpy.array(eigenvector), numpy.array(eigenvector).T)
        eigenvalue = sum1 / sum2
        # 向量归一化
        sum = numpy.dot(numpy.array(new_eigenvector), numpy.array(new_eigenvector).T)
        sum = math.sqrt(sum)
        # 每次循环将test重置，如果出现特征向量某一位的差值大于阈值，那么就再次进行循环
        test = 0
        for i in range(len(vertex_set)):
            # 进行归一化
            new_eigenvector[i] = numpy.array(new_eigenvector[i]) / sum
            if abs(new_eigenvector[i] - eigenvector[i]) > sub:
                test = 1
        # 如果超过阈值，将vk+1的值保存下来
        if test == 1:
            for i in range(len(vertex_set)):
                eigenvector[i] = new_eigenvector[i]
    return eigenvalue


def graph_generate(m, r, l, e, x=0, sub=0.000001):
    # m = int(input('请输入SSA约束的长度参数：'))
    # r = int(input('请输入RLL约束的长度参数：'))
    # l = int(input('请输入GC局部约束的长度参数：'))
    # e = int(input('请输入GC局部约束的GC和AT个数之差的阈值：'))
    # x = int(input('请输入添加人工碱基的个数：'))
    if m & 1 == 0 or r > l or 2 * e > l + 1 or x < 0:
        print("非法输入")
        exit()
    vertex_set = generate_strings(dict, m)
    # 首先进行SSA约束
    SSA_constraint(vertex_set, m)
    # 考虑m,r,l的大小顺序，考虑是否要对矩阵迭代后再进行约束
    if m >= r and m >= l:
        RLL_constraint(vertex_set, r)
        GC_constraint(vertex_set, l, e)
    elif r <= m and m < l:
        RLL_constraint(vertex_set, r)
        vertex_set = matrix_iterative(vertex_set, l - m)
        GC_constraint(vertex_set, l, e)
    else:
        vertex_set = matrix_iterative(vertex_set, r - m)
        RLL_constraint(vertex_set, r)
        vertex_set = matrix_iterative(vertex_set, l - r)
        GC_constraint(vertex_set, l, e)

    edge_set = []
    vertex_len = len(vertex_set[0])
    for vertex in vertex_set:
        temp_edge = []
        for i in 'ACGT':
            # 寻找以点vertex为起点的边
            temp_vertex = vertex[1:vertex_len] + i
            # 如果存在，就放到对应的列表中
            if temp_vertex in vertex_set:
                temp_edge += [temp_vertex]
            # 考虑到德布罗因图中不存在出度为0的点，故不考虑temp_edge为空的情况
        edge_set += [temp_edge]

    # 此处默认将x和所有点集中的序列有双向边
    if x > 0:
        x_pre_vertex_set = vertex_set  # 输入能直接走到人工碱基的所有序列，默认设置成全部
        x_next_vertex_set = vertex_set  # 输入x能直接走到的所有序列，默认设置成全部

    # 前面加入会引起矩阵构造出问题，现在加入，保证后面输出点集和边集时包含带有X
    if x > 0:
        # 构造以x为终点的边.以x为起点的边
        for vertex in x_pre_vertex_set:
            edge_set[vertex_set.index(vertex)].append('X')
        # 将以X为起点的边添加到坐标集中
        edge_set.append(x_next_vertex_set)
        # 将点X添加到点集中
        vertex_set.append('X')

    if x > 0:
        matrix_order = (x + 1) * len(vertex_set)
    else:
        matrix_order = len(vertex_set)

    eigenvalue = spectral_radii_cal(vertex_set, edge_set, sub)
    print('1碱基=', math.log2(eigenvalue), 'bit', sep='')
    print('矩阵的阶为：', matrix_order)
    print('谱半径为：', eigenvalue)
    return vertex_set, edge_set, matrix_order, eigenvalue
