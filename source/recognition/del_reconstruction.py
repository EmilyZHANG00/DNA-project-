from collections import defaultdict
# 序列按照分隔符进行分段,把一个簇分成4个簇
def segmentation(cluster,delimiter='M',chunk_size=57):
    # 去重
    cluster = list(set(cluster))
    segmentClusters = [[] for _ in range(4)]
    for seq in cluster:
        segment = ''
        clusteridx = 0
        lastisdelimiter = True  # 记录上一次分段是不是由于碰到了分隔符才分段
        for i in range(len(seq) + 1):
            if i == len(seq) or seq[i] == delimiter:
                if (lastisdelimiter):
                    segmentClusters[clusteridx].append(segment)
                segment = ''
                lastisdelimiter = True
                clusteridx += 1
            elif len(segment) == chunk_size:  # 此时长度已经到了应该分割的长度但是并没有如期遇到分隔符，所以此时直接开始一个新的段，并且这个时候是不放入cluster的
                segment = seq[i]
                clusteridx += 1
                lastisdelimiter = False
            else:
                segment += seq[i]
    return segmentClusters



def fullspaceReconstruction(cluster,Target_LEN):
    # 去重
    cluster = list(set(cluster))
    success = False;

    valid_cnt = 0
    for idx in range(0,len(cluster)):
        seq=cluster[idx]
        if(len(seq)==Target_LEN):
            return seq,True
        if(len(seq)>=Target_LEN-1):
            valid_cnt+=1
        seq+= 'A'*(Target_LEN-len(seq))
        cluster[idx]=seq
    char_count = defaultdict(lambda: defaultdict(int))
    for seq in cluster:
        # 遍历字符串的每个字符及其索引
        for index, char in enumerate(seq):
            char_count[index][char] += 1

    # 构建结果字符串
    most_frequent_str = ""
    for index in range(0,Target_LEN-1):
        # 对于每个位置，找到出现次数最多的字符
        max_char = max(char_count[index], key=char_count[index].get)
        most_frequent_str += max_char
    return most_frequent_str,success


# 真正实现从一个簇中重构出一个序列，这里序列为碱基序列，重构后长度应该为63
def VTReconstruction(cluster,Target_LEN):
    # 去重
    result_seq=''
    success = False;

    return result_seq,success


def Reconstruction(cluster,VTCode,delimiter='M',chunk_size=57):
    # 序列分段
    segmentClusters = segmentation(cluster,delimiter,chunk_size)

    # 对四个cluster分别进行重构并组合重构后的结果
    ansseq = ''
    successcnt = 0
    for i in range(4):
        if (len(segmentClusters[i]) == 0):
            segment = 'A' * chunk_size
            flag = False;
        else:
            if(VTCode):
                segment, flag = VTReconstruction(segmentClusters[i], chunk_size)
            else:
                segment, flag = fullspaceReconstruction(segmentClusters[i], chunk_size)
        if (flag):
            successcnt += 1
        ansseq += segment
    return ansseq, successcnt == 4


def recons_success_rate(origin_seqs,recons_seqs,delimiterChar='M'):
    success_cnt = 0
    for i in range(0,len(origin_seqs)):
        str = ''
        for ll in range(0,len(origin_seqs[i])):
            if origin_seqs[i][ll]!=delimiterChar:
                str+=origin_seqs[i][ll]
        if(str==recons_seqs[i]):
            success_cnt+=1
    return success_cnt / len(origin_seqs)