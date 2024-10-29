# import os.path
# import sys
# sys.path.append("recognition")
# from recognition.Config import CLUSTER_SIZE,CHUNK_SIZE,SEGMENT_LEN,delimiterChar,BASE_LOSS_RATE,CLUSTER_LOSS_RATE,VT_CODE_LEN,VT_REDANDANT,RS_NUMBER
# #from recognition.data_transfer import encodeFromImage,encodeFromText,decodeToImage,decodeToText,compare_and_save_images
# import recognition.data_transfer as data_transfer
# import recognition.channel as channel
# import recognition.del_reconstruction as RECONS
# from recognition.del_reconstruction import recons_success_rate
# import recognition.VTCode as VTCode
# import time
#
# origin_text = "DNA存储与传统的存储介质不同，DNA存储技术有如下显著优势：" \
#             "1)DNA存储密度高。一个DNA分子可以保留一个物种的全部遗传信息，最大的人类染色体含有近2.5亿个碱基对，那么就意味着一条和人手差不多长的DNA链，"\
#             "就可以存储1EB（1EB=10.74亿G）数据。与硬盘和闪存的数据存储密度相比，硬盘存储每立方厘米约为1013位，闪存存储约为1016位，"\
#             "而DNA存储的密度约为1019位。2）DNA分子存储具有稳定性。" \
#             "今年2月，国际顶级学术期刊Nature上的一篇论文称古生物学家在西伯利亚东北部的永久冻土层中提取到距今120万年猛犸象的遗传物质，" \
#             "并对其DNA进行了解析，这也进一步刷新了DNA分子的保存年代纪录。据悉，DNA至少可保留上百年的数据，相比之下，硬盘、磁带的数据最多只能保留约10年。" \
#             "3）DNA存储维护成本低。以DNA形式存储的数据易于维护，和传统的数据中心不同，不需要大量的人力、财力投入，仅需要保存在低温环境中。" \
#             "在能耗方面,1GB的数据硬盘存储能耗约为0.04W,而DNA存储的能耗则小于10-10W。"
#
# image_path = '../data/testA.jpg'  # 替换为你的图片路径
# output_path = '../data/output_image.jpg'  # 替换为输出图片的路径
# diff_image_dir = '../result/testA/10-25-01'  # 替换为差异图片的保存路径
#
# video_path = '../data/test3.mp4'
# output_video_dir = '../result/Video/10-25-01'
# # VTCode作为参数，记录是否进行VT编码
# def textTest_Reconstruction(Artificial=True,VTCodeEncode=False):
#     total_length = CHUNK_SIZE * 4    # 无论是否进行分段orVT编码，并不影响最终序列重构结果的对应长度
#     global SEGMENT_LEN
#     if (Artificial is False):
#         SEGMENT_LEN = CHUNK_SIZE * 4
#     else:
#         SEGMENT_LEN = CHUNK_SIZE
#     # 1.encodeFromText转换为碱基序列
#     origin_acgt_seqs,origin_seq_cnt = data_transfer.encodeFromText(origin_text,CHUNK_SIZE,SEGMENT_LEN)
#     encoding_acgt_seqs = origin_acgt_seqs
#     # 2.进行VT编码(可选)
#     if(VTCodeEncode):
#         encoding_acgt_seqs = VTCode.VTCodeEncodeSequences(origin_acgt_seqs,delimiterChar)   #进行VT编码
#     # 3.random_channel进行随机删除
#     #clusters = channel.random_channel(origin_acgt_seqs,CLUSTER_SIZE,DEL_NUM)
#     clusters = channel.random_channel_Probabilistic(encoding_acgt_seqs,CLUSTER_SIZE,CLUSTER_LOSS_RATE,BASE_LOSS_RATE)
#
#     # 4.序列重构
#     recon_ACGT_seqs=[]
#     for clu in clusters:
#         if(len(clu)==0):
#             # 补充为全0
#             recon_ACGT_seqs.append('A'*total_length)
#             continue
#         rec_seq ,success = RECONS.Reconstruction(clu,Artificial,VTCodeEncode,total_length,SEGMENT_LEN,delimiterChar)
#         recon_ACGT_seqs.append(rec_seq)
#
#     print("序列重构成功率为:",recons_success_rate(origin_acgt_seqs,recon_ACGT_seqs,delimiterChar))
#
#     # 验证序列长度是否等于 CHUNK_SIZE * 4
#     try:
#         for seq in origin_acgt_seqs:
#             if len(seq) != CHUNK_SIZE * 4:
#                 raise ValueError(f"序列长度不是 {CHUNK_SIZE*4 }：{seq}")
#     except ValueError as e:
#         print(e)
#     #6.恢复原数据内容
#     data_transfer.decodeToText(recon_ACGT_seqs, origin_seq_cnt, CHUNK_SIZE)
#
#
# def imageTest_Reconstruction(Artificial=True,VTCodeEncode=False):
#     print(" \n ======================  NewTest  ===================== ")
#     total_length = CHUNK_SIZE *4    # 无论是否进行分段orVT编码，并不影响最终序列重构结果的对应长度
#     # 1.encodeFromText转换为碱基序列
#     global SEGMENT_LEN
#     if (Artificial is False):
#         SEGMENT_LEN = CHUNK_SIZE * 4
#     else:
#         SEGMENT_LEN = CHUNK_SIZE
#
#     startTime = time.time()
#     origin_acgt_seqs, n = data_transfer.encodeFromImage(image_path,CHUNK_SIZE,SEGMENT_LEN)
#     encoding_acgt_seqs = origin_acgt_seqs
#     print(f'### Image has been split into {len(origin_acgt_seqs)} chunks. cost time:',time.time()-startTime)
#
#     # 2.进行VT编码(可选)
#     if(VTCodeEncode):
#         startTime = time.time()
#         encoding_acgt_seqs = VTCode.VTCodeEncodeSequences(origin_acgt_seqs,delimiterChar)   #进行VT编码
#         print("### VT Encode cost time:", time.time() - startTime)
#
#     # 3.random_channel进行随机删除
#     startTime = time.time()
#     #clusters = channel.random_channel(origin_acgt_seqs,CLUSTER_SIZE,DEL_NUM)
#     clusters = channel.random_channel_Probabilistic(encoding_acgt_seqs,CLUSTER_SIZE,CLUSTER_LOSS_RATE,BASE_LOSS_RATE)
#     print("### random_channel cost time:", time.time() - startTime)
#
#
#     # 4.序列重构
#     startTime = time.time()
#     recon_ACGT_seqs=[]
#     for clu in clusters:
#         if(len(clu)==0):
#             # 补充为全0
#             recon_ACGT_seqs.append('A'*total_length)
#             continue
#         rec_seq ,success = RECONS.Reconstruction(clu,Artificial,VTCodeEncode,total_length,SEGMENT_LEN,delimiterChar)
#         recon_ACGT_seqs.append(rec_seq)
#     print("### Reconstruction cost time:", time.time() - startTime)
#     print("序列重构成功率为:",recons_success_rate(origin_acgt_seqs,recon_ACGT_seqs,delimiterChar))
#
#
#
#     # 6.恢复原数据内容
#     startTime = time.time()
#     data_transfer.decodeToImage(output_path, recon_ACGT_seqs, n,CHUNK_SIZE)
#     print(f'### Image has been combined and saved to {output_path},cost time :', time.time() - startTime)
#
#     k=0
#     k += 1 if(Artificial==True) else 0
#     k += 1 if (VTCodeEncode == True) else 0
#     # 检查文件夹是否存在
#     if not os.path.exists(diff_image_dir):
#         # 不存在则创建文件夹
#         os.makedirs(diff_image_dir)
#     outputimageName =  str(CLUSTER_LOSS_RATE)+'-'+ str( BASE_LOSS_RATE )+'-' +str(CLUSTER_SIZE)+'-'+str(RS_NUMBER) + '-' + str(k)+".jpg"
#     data_transfer.compare_and_save_images(image_path, output_path, os.path.join(diff_image_dir,outputimageName))
#
#
#
# def videoTest_Reconstruction(Artificial=True,VTCodeEncode=False):
#     print(" \n ======================  NewTest  ===================== ")
#     total_length = CHUNK_SIZE *4    # 无论是否进行分段orVT编码，并不影响最终序列重构结果的对应长度
#
#     # 1.encodeFromText转换为碱基序列
#     global SEGMENT_LEN
#     if (Artificial is False):
#         SEGMENT_LEN = CHUNK_SIZE * 4
#     else:
#         SEGMENT_LEN = CHUNK_SIZE
#
#     startTime = time.time()
#     origin_acgt_seqs, n = data_transfer.encodeFromVedio(video_path,CHUNK_SIZE,SEGMENT_LEN)
#     encoding_acgt_seqs = origin_acgt_seqs
#     print(f'### Vedio has been split into {len(origin_acgt_seqs)} chunks. cost time:',time.time()-startTime)
#
#     # 2.进行VT编码(可选)
#     if(VTCodeEncode):
#         startTime = startTime = time.time()
#         encoding_acgt_seqs = VTCode.VTCodeEncodeSequences(origin_acgt_seqs,delimiterChar)   #进行VT编码
#         print("### VT Encode cost time:",time.time()-startTime)
#
#     startTime = time.time()
#     # 3.random_channel进行随机删除
#     #clusters = channel.random_channel(origin_acgt_seqs,CLUSTER_SIZE,DEL_NUM)
#     clusters = channel.random_channel_Probabilistic(encoding_acgt_seqs,CLUSTER_SIZE,CLUSTER_LOSS_RATE,BASE_LOSS_RATE)
#     print("### random_channel cost time:", time.time() - startTime)
#
#     # 4.序列重构
#
#     startTime = time.time()
#     recon_ACGT_seqs=[]
#     for clu in clusters:
#         if(len(clu)==0):
#             # 补充为全0
#             recon_ACGT_seqs.append('A'*total_length)
#             continue
#         rec_seq ,success = RECONS.Reconstruction(clu,Artificial,VTCodeEncode,total_length,SEGMENT_LEN,delimiterChar)
#         recon_ACGT_seqs.append(rec_seq)
#     print("### Reconstruction cost time:", time.time() - startTime)
#     print("序列重构成功率为:",recons_success_rate(origin_acgt_seqs,recon_ACGT_seqs,delimiterChar))
#
#     k = 0
#     k += 1 if (Artificial == True) else 0
#     k += 1 if (VTCodeEncode == True) else 0
#     # 检查文件夹是否存在
#     if not os.path.exists(output_video_dir):
#         # 不存在则创建文件夹
#         os.makedirs(output_video_dir)
#     outputvideoName = str(CLUSTER_LOSS_RATE) + '-' + str(BASE_LOSS_RATE) + '-' + str(CLUSTER_SIZE) + '-' + str(
#         RS_NUMBER) + '-' + str(k) + ".mp4"
#
#     #recon_ACGT_seqs= origin_acgt_seqs
#
#     # 6.恢复原数据内容
#     startTime = time.time()
#     data_transfer.decodeToVedio(os.path.join(output_video_dir,outputvideoName), recon_ACGT_seqs, n,CHUNK_SIZE)
#     print(f'### video has been combined and saved to {outputvideoName},cost time :',time.time()-startTime)
#
#
#
#
# # textTest_Reconstruction(False)     # 不加分隔符
# # textTest_Reconstruction(True,False)      # 加人工碱基作为分隔符，全空间
# # textTest_Reconstruction(True,True)      # 人工碱基 + VT码
# #
# #
# # imageTest_Reconstruction(False)     # 不加分隔符
# # imageTest_Reconstruction(True,False)      # 加人工碱基作为分隔符，全空间
# # imageTest_Reconstruction(True,True)      # 人工碱基 + VT码
# #
# # videoTest_Reconstruction(False)
# # videoTest_Reconstruction(True,False)
# # videoTest_Reconstruction(True,True)



