# 模拟随机化信道
# 思路: 参数1  所有的信息序列strs n   参数2:平均生成多少个子序列k  参数3:平均每个生成的序列删除多少个元素t
# 总共生成n*k个序列，把n*k分成随机的n份，其中每一个数组就代表对应index的序列生成多少个；
# 总共发生n*k*t个删除,把这n*k*t个删除分成n*k份，每一份允许有0出现(代表对应序列中不发生删除)
# 对于每个序列生成多少个，每个具体删除几个都已经确定了，接下来就是随机生成对应个数的位置，然后进行删除

import random
import math
# 把sum分成n份，并且这n份相加之和为k
def split_integer(sum, n):
    if n <= 0 or sum <= 0:
        raise ValueError("k and n must be positive integers.")
    # 随机生成n-1个分割点(随机生成)
    splits = sorted(random.choices(range(1, sum),k = n - 1))
    # 计算每个部分的值
    parts = [splits[0]] + [splits[i] - splits[i - 1] for i in range(1, n-1)] + [sum - splits[-1]]
    return parts


def random_channel(sequences,average_clutser_size,average_del_cnt):
    origin_sequence_cnt = len(sequences)
    total_sequence_cnt = origin_sequence_cnt * average_clutser_size
    total_del_cnt = total_sequence_cnt * average_del_cnt
    if(len(sequences)==1):
        clusters_size_list=[]
        clusters_size_list.append(average_clutser_size)
    else:
        clusters_size_list = split_integer(total_sequence_cnt,origin_sequence_cnt)
    del_cnt_list = split_integer(total_del_cnt,total_sequence_cnt)

    # print("每个cluster的大小:" ,clusters_size_list)
    # print("每个序列的删除数目:",del_cnt_list)
    # clusters_size_list=[]
    # for i in range(0,len(sequences)):
    #     clusters_size_list.append(average_clutser_size)
    result_sequences = []
    #构造所有的序列
    for i in range(0,origin_sequence_cnt):
        result_sequences += [sequences[i]]* clusters_size_list[i]


    # #对每个序列进行删除
    for i in range(0,len(del_cnt_list)):
        del_index = sorted(random.sample(range(0,len(result_sequences[i])),del_cnt_list[i]))
        for idx in range(0,del_cnt_list[i]):
            result_sequences[i] = result_sequences[i][:del_index[idx]-idx]+result_sequences[i][del_index[idx]-idx+1:]

    # 组织成二维列表
    clusters = []
    idx=0
    for i in range(0,len(clusters_size_list)):
        clusters.append(result_sequences[idx:idx+clusters_size_list[i]])
        idx+=clusters_size_list[i]

    return clusters


def random_channel_Probabilistic(sequences,average_clutser_size,lossRateCluster,lossRateBase):
    OriginSequenceCnt = len(sequences)
    TotalSequenceCnt = OriginSequenceCnt * average_clutser_size

    LossClusterSize = math.floor(lossRateCluster * OriginSequenceCnt)
    RemainClusterSize = OriginSequenceCnt - LossClusterSize
    print("random_channel_Probabilistic:簇丢失数目为",LossClusterSize)
    # 选出丢失的簇的下标,在这些位置插入0
    LossClusterIndex = sorted(random.sample(range(0, TotalSequenceCnt), LossClusterSize))
    # 未丢失的簇的大小
    splits = sorted(random.sample(range(0, TotalSequenceCnt-1), RemainClusterSize-1))
    ClustersSizeList = [splits[0]] + [splits[i] - splits[i - 1] for i in range(1, RemainClusterSize - 1)] + [TotalSequenceCnt - splits[-1]]

    for idx in LossClusterIndex:
        ClustersSizeList.insert(idx,0)

    ResultSequences = []
    # 构造所有的序列
    for i in range(0,OriginSequenceCnt):
        ResultSequences += [sequences[i]]* ClustersSizeList[i]

    RemainRate = 1-lossRateBase
    # 对所有的序列进行随机删除
    for i in range(0,len(ResultSequences)):
        sequence = ResultSequences[i]
        ResultSequences[i] = ''.join([c for c in sequence if random.random() <= RemainRate])

    # 组织成二维列表
    clusters = []
    idx=0
    for i in range(0,len(ClustersSizeList)):
        clusters.append(ResultSequences[idx:idx+ClustersSizeList[i]])
        idx+=ClustersSizeList[i]

    return clusters

#
# a=['ABSHASGAHSSX','AXSGSHWYCS','AAAAAAAACSSA','ASASASASAAZZA']
# print(random_channel_Probabilistic(a,5,0.05,0.5))