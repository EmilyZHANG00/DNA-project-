import recognition.data_transfer as data_transfer
from recognition.data_transfer import CLUSTER_SIZE,DEL_NUM,CHUNK_SIZE,delimiterChar
import recognition.channel as channel
import recognition.del_reconstruction as RECONS
from recognition.del_reconstruction import recons_success_rate
from recognition.VTCode import VTCodeEncodeSequences
from recognition.VTCode import VTCodeDecodeSequences



origin_text = "DNA存储与传统的存储介质不同，DNA存储技术有如下显著优势："
            # "1)DNA存储密度高。一个DNA分子可以保留一个物种的全部遗传信息，最大的人类染色体含有近2.5亿个碱基对，那么就意味着一条和人手差不多长的DNA链，"\
            # "就可以存储1EB（1EB=10.74亿G）数据。与硬盘和闪存的数据存储密度相比，硬盘存储每立方厘米约为1013位，闪存存储约为1016位，"\
            # "而DNA存储的密度约为1019位。2）DNA分子存储具有稳定性。" \
            # "今年2月，国际顶级学术期刊Nature上的一篇论文称古生物学家在西伯利亚东北部的永久冻土层中提取到距今120万年猛犸象的遗传物质，" \
            # "并对其DNA进行了解析，这也进一步刷新了DNA分子的保存年代纪录。据悉，DNA至少可保留上百年的数据，相比之下，硬盘、磁带的数据最多只能保留约10年。" \
            # "3）DNA存储维护成本低。以DNA形式存储的数据易于维护，和传统的数据中心不同，不需要大量的人力、财力投入，仅需要保存在低温环境中。" \
            # "在能耗方面,1GB的数据硬盘存储能耗约为0.04W,而DNA存储的能耗则小于10-10W。"



# VTCode作为参数，记录是否进行VT编码
def textTest_Reconstruction(VTCode=False):
    total_length = CHUNK_SIZE * 4 + 3
    # 1.encodeFromText转换为碱基序列
    origin_acgt_seqs,origin_seq_cnt = data_transfer.encodeFromText(origin_text)
    # 2.进行VT编码(可选)
    if(VTCode):
        total_length +=  6*4
        origin_acgt_seqs = VTCodeEncodeSequences(origin_acgt_seqs)   #进行VT编码

    # 3.random_channel进行随机删除
    clusters = channel.random_channel(origin_acgt_seqs,CLUSTER_SIZE,DEL_NUM)

    # 4.序列重构
    recon_ACGT_seqs=[]
    for clu in clusters:
        if(len(clu)==0):
            # 补充为全0
            recon_ACGT_seqs.append('A'*total_length)
            continue
        rec_seq ,success = RECONS.Reconstruction(clu,VTCode)
        recon_ACGT_seqs.append(rec_seq)

    #5.VT码解码(可选)
    if(VTCode):
        origin_acgt_seqs = VTCodeDecodeSequences(recon_ACGT_seqs)
    print("序列重构成功率为:",recons_success_rate(origin_acgt_seqs,recon_ACGT_seqs,delimiterChar))


    #6.恢复原数据内容
    data_transfer.decodeToText(recon_ACGT_seqs, origin_seq_cnt, CHUNK_SIZE)


def imageTest_Reconstruction(VTCode=False):
    print("imageTest_Reconstruction未实现")

textTest_Reconstruction(False)
imageTest_Reconstruction(False)