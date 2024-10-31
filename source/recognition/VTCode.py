# 输入数据是57*4+3长的【碱基】序列的列表，需要列表中的每个序列进行VT编码
# 具体步骤为对每个57长的segments分别进行VT编码
# 返回值应该是  【63*4+3长】的【碱基序列】构成的列表
def VTCodeEncodeSequences(inputsequences,delimiterChar):
    print("VTCodeEncodeSequences:为每个序列的segment分别进行VT编码")
    resultsequences = []
    for sequence in inputsequences:
        str=''.join(AGCT_VTencode(segment) + delimiterChar for segment in sequence.split(delimiterChar))
        str=str[:-1]
        resultsequences.append(str)
    return resultsequences

from Config import Dprint
import random
import numpy as np
from Config import VT_M,VT_SYNDROME,VT_CODE_LEN,VT_REDANDANT

baseMap={
    'A': '00',
    'C': '01',
    'G': '10',
    'T': '11',
    }
binaryMap={
    '00':'A',
    '01':'C',
    '10':'G',
    '11':'T',
}

def base_to_binary(baseSeq):
    binary_sequence = ''.join(baseMap[base] for base in baseSeq if base in baseMap)
    odd_indexed_elements = [binary_sequence[i] for i in range(len(binary_sequence)) if i % 2 != 0]
    even_indexed_elements = [binary_sequence[i] for i in range(len(binary_sequence)) if i % 2 == 0]
    return [''.join(even_indexed_elements),''.join(odd_indexed_elements)]

def binary_to_bases(binary_list):
    seq1 = binary_list[0]
    seq2 = binary_list[1]
    if len(seq1) != len(seq2):
        raise ValueError("两个序列的长度必须相同。")

    merged_sequence = ''.join([str(val) for pair in zip(seq1, seq2) for val in pair])
    base_sequence = ''.join(binaryMap[merged_sequence[i:i + 2]] for i in range(0, len(merged_sequence), 2))
    return base_sequence

def _compute_syndrome(m:64, SYN ,array_y):
    len_y=array_y.size
    return np.mod(SYN - np.sum((1+np.arange(len_y))*array_y),m)


def _is_codeword(y):
    if y is None or y.size!=VT_CODE_LEN:
        return False
    return _compute_syndrome(VT_M,VT_SYNDROME,y)==0

def _remove_redundant_bits(array_x):
    parity_positions = np.zeros(VT_REDANDANT, dtype=np.int64)
    for i in range(VT_REDANDANT):
        parity_positions[i] = np.power(2, i)
    codeword_str = ''
    for i in range(len(array_x)):
        if i+1 not in parity_positions:
            codeword_str += str(array_x[i])
    return codeword_str

def _remove_redundant_base(baseSeq):
    baseSeq= np.array(list(baseSeq))
    parity_positions = np.zeros(VT_REDANDANT, dtype=np.int64)
    for i in range(VT_REDANDANT):
        parity_positions[i] = np.power(2, i)
    codeword_str = ''
    for i in range(len(baseSeq)):
        if i + 1 not in parity_positions:
            codeword_str += str(baseSeq[i])
    return codeword_str

#57长input  63长output
def vt_encode(message):
    x=np.array(list(message), dtype=np.int64)
    #消息长度57？冗余位6
    parity_positions = np.zeros(VT_REDANDANT,dtype=np.int64)
    for i in range(VT_REDANDANT):
        parity_positions[i] = np.power(2, i)
    systematic_positions = np.setdiff1d(np.arange(1, VT_CODE_LEN + 1), parity_positions)
    #print(systematic_positions)
    #print(parity_positions)
    y = np.zeros(VT_CODE_LEN, dtype=np.int64)
    # first set systematic positions
    y[systematic_positions - 1] = x
    syn=_compute_syndrome(VT_M,VT_SYNDROME,y)
    if syn != 0:
        for pos in reversed(parity_positions):
            if syn >= pos:
                y[pos - 1] = 1
                syn -= pos
                if syn == 0:
                    break
    assert _is_codeword(y)
    return  ''.join(y.astype(str))