import os.path
import sys
sys.path.append("recognition")
from recognition.Config import CLUSTER_SIZE,CHUNK_SIZE,SEGMENT_LEN,delimiterChar,BASE_LOSS_RATE,CLUSTER_LOSS_RATE,VT_CODE_LEN,VT_REDANDANT,RS_NUMBER
#from recognition.data_transfer import encodeFromImage,encodeFromText,decodeToImage,decodeToText,compare_and_save_images
import recognition.data_transfer as data_transfer
import recognition.channel as channel
import recognition.del_reconstruction as RECONS
from recognition.del_reconstruction import recons_success_rate
import recognition.VTCode as VTCode
import time

originText = "DNA存储与传统的存储介质不同，DNA存储技术有如下显著优势：" \
            "1)DNA存储密度高。一个DNA分子可以保留一个物种的全部遗传信息，最大的人类染色体含有近2.5亿个碱基对，那么就意味着一条和人手差不多长的DNA链，"\
            "就可以存储1EB（1EB=10.74亿G）数据。与硬盘和闪存的数据存储密度相比，硬盘存储每立方厘米约为1013位，闪存存储约为1016位，"\
            "而DNA存储的密度约为1019位。2）DNA分子存储具有稳定性。" \
            "今年2月，国际顶级学术期刊Nature上的一篇论文称古生物学家在西伯利亚东北部的永久冻土层中提取到距今120万年猛犸象的遗传物质，" \
            "并对其DNA进行了解析，这也进一步刷新了DNA分子的保存年代纪录。据悉，DNA至少可保留上百年的数据，相比之下，硬盘、磁带的数据最多只能保留约10年。" \
            "3）DNA存储维护成本低。以DNA形式存储的数据易于维护，和传统的数据中心不同，不需要大量的人力、财力投入，仅需要保存在低温环境中。" \
            "在能耗方面,1GB的数据硬盘存储能耗约为0.04W,而DNA存储的能耗则小于10-10W。"

