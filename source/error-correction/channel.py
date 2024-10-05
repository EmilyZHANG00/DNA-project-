import random

import numpy as np


def split_integer(sum, n):
    if n <= 0 or sum <= 0:
        raise ValueError("k and n must be positive integers.")
    # 随机生成n-1个分割点(随机生成)
    splits = sorted(random.choices(range(1, sum), k=n - 1))
    # 计算每个部分的值
    parts = [splits[0]] + [splits[i] - splits[i - 1] for i in range(1, n - 1)] + [sum - splits[-1]]
    return parts


def deletion_channel_random(sequences, error_probabilities=[0.09, 0.9, 0.01, 0]):
    for i in range(len(sequences)):
        num_errors = random.choices([0, 1, 2, 3], weights=error_probabilities)[0]
        error_indices = sorted(random.sample(range(len(sequences[i])), num_errors), reverse=True)
        for idx in range(len(error_indices)):
            sequences[i] = sequences[i][:idx] + sequences[i][idx + 1:]

    return sequences


def deletion_channel_at_index(sequences, deleted_indices):
    for i in range(len(sequences)):
        for idx in range(len(deleted_indices)):
            sequences[i] = sequences[i][:deleted_indices[idx] - idx] + sequences[i][deleted_indices[idx] - idx + 1:]
    return sequences
