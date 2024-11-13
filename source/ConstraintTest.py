from constraint.graph_generate import *
from constraint.division_coding import *
from constraint.fixed_length_coding import *

vertex_set, edge_set, matrix_order, capacity = graph_generate(3, 3, 4, 1)


def graph_generate_QT(m, r, l, e, x):
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    return len(vertex_set),len(vertex_set[0]),capacity;

def division_coding_QT(m, r, l, e, x):
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    division_coding(vertex_set, edge_set, capacity, 3)

def fixed_length_coding_QT(m, r, l, e, x):
    vertex_set, edge_set, matrix_order, capacity = graph_generate(m, r, l, e, x)
    fixed_length_coding(vertex_set, edge_set, capacity, 3)