# image_path = '../data/testA.jpg'  # 替换为你的图片路径
# output_path = '../data/output_image.jpg'  # 替换为输出图片的路径
# diff_image_dir = '../result/testA/10-25-01'  # 替换为差异图片的保存路径
#
# video_path = '../data/test3.mp4'
# output_video_dir = '../result/Video/10-25-01'
# VTCode作为参数，记录是否进行VT编码
def textTest_Reconstruction(origin_text = originText,type = 1):
    Artificial=False
    VTCodeEncode=False
    if(type==2):
        Artificial=True
        VTCodeEncode=False
    elif(type==3):
        Artificial=True
        VTCodeEncode=True

    total_length = CHUNK_SIZE * 4    # 无论是否进行分段orVT编码，并不影响最终序列重构结果的对应长度
    global SEGMENT_LEN
    if (Artificial is False):
        SEGMENT_LEN = CHUNK_SIZE * 4
    else:
        SEGMENT_LEN = CHUNK_SIZE
    # 1.encodeFromText转换为碱基序列
    origin_acgt_seqs,origin_seq_cnt = data_transfer.encodeFromText(origin_text,CHUNK_SIZE,SEGMENT_LEN)
    encoding_acgt_seqs = origin_acgt_seqs
    # 2.进行VT编码(可选)
    if(VTCodeEncode):
        encoding_acgt_seqs = VTCode.VTCodeEncodeSequences(origin_acgt_seqs,delimiterChar)   #进行VT编码
    # 3.random_channel进行随机删除
    #clusters = channel.random_channel(origin_acgt_seqs,CLUSTER_SIZE,DEL_NUM)
    clusters = channel.random_channel_Probabilistic(encoding_acgt_seqs,CLUSTER_SIZE,CLUSTER_LOSS_RATE,BASE_LOSS_RATE)

    # 4.序列重构
    recon_ACGT_seqs=[]
    for clu in clusters:
        if(len(clu)==0):
            # 补充为全0
            recon_ACGT_seqs.append('A'*total_length)
            continue
        rec_seq ,success = RECONS.Reconstruction(clu,Artificial,VTCodeEncode,total_length,SEGMENT_LEN,delimiterChar)
        recon_ACGT_seqs.append(rec_seq)

    print("序列重构成功率为:",recons_success_rate(origin_acgt_seqs,recon_ACGT_seqs,delimiterChar))

    # 验证序列长度是否等于 CHUNK_SIZE * 4
    try:
        for seq in origin_acgt_seqs:
            if len(seq) != CHUNK_SIZE * 4:
                raise ValueError(f"序列长度不是 {CHUNK_SIZE*4 }：{seq}")
    except ValueError as e:
        print(e)
    #6.恢复原数据内容
    return data_transfer.decodeToText(recon_ACGT_seqs, origin_seq_cnt, CHUNK_SIZE)





