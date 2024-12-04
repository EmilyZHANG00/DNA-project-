from constraint.graph_generate import *
from constraint.division_coding import *
from constraint.fixed_length_coding import *
import time

# vertex_set, edge_set, matrix_order, capacity = graph_generate(3, 3, 4, 1)
# division_coding(vertex_set, edge_set, capacity, 1)
# fixed_length_coding(vertex_set, edge_set, capacity, 1)


def checkPara(m, r, l, e, x):
    if m & 1 == 0 or r > l or 2 * e > l + 1 or x < 0:
        return "非法输入"
    return "pass"

def graph_generate_QT(m, r, l, e, x):
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    return len(vertex_set),len(vertex_set[0]),capacity;

# seq为输入的01序列，runCnt为准备运行的次数

# 最终的return值都以string的统一形式返回
def division_coding_one_QT(m, r, l, e, x,seq):
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    a,b,c = division_coding_one(vertex_set, edge_set,int(seq,2))
    return a,b

def fixed_length_coding_one_QT(m, r, l, e, x,seq):
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    return fixed_length_coding_one(vertex_set, edge_set,capacity,int(seq,2))
def division_coding_QT(m, r, l, e, x,runCnt):
    beginTime = time.time()
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    cap =  division_coding(vertex_set, edge_set, capacity, runCnt)
    endTime = time.time()
    time_str = "{:.4f}s".format(endTime - beginTime)
    print(type(cap),endTime - beginTime)
    return  cap,time_str

def fixed_length_coding_QT(m, r, l, e, x,runCnt):
    beginTime = time.time()
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    cap =  fixed_length_coding(vertex_set, edge_set, capacity, runCnt)
    endTime = time.time()
    time_str = "{:.4f}s".format(endTime - beginTime)
    print(type(cap),endTime - beginTime)
    return  cap,time_str



# print(division_coding_one_QT(3, 3, 4, 1,1,"111111"))
# print(fixed_length_coding_one_QT(3, 3, 4, 1,1,"0101010101"))



#
# #
print(" res: " ,division_coding_QT(3, 3, 4, 1,0,20))
print(" res: " ,fixed_length_coding_QT(3, 3, 4, 1,0,20))