def vt_errorCorrection(codeword):
    '''
    y:n-1 length
    a:VT syndrome,default 0
    return codeword x with length n
    '''
    assert len(codeword)==VT_CODE_LEN-1
    # 转换为 NumPy 数组，每位一个
    array_y = np.array(list(codeword), dtype=np.int64)
    sum_of_ones=np.sum(array_y) #omega
    checksum=_compute_syndrome(VT_M,VT_SYNDROME,array_y)
    array_x=array_y
    if checksum<=sum_of_ones: #说明被删除的是0
        #从右往左数 R1 个 1的地方插入0
        R_1=checksum
        if R_1==0:
            array_x=np.append(array_x,0)
        elif R_1!=0:
            ones_indices = np.where(array_x == 1)[0]  # 1的位置
            #print(ones_indices)
            insert_ind = ones_indices[-R_1]  # 要插入在它的前面
            #print(insert_ind)
            array_x = np.insert(array_x, insert_ind, 0)
            pass
    elif checksum>sum_of_ones:  #说明被删除的是1
        # 从左往右L0个0的地方插入1
        L_0=checksum-1-sum_of_ones
        zeros_indices = np.where(array_x == 0)[0]
        #if L_0>=len(zeros_indices): return
        if L_0 == 0:
            array_x = np.insert(array_x, 0, 1)
        else:
            insert_ind = zeros_indices[L_0-1]
            array_x = np.insert(array_x, insert_ind+1, 1)  # L_0 个 0之后插入一个1
    return array_x

def vt_decode(codeword):
    return _remove_redundant_bits(vt_errorCorrection(codeword))

# Input:碱基序列 57长
# Output:碱基序列 63长
def AGCT_VTencode(bases_seq):
    binary_list=base_to_binary(bases_seq)
    encoded=[]
    for item in binary_list:
        encoded.append(vt_encode(item))
    return binary_to_bases(encoded)

# Input:碱基序列  63长
# Output:碱基序列  57长
def AGCT_VTdecode(bases_seq):
    binary_list = base_to_binary(bases_seq)
    decoded = []
    for item in binary_list:
        decoded.append(vt_decode(item))
    return binary_to_bases(decoded)

#先把cluster分一分喽
def divide_cluster(cluster):
    del_0_list=[]
    del_1_list=[]
    del_2_list=[]
    for item in cluster : #太短的也处理不了
        if(len(item)==VT_CODE_LEN): del_0_list.append(item)
        if (len(item) == VT_CODE_LEN-1):del_1_list.append(item)
        if (len(item) == VT_CODE_LEN-2): del_2_list.append(item)
    return [del_0_list,del_1_list,del_2_list]


# def insert_one_bit(binary_str):
#     # 用于存储所有不同的序列
#     unique_sequences = set()
#     # 遍历每个可能的插入位置
#     for i in range(len(binary_str) + 1):
#         # 创建新的序列，将比特插入到当前位置
#         new_sequence0 = binary_str[:i] + "0" + binary_str[i:]
#         unique_sequences.add(new_sequence0)
#         new_sequence1 = binary_str[:i] + "1" + binary_str[i:]
#         unique_sequences.add(new_sequence1)  # 添加到集合中以确保唯一性
#     return list(unique_sequences)  # 转换为列表返回

# def vt_2_decode(cluster):
#     #尝试插入一个bit,不可以这样直接插入
#     list_decoding=set()
#     for item in cluster:
#         insert_ont_bit=insert_one_bit(item)
#         bucket = []
#         for seq in insert_ont_bit:
#             if(vt_decode(seq) is not None):
#                 bucket.append(vt_decode(seq)) #所有插入一个之后可能得到的码字吧，还需要求个交集喽
#         if len(list_decoding) == 0:
#             list_decoding.update(bucket)
#         else :
#             bucket=set(bucket)
#             list_decoding=list_decoding.intersection(bucket)
#     print("len")
#     print(len(list_decoding))
#     if len(list_decoding)==1:
#         return True,list_decoding.pop()
#     elif len(list_decoding)>1:
#         return False, list_decoding.pop()

def CheckdiffCnt(Seq,TargetSeq):
    idxTarget=0
    Cnt=0
    for idx in range(0,len(Seq)):
        if(Seq[idx]==TargetSeq[idxTarget]):
            idxTarget+=1
        else:
            Cnt+=1
    return Cnt==2


def two_del_01_VT_Reconstruction(cluster):
    cluster = list(set(cluster))
    del_1_list = []
    seqCnt = min(len(cluster),7)
    for idx in range(0,len(cluster[0])):
        zeroCnt = 0
        for seqIdx in range(seqCnt):
            if(cluster[seqIdx][idx]=='0'):
                zeroCnt+=1
        if(zeroCnt == 0  or zeroCnt==seqCnt):
            continue
        else:
            for seqIdx in range(seqCnt):
                list_str = list(cluster[seqIdx])
                list_str.insert(idx, "1" if cluster[seqIdx][idx] == '0' else "0" )
                del_1_list.append(''.join(list_str))

    # VT解码
    vt_list = []
    for seq in del_1_list:
        vtSeq = vt_errorCorrection(seq)
        if(vtSeq is not None):
            vt_list.append(vtSeq)

    # 判断结果序列中哪个符合要求(即能够生成cluster中的所有序列)
    for vt_seq in vt_list:
        result = all(CheckdiffCnt(vt_seq,origin_seq) for origin_seq in cluster)
        if(result):
            return seqCnt>=7,vt_seq
    return False,vt_list[0] if len(vt_list)>0 else cluster[0]+'0'*2