imagePath = '../data/testA.jpg'  # 替换为你的图片路径
# output_path = '../data/output_image.jpg'  # 替换为输出图片的路径
# diff_image_dir = '../result/testA/10-25-01'  # 替换为差异图片的保存路径

videoPath = '../data/test3.mp4'
# output_video_dir = '../result/Video/10-25-01'



def imageTest_Reconstruction(image_path,type = 1):
    Artificial=False
    VTCodeEncode=False
    if(type==2):
        Artificial=True
        VTCodeEncode=False
    elif(type==3):
        Artificial=True
        VTCodeEncode=True

    print(" \n ======================  NewTest  ===================== ")
    total_length = CHUNK_SIZE *4    # 无论是否进行分段orVT编码，并不影响最终序列重构结果的对应长度
    # 1.encodeFromText转换为碱基序列
    global SEGMENT_LEN
    if (Artificial is False):
        SEGMENT_LEN = CHUNK_SIZE * 4
    else:
        SEGMENT_LEN = CHUNK_SIZE

    startTime = time.time()
    origin_acgt_seqs, n = data_transfer.encodeFromImage(image_path,CHUNK_SIZE,SEGMENT_LEN)
    encoding_acgt_seqs = origin_acgt_seqs
    print(f'### Image has been split into {len(origin_acgt_seqs)} chunks. cost time:',time.time()-startTime)

    # 2.进行VT编码(可选)
    if(VTCodeEncode):
        startTime = time.time()
        encoding_acgt_seqs = VTCode.VTCodeEncodeSequences(origin_acgt_seqs,delimiterChar)   #进行VT编码
        print("### VT Encode cost time:", time.time() - startTime)

    # 3.random_channel进行随机删除
    startTime = time.time()
    #clusters = channel.random_channel(origin_acgt_seqs,CLUSTER_SIZE,DEL_NUM)
    clusters = channel.random_channel_Probabilistic(encoding_acgt_seqs,CLUSTER_SIZE,CLUSTER_LOSS_RATE,BASE_LOSS_RATE)
    print("### random_channel cost time:", time.time() - startTime)


    # 4.序列重构
    startTime = time.time()
    recon_ACGT_seqs=[]
    for clu in clusters:
        if(len(clu)==0):
            # 补充为全0
            recon_ACGT_seqs.append('A'*total_length)
            continue
        rec_seq ,success = RECONS.Reconstruction(clu,Artificial,VTCodeEncode,total_length,SEGMENT_LEN,delimiterChar)
        recon_ACGT_seqs.append(rec_seq)
    print("### Reconstruction cost time:", time.time() - startTime)
    print("序列重构成功率为:",recons_success_rate(origin_acgt_seqs,recon_ACGT_seqs,delimiterChar))


    output_image_dir =  os.path.join(os.path.dirname(image_path),"imageResult")
    # 检查文件夹是否存在
    if not os.path.exists(output_image_dir):
        # 不存在则创建文件夹
        os.makedirs(output_image_dir)
    k=0
    k += 1 if(Artificial==True) else 0
    k += 1 if (VTCodeEncode == True) else 0

    outputimageName =  str(CLUSTER_LOSS_RATE)+'-'+ str( BASE_LOSS_RATE )+'-' +str(CLUSTER_SIZE)+'-'+str(RS_NUMBER) + '-' + str(k)+".jpg"
    output_path = os.path.join(output_image_dir,outputimageName)

    # 6.恢复原数据内容
    startTime = time.time()
    data_transfer.decodeToImage(output_path, recon_ACGT_seqs, n,CHUNK_SIZE)
    print(f'### Image has been combined and saved to {output_path},cost time :', time.time() - startTime)

    outputimageName =  str(CLUSTER_LOSS_RATE)+'-'+ str( BASE_LOSS_RATE )+'-' +str(CLUSTER_SIZE)+'-'+str(RS_NUMBER) + '-' + str(k)+".jpg"
    data_transfer.compare_and_save_images(image_path, output_path, os.path.join(output_image_dir,"diff"+outputimageName))



