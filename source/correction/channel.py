import random


def split_integer(sum, n):
    if n <= 0 or sum <= 0:
        raise ValueError("k and n must be positive integers.")
    # 随机生成n-1个分割点(随机生成)
    splits = sorted(random.choices(range(1, sum), k=n - 1))
    # 计算每个部分的值
    parts = [splits[0]] + [splits[i] - splits[i - 1] for i in range(1, n - 1)] + [sum - splits[-1]]
    return parts


def random_channel_Probabilistic(sequences, lossRateBase):
    print("开始通过删除信道")
    RemainRate = 1 - lossRateBase
    # 对所有的序列进行随机删除
    original_length = len(sequences[0])
    del_cnt_list = []
    for i in range(0, len(sequences)):
        tmp_sequence = sequences[i]
        sequences[i] = ''.join([c for c in tmp_sequence if random.random() <= RemainRate])  # 对每个符号进行随机删除
        del_cnt_list.append(original_length - len(sequences[i]))
    # print("每个序列的删除数目:", del_cnt_list)
    # print("删除数目为2的序列数:", del_cnt_list.count(2))
    # count_greater_than_1 = len([num for num in del_cnt_list if num > 2])  # 统计大于2的元素数量
    # print("删除数目为大于2的序列数:", count_greater_than_1)
    # 组织成二维列表
    print("删除信道结束")
    return sequences


def deletion_channel_random(sequences, average_del_cnt):
    total_sequence_cnt = len(sequences)
    print("所有的序列数", total_sequence_cnt)
    total_del_cnt = total_sequence_cnt * average_del_cnt
    del_cnt_list = split_integer(total_del_cnt, total_sequence_cnt)
    print("每个序列的删除数目:", del_cnt_list)
    print("删除数目为2的序列数:", del_cnt_list.count(2))
    count_greater_than_1 = len([num for num in del_cnt_list if num > 2])  # 统计大于2的元素数量
    print("删除数目为大于2的序列数:", count_greater_than_1)
    for i in range(0, len(del_cnt_list)):
        del_index = sorted(random.sample(range(0, len(sequences[i])), del_cnt_list[i]))
        for idx in range(0, del_cnt_list[i]):
            sequences[i] = sequences[i][:del_index[idx] - idx] + sequences[i][
                                                                 del_index[idx] - idx + 1:]
    return sequences


def deletion_channel_at_index(sequences, deleted_indices):
    deleted_indices = sorted(deleted_indices)
    for i in range(len(sequences)):
        for idx in range(len(deleted_indices)):
            sequences[i] = sequences[i][:deleted_indices[idx] - idx] + sequences[i][deleted_indices[idx] - idx + 1:]
    return sequences
