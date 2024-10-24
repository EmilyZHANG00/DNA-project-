from collections import defaultdict
import VTCode
from Config import  FilePrint,Dprint
# 序列按照分隔符进行分段 , 把一个簇分成4个簇
def segmentation(cluster,TargetLen,delimiter='M'):
    # 去重
    cluster = list(set(cluster))
    segmentClusters = [[] for _ in range(4)]
    for seq in cluster:
        segment = ''
        clusteridx = 0
        lastisdelimiter = True  #记录上一次分段是不是由于碰到了分隔符才分段
        for i in range(len(seq) + 1):
            if i == len(seq) or seq[i] == delimiter:
                if (lastisdelimiter):
                    segmentClusters[clusteridx].append(segment)
                segment = ''
                lastisdelimiter = True
                clusteridx += 1
            elif len(segment) == TargetLen:  # 此时长度已经到了应该分割的长度但是并没有如期遇到分隔符，所以此时直接开始一个新的段，并且这个时候是不放入cluster的
                segment = seq[i]
                clusteridx += 1
                lastisdelimiter = False
            else:
                segment += seq[i]
    return segmentClusters


# 多位对比
def fullspaceReconstruction(cluster,Target_LEN):
    # 去重
    cluster = list(set(cluster))

    DEL_1_SEQS = []
    for idx in range(0,len(cluster)):
        seq=cluster[idx]
        if(len(seq) == Target_LEN):
            return seq,True
        if(len(seq) >= Target_LEN-1):
            DEL_1_SEQS.append(seq)
        seq+= 'A'*(Target_LEN-len(seq))
        cluster[idx]=seq

    res=""
    if(len(DEL_1_SEQS)>=3):
        for idx in range(0,Target_LEN-1):
            if(DEL_1_SEQS[0][idx] == DEL_1_SEQS[1][idx] and  DEL_1_SEQS[1][idx] ==  DEL_1_SEQS[2][idx]):
                res+=DEL_1_SEQS[0][idx]
            elif(DEL_1_SEQS[0][idx] == DEL_1_SEQS[1][idx]):
                res += DEL_1_SEQS[0][idx]
                res += DEL_1_SEQS[2][idx:]
                return res, True;
            elif (DEL_1_SEQS[0][idx] == DEL_1_SEQS[2][idx]):
                res += DEL_1_SEQS[0][idx]
                res += DEL_1_SEQS[1][idx:]
                return res, True;
            elif (DEL_1_SEQS[1][idx] == DEL_1_SEQS[2][idx]):
                res += DEL_1_SEQS[1][idx]
                res += DEL_1_SEQS[0][idx:]
                return res, True;

    char_count = defaultdict(lambda: defaultdict(int))
    for seq in cluster:
        # 遍历字符串的每个字符及其索引
        for index, char in enumerate(seq):
            char_count[index][char] += 1

    # 构建结果字符串
    most_frequent_str = ""
    for index in range(0,Target_LEN):
        # 对于每个位置，找到出现次数最多的字符
        max_char = max(char_count[index], key=char_count[index].get)
        most_frequent_str += max_char

    try:
        if len(most_frequent_str) != Target_LEN:
            raise ValueError(f"重构后序列长度不满足要求!")
    except ValueError as e:
        print("Error", e)
        return -1
    return most_frequent_str,False


# 真正实现从一个簇中重构出一个序列，这里序列为碱基序列，重构后长度应该为63
def VTReconstruction(cluster,TargetLen):
    # 去重
    success,result_seq = VTCode.reconstrection(cluster)
    try:
        if (len(result_seq) != TargetLen):
            raise ValueError(f"序列长度不是{TargetLen} :{result_seq},{len(result_seq)}")
    except ValueError as e:
        print("Error", e)
        return -1
    return result_seq,success


def ReconstructionNoSegs(cluster,VTCodeEncode,TargetLen=228):
    if (VTCodeEncode):
        Seq, Success = VTReconstruction(cluster, TargetLen)
    else:
        Seq, Success = fullspaceReconstruction(cluster, TargetLen)

    try:
        if (len(Seq) != TargetLen):
            raise ValueError(f"序列长度不是{TargetLen} :{Seq},{len(Seq)}")
    except ValueError as e:
        print("Error", e)
        return -1

    return Seq, Success

def ReconstructionSegs(cluster,VTCodeEncode,TargetLen,SegmentLen,delimiter='M'):
    # 序列分段
    if(VTCodeEncode):
        segmentClusters = segmentation(cluster,SegmentLen+VTCode.VT_REDANDANT,delimiter)
    else:
        segmentClusters = segmentation(cluster, SegmentLen, delimiter)
    # 对四个cluster分别进行重构并组合重构后的结果
    ansseq = ''
    successcnt = 0
    for i in range(4):
        if (len(segmentClusters[i]) == 0):
            segment = 'A' * SegmentLen
            flag = False;
        else:
            if(VTCodeEncode):
                segment, flag = VTReconstruction(segmentClusters[i], SegmentLen)
            else:
                segment, flag = fullspaceReconstruction(segmentClusters[i], SegmentLen)
        if (flag):
            successcnt += 1
        ansseq += segment
    try:
        if(len(ansseq)!=TargetLen):
                raise ValueError(f"序列长度不是{TargetLen} :{ansseq},{len(ansseq)}")
    except ValueError as e:
        print("Error", e)
        return -1
    return ansseq, successcnt == 4



def Reconstruction(cluster,Artificial,VTCodeEncode,TaegetLen,SegmentLen,delimiter):
    if(Artificial):
        ansseq, success = ReconstructionSegs(cluster,VTCodeEncode,TaegetLen,SegmentLen,delimiter)
    else:
        ansseq, success = ReconstructionNoSegs(cluster, VTCodeEncode, TaegetLen)
    return ansseq, success


def recons_success_rate(origin_seqs,recons_seqs,delimiterChar='M'):
    success_cnt = 0
    outputinfo=''
    for i in range(0,len(origin_seqs)):
        str = ''
        for ll in range(0,len(origin_seqs[i])):
            if origin_seqs[i][ll]!=delimiterChar:
                str+=origin_seqs[i][ll]
        if(str==recons_seqs[i]):
            success_cnt+=1
        # else:
        #     outputinfo += "recons_success_rate: Reconstruction failed!"+str+','+recons_seqs[i]+"\n"
        #     Dprint("recons_success_rate: Reconstruction failed!",str,len(str),recons_seqs[i],len(recons_seqs[i]))
        # FilePrint(outputinfo)
    return success_cnt / len(origin_seqs)