def two_del_ACGT_VT_Reconstruction(dele_2_list):
    #把list里面的碱基序列，一拆二分别存，分别求译码之后的交集，然后return
    cluster1=[]
    cluster2=[]
    for item in dele_2_list:
        binaryList=base_to_binary(item)
        cluster1.append(binaryList[0])
        cluster2.append(binaryList[1])
    flag1,dSeq1=two_del_01_VT_Reconstruction(cluster1)
    flag2, dSeq2 = two_del_01_VT_Reconstruction(cluster2)
    binarycode=[dSeq1,dSeq2]
    return flag2 and flag1, binary_to_bases(binarycode)



#可能是63长的，可能是62长的，可能是61长的吧
#希望cluster是一个集合，去重
def reconstrection(cluster):
    DelClusterClass = divide_cluster(cluster)
    del_0_list=DelClusterClass[0]
    del_1_list = DelClusterClass[1]
    del_2_list = DelClusterClass[2]
    #有未被删除的,只需要去除冗余
    if len(del_0_list)!=0:
        Dprint('VTCode.reconstrection : Case 1',del_0_list[0],len(del_0_list[0]))
        return True, _remove_redundant_base(del_0_list[0])
    elif len(del_1_list)!=0:
        Dprint('VTCode.reconstrection : Case 2', del_1_list[0], len(del_1_list[0]))
        return True,AGCT_VTdecode(del_1_list[0])
    elif len(del_2_list)!=0:
        success,res =two_del_ACGT_VT_Reconstruction(del_2_list)
        Dprint('VTCode.reconstrection : Case 3',_remove_redundant_base(res))
        return success, _remove_redundant_base(res)
    else: #无法处理的情况:删除的个数都大于等于3 => 直接选择第一个补充为63长 然后取出冗余位
        Dprint('VTCode.reconstrection : Case 4',_remove_redundant_base(cluster[0]+('A'*(VT_CODE_LEN-len(cluster[0])))))
        return False,_remove_redundant_base(cluster[0]+("A"*(VT_CODE_LEN-len(cluster[0]))))

if __name__=="__main__":
    cluster=[
             ]
    #print(len("ACGCCGGCGTCGACTTAGCAGCTAAAGCTAAACTACAGAGCTGTCGATTAGCTTTTTTACG"))
    flag,seq=reconstrection(cluster)
    print(flag)
    print(seq)
    #原始57长碱基序列
    #bases="AGCTACGTCGATTAGCAGCTACGTCGATTAGCAGCTACGTCGATTAGCTTTTTTTTT"
    # print(len(bases))
    # vt_encoded_AGCT=AGCT_encode(bases) #ATATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGCTTTTTTTTT
    # cluster=["ATATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGAGCTACGTCGATTAGCTTTTTTTTT","ATATGCTTACGTGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGCTTTTTTTTT","ATATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGCTTTTTTT","ATATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGTTTTTTTT"]
    # "ATATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGCTTTTTTTTT",
    # print(reconstrection(cluster))
    # print(bases)
    #dele2list0=["ATATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGCTTTTTTT"]
    #dele2list =["ATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGCTTTTTTTTT","ATATGCTTACGTCGATTTAGCAGCTACGTCGAATTAGCAGCTACGTCGATTAGTTTTTTTT"]

    #print(len(dele2list0))
    #flag, recons=two_del_VT_reconstruction(dele2list0)
    #print(flag) #false 不一定是真的false,true 一定是真的true
    #print(recons)
    #print(bases)

    # seq1="0101101100110101110100101001101001101001010011010110101111111"
    # seq2="0101101100110101110100101001101001101001010011010110111111111"
    # seq3="01011011001101011101001010011010011010010100110101101011111111"
    # seq4="01011011001101011101001010011010011010010100110101101101111111"
    # print(vt_decode(seq4))

    # for item in dele2list:
    #     print(len(item))
    #print(len(vt_encoded_AGCT))
    # bases="AGCTACGTCGATTAGCAGCTACGTCGATTAGCAGCTACGTCGATTAGCTTTTTTTTT"
    # print(bases)
    # print(AGCT_encode(bases))
    # print(len(bases))