def videoTest_Reconstruction(video_path,type = 1):
    Artificial=False
    VTCodeEncode=False
    if(type==2):
        Artificial=True
        VTCodeEncode=False
    elif(type==3):
        Artificial=True
        VTCodeEncode=True

    print(" \n ======================  NewTest  ===================== ")
    total_length = CHUNK_SIZE *4    # 无论是否进行分段orVT编码，并不影响最终序列重构结果的对应长度

    # 1.encodeFromText转换为碱基序列
    global SEGMENT_LEN
    if (Artificial is False):
        SEGMENT_LEN = CHUNK_SIZE * 4
    else:
        SEGMENT_LEN = CHUNK_SIZE

    startTime = time.time()
    origin_acgt_seqs, n = data_transfer.encodeFromVedio(video_path,CHUNK_SIZE,SEGMENT_LEN)
    encoding_acgt_seqs = origin_acgt_seqs
    print(f'### Vedio has been split into {len(origin_acgt_seqs)} chunks. cost time:',time.time()-startTime)

    # 2.进行VT编码(可选)
    if(VTCodeEncode):
        startTime = startTime = time.time()
        encoding_acgt_seqs = VTCode.VTCodeEncodeSequences(origin_acgt_seqs,delimiterChar)   #进行VT编码
        print("### VT Encode cost time:",time.time()-startTime)

    startTime = time.time()
    # 3.random_channel进行随机删除
    #clusters = channel.random_channel(origin_acgt_seqs,CLUSTER_SIZE,DEL_NUM)
    clusters = channel.random_channel_Probabilistic(encoding_acgt_seqs,CLUSTER_SIZE,CLUSTER_LOSS_RATE,BASE_LOSS_RATE)
    print("### random_channel cost time:", time.time() - startTime)

    # 4.序列重构

    startTime = time.time()
    recon_ACGT_seqs=[]
    for clu in clusters:
        if(len(clu)==0):
            # 补充为全0
            recon_ACGT_seqs.append('A'*total_length)
            continue
        rec_seq ,success = RECONS.Reconstruction(clu,Artificial,VTCodeEncode,total_length,SEGMENT_LEN,delimiterChar)
        recon_ACGT_seqs.append(rec_seq)
    print("### Reconstruction cost time:", time.time() - startTime)
    print("序列重构成功率为:",recons_success_rate(origin_acgt_seqs,recon_ACGT_seqs,delimiterChar))

    k = 0
    k += 1 if (Artificial == True) else 0
    k += 1 if (VTCodeEncode == True) else 0

    output_video_dir = os.path.join(os.path.dirname(video_path),"videoResult")
    # 检查文件夹是否存在
    if not os.path.exists(output_video_dir):
        # 不存在则创建文件夹
        os.makedirs(output_video_dir)
    outputvideoName = str(CLUSTER_LOSS_RATE) + '-' + str(BASE_LOSS_RATE) + '-' + str(CLUSTER_SIZE) + '-' + str(
        RS_NUMBER) + '-' + str(k) + ".mp4"

    #recon_ACGT_seqs= origin_acgt_seqs

    # 6.恢复原数据内容
    startTime = time.time()
    data_transfer.decodeToVedio(os.path.join(output_video_dir,outputvideoName), recon_ACGT_seqs, n,CHUNK_SIZE)
    print(f'### video has been combined and saved to {outputvideoName},cost time :',time.time()-startTime)



global BASE_LOSS_RATE,CLUSTER_LOSS_RATE,RS_NUMBER,CLUSTER_SIZE
# 通过可视化界面设置参数
def setPara(baseLoss = BASE_LOSS_RATE,cluLoss = CLUSTER_LOSS_RATE,rsNumber=RS_NUMBER,cluSize=CLUSTER_SIZE):
    BASE_LOSS_RATE = baseLoss
    CLUSTER_LOSS_RATE = cluLoss
    RS_NUMBER = rsNumber
    CLUSTER_SIZE = cluSize


def all_test():
    textTest_Reconstruction("啊撒大苏打实打实",1)     # 不加分隔符
    # textTest_Reconstruction(2)      # 加人工碱基作为分隔符，全空间
    # textTest_Reconstruction(3)      # 人工碱基 + VT码


    # imageTest_Reconstruction(imagePath,1)     # 不加分隔符
    # imageTest_Reconstruction(imagePath,2)      # 加人工碱基作为分隔符，全空间
    # imageTest_Reconstruction(imagePath,3)      # 人工碱基 + VT码
    #
    # videoTest_Reconstruction(videoPath, 1)
    # videoTest_Reconstruction(videoPath,2)
    # videoTest_Reconstruction(videoPath,3)


all_test()