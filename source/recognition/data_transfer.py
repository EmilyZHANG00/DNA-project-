# import time
# from reedsolo import RSCodec
# from PIL import Image
# import cv2
# import matplotlib.pyplot as plt
# import numpy as np
# from Config  import RS_NUMBER,DEBUG,RS_FIELD_SIZE
# rsc = RSCodec(RS_NUMBER,nsize=255)
# from Config import Dprint,RS_ENCODE_VALID,VIDEO_IMGSIZE_BYTE_CNT,VIDEO_VALID_END
# ImageShape = None
# FrameShape = None
#
#
# def RSencode(origin_bytes_list):
#     if(RS_ENCODE_VALID is False):
#         return origin_bytes_list
#
#     rs_col_byte_arr_list=[]
#     for col in range(0,len(origin_bytes_list[0])):
#         """创建新的n长字节串并进行RS编码"""
#         col_byte_arr = bytearray()
#         for byte_str in origin_bytes_list:
#             col_byte_arr.append(byte_str[col])
#         rs_col_byte_arr = rsc.encode(col_byte_arr)
#         rs_col_byte_arr_list.append(rs_col_byte_arr)
#
#     rs_bytes_lists=[]
#     for row in range(0,len(rs_col_byte_arr_list[0])):
#         row_byte_arr = bytearray()
#         for rs_col_byte_arr in rs_col_byte_arr_list:
#             row_byte_arr.append(rs_col_byte_arr[row])
#         rs_bytes_lists.append(row_byte_arr)
#     return rs_bytes_lists
#
#
# # [输入] rs_bin_str_lists:RS编码后的byte串构成的列表  Data_seq_cnt:原始数据对应的序列数目;
# # [输出] 原始数据内容的bytes串构成的列表
# def RSdecode(rs_bin_str_lists,Data_seq_cnt,erase_list):
#     # 01字符串转换为bytes 字节串
#     rs_bytes_lines = []
#     for rs_bin_str in rs_bin_str_lists:
#         bytes_from_binary = bytes([int(rs_bin_str[i:i + 8], 2) for i in range(0, len(rs_bin_str), 8)])
#         rs_bytes_lines.append(bytes_from_binary)
#
#     if(RS_ENCODE_VALID is False):
#         return rs_bytes_lines
#
#     # 把数据部分对应取出来
#     rs_fail_return = []
#     for i in range(0, len(rs_bytes_lines), RS_FIELD_SIZE):
#         # 获取当前块的前B个元素
#         block = rs_bytes_lines[i:min(len(rs_bytes_lines),i+RS_FIELD_SIZE)-RS_NUMBER]
#         # 将当前块的元素添加到结果列表中
#         rs_fail_return.extend(block)
#     col_bytestr_list = []
#     for col in range(0,len(rs_bytes_lines[0])):
#         """按列进行RS解码"""
#         col_k_rs_bytes_arr = bytearray()
#         for bytes_str in rs_bytes_lines:
#             col_k_rs_bytes_arr.append(bytes_str[col])
#         # RS解码
#         try:
#             # for idx in erase_list:
#             #     print(idx,",",len(erase_list),col_k_rs_bytes_arr[idx-1],col_k_rs_bytes_arr[idx],col_k_rs_bytes_arr[idx+1])
#             #     col_k_rs_bytes_arr[idx]=0
#             # repaired_message, repaired_message_with_ecc, additional_info = rsc.decode(col_k_rs_bytes_arr,erase_pos = erase_list,only_erasures =True)
#             repaired_message, repaired_message_with_ecc, additional_info = rsc.decode(col_k_rs_bytes_arr)
#             # print("RS解码后的消息:", repaired_message)
#             # print("修复后的消息 + ECC:", repaired_message_with_ecc)
#             # print("附加信息:", additional_info)
#             col_bytestr_list.append(repaired_message)
#
#         except ValueError as e:
#             print("解包错误:", e)
#             return rs_fail_return
#         except Exception as e:
#             print("其他错误:", e)
#             return rs_fail_return
#
#     origin_byte_arr_lines = []
#     for row in range(0,len(col_bytestr_list[0])):
#         origin_bytes = bytearray()
#         for col_k_bytestr in col_bytestr_list:
#             origin_bytes.append(col_k_bytestr[row])
#         origin_byte_arr_lines.append(origin_bytes)
#     return origin_byte_arr_lines
#
#
# def encodeFromBytes(bytesStr,chunk_size,segment_len,delimiterChar='M'):
#     # 1.分割成32长的字节串;对第一个字节串和最后一个字节串进行处理，统一长度为57
#     bytes_list = [bytesStr[i:i + chunk_size] for i in range(0, len(bytesStr), chunk_size)]
#     bytes_list.insert(0,bytes(len(bytesStr)))
#
#
#     bytes_len = len(bytesStr)
#     bytes_list[0] = bytes_len.to_bytes(length=chunk_size, byteorder='little', signed=False)
#     bytes_list[-1] = bytes_list[-1] + (' '*(chunk_size-len(bytes_list[-1] ))).encode()
#     data_seq_cnt = len(bytes_list)
#     print("encodeFromBytes:总数据长度为",bytes_len,"共分割为", data_seq_cnt,"个短字节串数组：","每个长度为",chunk_size)
#     Dprint(bytes_list)
#
#
#     # 2.RS编码
#     RS_bytes_lists = RSencode(bytes_list)
#     print("encodeFromBytes:进行RS编码后数组长度为", len(RS_bytes_lists))
#     Dprint("RS_bytes_lists：", RS_bytes_lists)
#
#
#     # 3 bytes变成01序列，再进一步变成碱基
#     conversion = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
#     ACGT_str_lists=[]
#     for bytestr  in  RS_bytes_lists:
#         binstr=''.join(format(byte, '08b') for byte in bytestr)
#         ACGT_str=''
#         for i in range(0,len(binstr),2):
#             ACGT_str += conversion[binstr[i:i+2]]
#         ACGT_str_lists.append(ACGT_str)
#     Dprint("RS编码后碱基序列内容：",ACGT_str_lists)
#
#     # 4.添加分隔符（当segment_len小于序列长度时才加分隔符进行分段）
#     if(segment_len < len(ACGT_str_lists[0])):
#         for i in range(0,len(ACGT_str_lists)):
#             str = ACGT_str_lists[i]
#             result_str=''
#             result_str = str[0:segment_len]
#             for idx in range(segment_len,len(str), segment_len):
#                 result_str += delimiterChar+str[idx:idx+segment_len]
#             ACGT_str_lists[i] = result_str
#     return ACGT_str_lists,data_seq_cnt
#
#
# ## 从ACGT碱基序列转换为原数据内容(这里的ACGT碱基序列是不包含分隔符的)
# def decodeToBytes(RS_ACGT_str_lists,Data_seq_cnt,erase_list,chunk_size):
#     # 1.转换为01序列
#     conversion = {'A':'00', 'C':'01','G':'10', 'T':'11'}
#     bin_str_lists = []
#     for str in RS_ACGT_str_lists:
#         bin_str = ''
#         for  ch in str:
#             bin_str += conversion[ch]
#         bin_str_lists.append(bin_str)
#     Dprint("二进制字符串序列：",bin_str_lists)
#
#     # 2.01序列转换为字节串，并进行RS解码
#     bytes_list = RSdecode(bin_str_lists,Data_seq_cnt,erase_list)
#     Dprint("RS解码后字节串内容：", bytes_list)
#
#     print("decodeToBytes:RS解码前数据序列数组大小:", len(bin_str_lists))
#     print("decodeToBytes:RS解码后数据序列数组大小:",len(bytes_list))
#
#     # 3.求出第一个字节序所代表的内容（也就是数据总长度）
#     total_len = int.from_bytes(bytes_list[0], byteorder = 'little', signed = False)
#     print("decodeToBytes:解码出原序列总字节数目为:",total_len)
#
#     global ImageShape,FrameShape
#     if ImageShape is not None:
#         total_len = ImageShape[0] * ImageShape[1] * ImageShape[2]
#     elif FrameShape is not None:
#         total_len = FrameShape[0] * FrameShape[1] * FrameShape[2]
#
#     # 4. 拼接得到原始数据对应的字节串
#     bytes_str = bytearray()
#     for i in range(1,len(bytes_list)-1):
#         bytes_str += bytes_list[i]
#     bytes_str += bytes_list[-1][:(total_len % chunk_size)]
#     Dprint("4 二进制字节串内容：" ,bytes_str,total_len % chunk_size)
#     return bytes_str
#
#
# def encodeFromText(original_text,chunk_size,segment_len,delimiterChar='M'):
#     # 1.变成bytes类型  字节串
#     utf8_bytes = original_text.encode('utf-8')
#     Dprint("1 编码为字节串内容:",type(utf8_bytes),len( utf8_bytes),utf8_bytes)
#     ACGT_str_lists, date_seq_cnt = encodeFromBytes(utf8_bytes,chunk_size,segment_len,delimiterChar)
#     return ACGT_str_lists,date_seq_cnt
#
#
# ## 从ACGT碱基序列转换为原数据内容
# def decodeToText(RS_ACGT_str_lists,Data_seq_cnt,erase_list,chunk_size=57):
#     bytes_str = decodeToBytes(RS_ACGT_str_lists,Data_seq_cnt,erase_list,chunk_size)
#     # 5.尝试恢复原始数据
#     try:
#         restored_text = bytes_str.decode('utf-8')
#         print(f"5 恢复后的文本: {restored_text}")
#     except UnicodeDecodeError as e:
#         print("[ ######## 解码失败,错误过多，无法恢复原信息! #########] details:",e)
#         return f"[ ######## 解码失败,错误过多，无法恢复原信息! #########] details:{e}"
#     return restored_text
#
#
#
# ## 编码流程:文本->二进制序列->RS编码->碱基序列
# def encodeFromImage(image_path,chunk_size,segment_len,delimiterChar='M'):
#     # 1 打开图片,转换为字节流
#     with Image.open(image_path) as img:
#         # 将图片转换为字节流
#         img_array = np.array(img)
#         global ImageShape
#         ImageShape = img_array.shape
#         print("encodeFromImage:图片尺寸",img_array.shape)
#     byte_array = img_array.tobytes()
#     print("encodeFromImage : 原图片转换为bytes，字节数目",len(byte_array))
#
#     ACGT_str_lists, date_seq_cnt = encodeFromBytes(byte_array,chunk_size,segment_len,delimiterChar)
#     print("encodeFromImage: 编码后每个序列长", len(ACGT_str_lists[0]),"序列数目：", len(ACGT_str_lists))
#     return ACGT_str_lists,date_seq_cnt
#
#
#
# ## 从ACGT碱基序列转换为原数据内容
# def decodeToImage(output_path,RS_ACGT_str_lists,Data_seq_cnt,erase_list,chunk_size, image_format='PNG'):
#     print("decodeToImage: 序列重构后后每个序列长", len(RS_ACGT_str_lists[0]),"序列数目：", len(RS_ACGT_str_lists))
#
#     # 2.将字节流转换numpy数组
#     byte_array = decodeToBytes(RS_ACGT_str_lists, Data_seq_cnt, erase_list,chunk_size)
#     print("decodeToImage :", type(byte_array), len(byte_array))
#
#     # 3.将numpy转换为图片
#     modified_image_array = np.frombuffer(byte_array, dtype=np.uint8).reshape(ImageShape)
#
#     # 4.创建Pillow图像对象
#     recons_image = Image.fromarray(modified_image_array)
#     recons_image.save(output_path, format=image_format)
#
#
# def compare_and_save_images(input_image_path, output_image_path, diff_image_path):
#     # 读取输入和输出图片
#     input_image = Image.open(input_image_path)
#     output_image = Image.open(output_image_path)
#
#     # 将图片转换为numpy数组以便计算差异
#     input_image_np = np.array(input_image)
#     output_image_np = np.array(output_image)
#
#     # 计算差异
#     diff = np.abs(input_image_np - output_image_np)
#     diff_image = Image.fromarray(np.uint8(diff))
#
#     # 展示图片
#     plt.figure(figsize=(10, 3))
#
#     plt.subplot(1, 3, 1)
#     plt.imshow(input_image_np)
#     plt.title('Input Image')
#     plt.axis('off')
#
#     plt.subplot(1, 3, 2)
#     plt.imshow(output_image_np)
#     plt.title('Output Image')
#     plt.axis('off')
#
#     plt.subplot(1, 3, 3)
#     plt.imshow(diff_image)
#     plt.title('Difference')
#     plt.axis('off')
#
#     # 保存整体图片
#     plt.savefig(diff_image_path,dpi=250)
#     plt.show()
#
#
# def encodeFromVedioAsFrame(video_path,chunk_size,segment_len,delimiterChar='M'):
#     # 1 打开视频文件
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         raise ValueError("无法打开视频文件")
#
#     total_frames = -1
#     # 读取第一帧作为参考帧
#     ret, prev_frame = cap.read()
#     if not ret:
#         raise ValueError("无法读取视频帧")
#     else:
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#
#     bytes_arr = bytearray()
#     lastframe = np.zeros_like(prev_frame)
#     global FrameShape
#     FrameShape = prev_frame.shape
#
#     frame_idx = 0
#     while True:
#         frame_idx += 1
#         # 读取当前帧
#         ret, frame = cap.read()
#         if not ret:
#             break
#         bytes_arr += frame.tobytes()
#
#         if(frame_idx % (total_frames // 10) == 0):
#             print("encoding ", frame_idx, "/", total_frames, "size:", frame.shape,"......" )
#         # if(frame_idx>3):
#         #     break
#         # 更新参考帧
#
#     cap.release()
#
#     ACGT_str_lists, date_seq_cnt = encodeFromBytes(bytes_arr,chunk_size,segment_len,delimiterChar)
#     print("encodeFromVedio: 编码后每个序列长", len(ACGT_str_lists[0]),"序列数目：", len(ACGT_str_lists))
#     return ACGT_str_lists,date_seq_cnt
#
#
#
# ## 从ACGT碱基序列转换为原数据内容
# def decodeToVedioAsFrame(output_vedio_path,RS_ACGT_str_lists,Data_seq_cnt,erase_list,chunk_size, image_format='PNG'):
#     print("decodeToVedio: 序列重构后后每个序列长", len(RS_ACGT_str_lists[0]),"序列数目：", len(RS_ACGT_str_lists))
#     bytes_arr = decodeToBytes(RS_ACGT_str_lists, Data_seq_cnt, erase_list,chunk_size)
#     print("decodeToVedio :", type(bytes_arr), len(bytes_arr))
#     # 计算总共有多少帧
#     frame_size = FrameShape[0] * FrameShape[1] * FrameShape[2]
#     num_frames = len(bytes_arr) // frame_size
#
#     out = cv2.VideoWriter(output_vedio_path, cv2.VideoWriter_fourcc(*'mp4v'), min(num_frames, 30),
#                           (FrameShape[1], FrameShape[0]))
#
#     # 将bytearray转换回帧
#     for i in range(num_frames):
#         # 提取一个帧的数据
#         frame_data = bytes_arr[i * frame_size:(i + 1) * frame_size]
#         # 将字节数据转换为NumPy数组
#         frame_array = np.frombuffer(frame_data, dtype=np.uint8)
#         # 将一维数组重新构造成二维图像数组
#         frame_image = frame_array.reshape((FrameShape[0], FrameShape[1], 3))
#         # 写入帧到视频文件
#         out.write(frame_image)
#
#     # 释放视频写入对象
#     out.release()
#
#
#
# def encodeFromVedio(video_path,chunk_size,segment_len,delimiterChar='M'):
#     # 1 打开视频文件
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         raise ValueError("无法打开视频文件")
#
#     total_frames = -1
#     # 读取第一帧作为参考帧
#     ret, prev_frame = cap.read()
#     if not ret:
#         raise ValueError("无法读取视频帧")
#     else:
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#
#     bytes_arr = bytearray()
#     lastframe = np.zeros_like(prev_frame)
#     global  FrameShape
#     FrameShape = prev_frame.shape
#
#     frame_idx = 0
#     while True:
#         frame_idx += 1
#         # 读取当前帧
#         ret, frame = cap.read()
#         if not ret:
#             break
#         # 计算当前帧与上一帧的差分
#         diff = frame.astype(np.int8) - lastframe
#         points_cnt = 0
#         for y in range(diff.shape[0]):
#             for x in range(diff.shape[1]):
#                 if diff[y, x, 0] != 0 or diff[y, x, 1] != 0 or diff[y, x, 2] != 0 or  (x==0 and y==0 ) or (x==diff.shape[1]-1 and  y == diff.shape[0]-1):
#                     # 位置用3个字节表示（假设视频帧大小不超过1G像素）
#                     pos = y * frame.shape[1] + x
#                     bytes_arr.extend(pos.to_bytes(VIDEO_IMGSIZE_BYTE_CNT, 'little'))  # 位置
#                     bytes_arr.append(frame[y, x, 0])
#                     bytes_arr.append(frame[y, x, 1])
#                     bytes_arr.append(frame[y, x, 2])
#                     points_cnt += 1
#         if(frame_idx % (total_frames // 10) == 0):
#             print("encoding ", frame_idx, "/", total_frames, "size:", frame.shape, points_cnt,"......" )
#         # if(frame_idx>10):
#         #     break
#         # 更新参考帧
#         lastframe = frame.astype(np.int8)
#
#     cap.release()
#
#     ACGT_str_lists, date_seq_cnt = encodeFromBytes(bytes_arr,chunk_size,segment_len,delimiterChar)
#     print("encodeFromVedioAsFrame: 编码后每个序列长", len(ACGT_str_lists[0]),"序列数目：", len(ACGT_str_lists))
#     return ACGT_str_lists,date_seq_cnt
#
#
#
# ## 从ACGT碱基序列转换为原数据内容
# def decodeToVedio(output_vedio_path,RS_ACGT_str_lists,Data_seq_cnt,erase_list,chunk_size, image_format='PNG'):
#     print("decodeToVedioAsFrame: 序列重构后后每个序列长", len(RS_ACGT_str_lists[0]),"序列数目：", len(RS_ACGT_str_lists))
#     bytes_arr = decodeToBytes(RS_ACGT_str_lists, Data_seq_cnt, erase_list,chunk_size)
#     print("decodeToVedioAsFrame :", type(bytes_arr), len(bytes_arr))
#
#     # 将Bytes转换为帧
#     # 初始化视频帧的数组
#     frames = []
#     frame = np.zeros((FrameShape[0], FrameShape[1], 3), dtype=np.uint8)
#     # 初始化字节序列的索引
#     index = 0
#     lastpos = 0
#
#     while index < len(bytes_arr)-VIDEO_IMGSIZE_BYTE_CNT-3:
#         # 读取位置信息，位置使用3个字节
#
#         pos = int.from_bytes(bytes_arr[index:index + VIDEO_IMGSIZE_BYTE_CNT], 'little')
#         index += VIDEO_IMGSIZE_BYTE_CNT
#         if(pos<0 or pos >= FrameShape[0] * FrameShape[1]):
#             index += 3
#             continue
#         if(pos == 0  and lastpos >= FrameShape[0] * FrameShape[1] * VIDEO_VALID_END): # 保存一个帧
#             frames.append(frame.copy())
#         #print(pos,lastpos)
#         pos_x = int(pos / FrameShape[1])
#         pos_y = int(pos % FrameShape[1])
#
#         if(pos_x < FrameShape[0] and pos_y < FrameShape[1]):
#         # 读取三个元素的值，每个通道值使用1个字节
#             frame[pos_x,pos_y,0] = bytes_arr[index]
#             frame[pos_x,pos_y,1] = bytes_arr[index+1]
#             frame[pos_x,pos_y,2] = bytes_arr[index+2]
#         index += 3
#         lastpos = pos
#
#     frames.append(frame.copy())
#     # 将帧数组转换为视频
#     print("重构后帧数目:",len(frames),"开始写入视频......")
#     out = cv2.VideoWriter(output_vedio_path, cv2.VideoWriter_fourcc(*'mp4v'), min(len(frames),30), (FrameShape[1],FrameShape[0]))
#     for frame in frames:
#         # cv2.imshow('Frame', frame)
#         # time.sleep(2)
#         # if cv2.waitKey(1) & 0xFF == ord('q'):
#         #     break
#         out.write(frame)
#     out.release()
#
#
#
# def finddataindex(image_path,chunk_size,segment_len,delimiterChar='M'):
#     # 1 打开图片,转换为字节流
#     with Image.open(image_path) as img:
#         # 将图片转换为字节流
#         img_array = np.array(img)
#         global ImageShape
#         ImageShape = img_array.shape
#         print("encodeFromImage:图片尺寸",img_array.shape)
#     byte_array = img_array.tobytes()
#     print("encodeFromImage : 原图片转换为bytes，字节数目",len(byte_array))
#     # 1.分割成32长的字节串;对第一个字节串和最后一个字节串进行处理，统一长度为57
#     bytes_list = [byte_array[i:i + chunk_size] for i in range(0, len(byte_array), chunk_size)]
#     bytes_list.insert(0, bytes(len(byte_array)))
#
#     bytes_len = len(byte_array)
#     bytes_list[0] = bytes_len.to_bytes(length=chunk_size, byteorder='little', signed=False)
#     bytes_list[-1] = bytes_list[-1] + (' ' * (chunk_size - len(bytes_list[-1]))).encode()
#     data_seq_cnt = len(bytes_list)
#     print("encodeFromBytes:总数据长度为", bytes_len, "共分割为", data_seq_cnt, "个短字节串数组：", "每个长度为",
#           chunk_size)
#     Dprint(bytes_list)
#
#     #bytes_list =bytes_list[0:300]
#     # 2.RS编码
#     RS_bytes_lists = RSencode(bytes_list)
#     print("encodeFromBytes:进行RS编码后数组长度为", len(RS_bytes_lists))
#     Dprint("RS_bytes_lists：", RS_bytes_lists)
#
#     # bytes_list是原来的数据内容， ebytes现在是对原来的数据内容去进行遍历，求原来数据部分在生成的rs码编码数部分对应的序列下标
#     res = []
#     cnt = 0
#     for ebytes in bytes_list:
#         for idx in range(0, len(RS_bytes_lists)):
#             if (ebytes ==  RS_bytes_lists[idx]):
#                 # if(len(res)>1 and idx!=res[-1]+1):
#                 print("第",cnt,"个序列对应",idx)
#                 res.append(idx)
#                 break
#         cnt+=1
#     # print(len(res),res)
#     return res
#
#
# # finddataindex("D:\Desktop\Dna-encoding\data\Image6.jpg",57,57)



import time
from reedsolo import RSCodec
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import numpy as np
import Config
# from Config import Dprint,RS_ENCODE_VALID,VIDEO_IMGSIZE_BYTE_CNT,VIDEO_VALID_END
ImageShape = None
FrameShape = None


def RSencode(origin_bytes_list,RS_NUMBER):
    if(Config.RS_ENCODE_VALID is False):
        return origin_bytes_list

    rs_col_byte_arr_list=[]
    for col in range(0,len(origin_bytes_list[0])):
        """创建新的n长字节串并进行RS编码"""
        col_byte_arr = bytearray()
        for byte_str in origin_bytes_list:
            col_byte_arr.append(byte_str[col])
        rsc = RSCodec(RS_NUMBER,nsize=255)
        rs_col_byte_arr = rsc.encode(col_byte_arr)
        rs_col_byte_arr_list.append(rs_col_byte_arr)

    rs_bytes_lists=[]
    for row in range(0,len(rs_col_byte_arr_list[0])):
        row_byte_arr = bytearray()
        for rs_col_byte_arr in rs_col_byte_arr_list:
            row_byte_arr.append(rs_col_byte_arr[row])
        rs_bytes_lists.append(row_byte_arr)
    return rs_bytes_lists


# [输入] rs_bin_str_lists:RS编码后的byte串构成的列表  Data_seq_cnt:原始数据对应的序列数目;
# [输出] 原始数据内容的bytes串构成的列表
def RSdecode(rs_bin_str_lists,RS_NUMBER,Data_seq_cnt,erase_list):
    # 01字符串转换为bytes 字节串
    rs_bytes_lines = []
    for rs_bin_str in rs_bin_str_lists:
        bytes_from_binary = bytes([int(rs_bin_str[i:i + 8], 2) for i in range(0, len(rs_bin_str), 8)])
        rs_bytes_lines.append(bytes_from_binary)
    print(rs_bin_str_lists,rs_bytes_lines)
    if(Config.RS_ENCODE_VALID is False):
        return rs_bytes_lines

    # 把数据部分对应取出来
    rs_fail_return = []
    for i in range(0, len(rs_bytes_lines), Config.RS_FIELD_SIZE):
        # 获取当前块的前B个元素
        block = rs_bytes_lines[i:min(len(rs_bytes_lines),i+Config.RS_FIELD_SIZE)-RS_NUMBER]
        # 将当前块的元素添加到结果列表中
        rs_fail_return.extend(block)
    col_bytestr_list = []
    for col in range(0,len(rs_bytes_lines[0])):
        """按列进行RS解码"""
        col_k_rs_bytes_arr = bytearray()
        for bytes_str in rs_bytes_lines:
            col_k_rs_bytes_arr.append(bytes_str[col])
        # RS解码
        try:
            # for idx in erase_list:
            #     print(idx,",",len(erase_list),col_k_rs_bytes_arr[idx-1],col_k_rs_bytes_arr[idx],col_k_rs_bytes_arr[idx+1])
            #     col_k_rs_bytes_arr[idx]=0
            # repaired_message, repaired_message_with_ecc, additional_info = rsc.decode(col_k_rs_bytes_arr,erase_pos = erase_list,only_erasures =True)
            rsc = RSCodec(RS_NUMBER,nsize=255)
            repaired_message, repaired_message_with_ecc, additional_info = rsc.decode(col_k_rs_bytes_arr)
            # print("RS解码后的消息:", repaired_message)
            # print("修复后的消息 + ECC:", repaired_message_with_ecc)
            # print("附加信息:", additional_info)
            col_bytestr_list.append(repaired_message)

        except ValueError as e:
            print("解包错误:", e)
            return rs_fail_return
        except Exception as e:
            print("其他错误:", e)
            return rs_fail_return

    origin_byte_arr_lines = []
    for row in range(0,len(col_bytestr_list[0])):
        origin_bytes = bytearray()
        for col_k_bytestr in col_bytestr_list:
            origin_bytes.append(col_k_bytestr[row])
        origin_byte_arr_lines.append(origin_bytes)
    return origin_byte_arr_lines


def encodeFromBytes(bytesStr,RS_NUMBER,chunk_size,segment_len,delimiterChar='M'):
    # 1.分割成32长的字节串;对第一个字节串和最后一个字节串进行处理，统一长度为57
    bytes_list = [bytesStr[i:i + chunk_size] for i in range(0, len(bytesStr), chunk_size)]
    bytes_list.insert(0,bytes(len(bytesStr)))


    bytes_len = len(bytesStr)
    bytes_list[0] = bytes_len.to_bytes(length=chunk_size, byteorder='little', signed=False)
    bytes_list[-1] = bytes_list[-1] + (' '*(chunk_size-len(bytes_list[-1] ))).encode()
    data_seq_cnt = len(bytes_list)
    print("encodeFromBytes:总数据长度为",bytes_len,"共分割为", data_seq_cnt,"个短字节串数组：","每个长度为",chunk_size)
    Config.Dprint(bytes_list)


    # 2.RS编码
    RS_bytes_lists = RSencode(bytes_list,RS_NUMBER)
    print("encodeFromBytes:进行RS编码后数组长度为", len(RS_bytes_lists))
    Config.Dprint("RS_bytes_lists：", RS_bytes_lists)


    # 3 bytes变成01序列，再进一步变成碱基
    conversion = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
    ACGT_str_lists=[]
    for bytestr  in  RS_bytes_lists:
        binstr=''.join(format(byte, '08b') for byte in bytestr)
        ACGT_str=''
        for i in range(0,len(binstr),2):
            ACGT_str += conversion[binstr[i:i+2]]
        ACGT_str_lists.append(ACGT_str)
    Config.Dprint("RS编码后碱基序列内容：",ACGT_str_lists)

    # 4.添加分隔符（当segment_len小于序列长度时才加分隔符进行分段）
    if(segment_len < len(ACGT_str_lists[0])):
        for i in range(0,len(ACGT_str_lists)):
            str = ACGT_str_lists[i]
            result_str=''
            result_str = str[0:segment_len]
            for idx in range(segment_len,len(str), segment_len):
                result_str += delimiterChar+str[idx:idx+segment_len]
            ACGT_str_lists[i] = result_str
    return ACGT_str_lists,data_seq_cnt


## 从ACGT碱基序列转换为原数据内容(这里的ACGT碱基序列是不包含分隔符的)
def decodeToBytes(RS_ACGT_str_lists,RS_NUMBER,Data_seq_cnt,erase_list,chunk_size):
    # 1.转换为01序列
    conversion = {'A':'00', 'C':'01','G':'10', 'T':'11'}
    bin_str_lists = []
    for str in RS_ACGT_str_lists:
        bin_str = ''
        for  ch in str:
            bin_str += conversion[ch]
        bin_str_lists.append(bin_str)
    Config.Dprint("二进制字符串序列：",bin_str_lists)

    # 2.01序列转换为字节串，并进行RS解码
    bytes_list = RSdecode(bin_str_lists,RS_NUMBER,Data_seq_cnt,erase_list)
    Config.Dprint("RS解码后字节串内容：", bytes_list)

    print("decodeToBytes:RS解码前数据序列数组大小:", len(bin_str_lists))
    print("decodeToBytes:RS解码后数据序列数组大小:",len(bytes_list))

    # 3.求出第一个字节序所代表的内容（也就是数据总长度）
    total_len = int.from_bytes(bytes_list[0], byteorder = 'little', signed = False)
    print("decodeToBytes:解码出原序列总字节数目为:",total_len)

    global ImageShape,FrameShape
    if ImageShape is not None:
        total_len = ImageShape[0] * ImageShape[1] * ImageShape[2]
    elif FrameShape is not None:
        total_len = FrameShape[0] * FrameShape[1] * FrameShape[2]

    # 4. 拼接得到原始数据对应的字节串
    bytes_str = bytearray()
    for i in range(1,len(bytes_list)-1):
        bytes_str += bytes_list[i]
    bytes_str += bytes_list[-1][:(total_len % chunk_size)]
    Config.Dprint("4 二进制字节串内容：" ,bytes_str,total_len % chunk_size)
    return bytes_str


def encodeFromText(original_text,RS_NUMBER,chunk_size,segment_len,delimiterChar='M'):
    # 1.变成bytes类型  字节串
    utf8_bytes = original_text.encode('utf-8')
    Config.Dprint("1 编码为字节串内容:",type(utf8_bytes),len( utf8_bytes),utf8_bytes)
    ACGT_str_lists, date_seq_cnt = encodeFromBytes(utf8_bytes,RS_NUMBER,chunk_size,segment_len,delimiterChar)
    return ACGT_str_lists,date_seq_cnt


## 从ACGT碱基序列转换为原数据内容
def decodeToText(RS_ACGT_str_lists,RS_NUMBER,Data_seq_cnt,erase_list,chunk_size=57):
    bytes_str = decodeToBytes(RS_ACGT_str_lists,RS_NUMBER,Data_seq_cnt,erase_list,chunk_size)
    # 5.尝试恢复原始数据
    try:
        restored_text = bytes_str.decode('utf-8')
        print(f"5 恢复后的文本: {restored_text}")
    except UnicodeDecodeError as e:
        print("[ ######## 解码失败,错误过多，无法恢复原信息! #########] details:",e)
        return f"[ ######## 解码失败,错误过多，无法恢复原信息! #########] details:{e}"
    return restored_text



## 编码流程:文本->二进制序列->RS编码->碱基序列
def encodeFromImage(image_path,chunk_size,segment_len,delimiterChar='M'):
    # 1 打开图片,转换为字节流
    with Image.open(image_path) as img:
        # 将图片转换为字节流
        img_array = np.array(img)
        global ImageShape
        ImageShape = img_array.shape
        print("encodeFromImage:图片尺寸",img_array.shape)
    byte_array = img_array.tobytes()
    print("encodeFromImage : 原图片转换为bytes，字节数目",len(byte_array))

    ACGT_str_lists, date_seq_cnt = encodeFromBytes(byte_array,chunk_size,segment_len,delimiterChar)
    print("encodeFromImage: 编码后每个序列长", len(ACGT_str_lists[0]),"序列数目：", len(ACGT_str_lists))
    return ACGT_str_lists,date_seq_cnt



## 从ACGT碱基序列转换为原数据内容
def decodeToImage(output_path,RS_ACGT_str_lists,RS_NUMBER,Data_seq_cnt,erase_list,chunk_size, image_format='PNG'):
    print("decodeToImage: 序列重构后后每个序列长", len(RS_ACGT_str_lists[0]),"序列数目：", len(RS_ACGT_str_lists))

    # 2.将字节流转换numpy数组
    byte_array = decodeToBytes(RS_ACGT_str_lists, RS_NUMBER,Data_seq_cnt, erase_list,chunk_size)
    print("decodeToImage :", type(byte_array), len(byte_array))

    # 3.将numpy转换为图片
    modified_image_array = np.frombuffer(byte_array, dtype=np.uint8).reshape(ImageShape)

    # 4.创建Pillow图像对象
    recons_image = Image.fromarray(modified_image_array)
    recons_image.save(output_path, format=image_format)


def compare_and_save_images(input_image_path, output_image_path, diff_image_path):
    # 读取输入和输出图片
    input_image = Image.open(input_image_path)
    output_image = Image.open(output_image_path)

    # 将图片转换为numpy数组以便计算差异
    input_image_np = np.array(input_image)
    output_image_np = np.array(output_image)

    # 计算差异
    diff = np.abs(input_image_np - output_image_np)
    diff_image = Image.fromarray(np.uint8(diff))

    # 展示图片
    plt.figure(figsize=(10, 3))

    plt.subplot(1, 3, 1)
    plt.imshow(input_image_np)
    plt.title('Input Image')
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(output_image_np)
    plt.title('Output Image')
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(diff_image)
    plt.title('Difference')
    plt.axis('off')

    # 保存整体图片
    plt.savefig(diff_image_path,dpi=250)
    plt.show()


def encodeFromVedioAsFrame(video_path,RS_NUMBER,chunk_size,segment_len,delimiterChar='M'):
    # 1 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频文件")

    total_frames = -1
    # 读取第一帧作为参考帧
    ret, prev_frame = cap.read()
    if not ret:
        raise ValueError("无法读取视频帧")
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    bytes_arr = bytearray()
    lastframe = np.zeros_like(prev_frame)
    global FrameShape
    FrameShape = prev_frame.shape

    frame_idx = 0
    while True:
        frame_idx += 1
        # 读取当前帧
        ret, frame = cap.read()
        if not ret:
            break
        bytes_arr += frame.tobytes()

        if(frame_idx % (total_frames // 10) == 0):
            print("encoding ", frame_idx, "/", total_frames, "size:", frame.shape,"......" )
        # if(frame_idx>3):
        #     break
        # 更新参考帧

    cap.release()

    ACGT_str_lists, date_seq_cnt = encodeFromBytes(bytes_arr,RS_NUMBER,chunk_size,segment_len,delimiterChar)
    print("encodeFromVedio: 编码后每个序列长", len(ACGT_str_lists[0]),"序列数目：", len(ACGT_str_lists))
    return ACGT_str_lists,date_seq_cnt



## 从ACGT碱基序列转换为原数据内容
def decodeToVedioAsFrame(output_vedio_path,RS_ACGT_str_lists,RS_NUMBER,Data_seq_cnt,erase_list,chunk_size, image_format='PNG'):
    print("decodeToVedio: 序列重构后后每个序列长", len(RS_ACGT_str_lists[0]),"序列数目：", len(RS_ACGT_str_lists))
    bytes_arr = decodeToBytes(RS_ACGT_str_lists,RS_NUMBER, Data_seq_cnt, erase_list,chunk_size)
    print("decodeToVedio :", type(bytes_arr), len(bytes_arr))
    # 计算总共有多少帧
    frame_size = FrameShape[0] * FrameShape[1] * FrameShape[2]
    num_frames = len(bytes_arr) // frame_size

    out = cv2.VideoWriter(output_vedio_path, cv2.VideoWriter_fourcc(*'mp4v'), min(num_frames, 30),
                          (FrameShape[1], FrameShape[0]))

    # 将bytearray转换回帧
    for i in range(num_frames):
        # 提取一个帧的数据
        frame_data = bytes_arr[i * frame_size:(i + 1) * frame_size]
        # 将字节数据转换为NumPy数组
        frame_array = np.frombuffer(frame_data, dtype=np.uint8)
        # 将一维数组重新构造成二维图像数组
        frame_image = frame_array.reshape((FrameShape[0], FrameShape[1], 3))
        # 写入帧到视频文件
        out.write(frame_image)

    # 释放视频写入对象
    out.release()



def encodeFromVedio(video_path,RS_NUMBER,chunk_size,segment_len,delimiterChar='M'):
    # 1 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频文件")

    total_frames = -1
    # 读取第一帧作为参考帧
    ret, prev_frame = cap.read()
    if not ret:
        raise ValueError("无法读取视频帧")
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    bytes_arr = bytearray()
    lastframe = np.zeros_like(prev_frame)
    global  FrameShape
    FrameShape = prev_frame.shape

    frame_idx = 0
    while True:
        frame_idx += 1
        # 读取当前帧
        ret, frame = cap.read()
        if not ret:
            break
        # 计算当前帧与上一帧的差分
        diff = frame.astype(np.int8) - lastframe
        points_cnt = 0
        for y in range(diff.shape[0]):
            for x in range(diff.shape[1]):
                if diff[y, x, 0] != 0 or diff[y, x, 1] != 0 or diff[y, x, 2] != 0 or  (x==0 and y==0 ) or (x==diff.shape[1]-1 and  y == diff.shape[0]-1):
                    # 位置用3个字节表示（假设视频帧大小不超过1G像素）
                    pos = y * frame.shape[1] + x
                    bytes_arr.extend(pos.to_bytes(Config.VIDEO_IMGSIZE_BYTE_CNT, 'little'))  # 位置
                    bytes_arr.append(frame[y, x, 0])
                    bytes_arr.append(frame[y, x, 1])
                    bytes_arr.append(frame[y, x, 2])
                    points_cnt += 1
        if(frame_idx % (total_frames // 10) == 0):
            print("encoding ", frame_idx, "/", total_frames, "size:", frame.shape, points_cnt,"......" )
        # if(frame_idx>10):
        #     break
        # 更新参考帧
        lastframe = frame.astype(np.int8)

    cap.release()

    ACGT_str_lists, date_seq_cnt = encodeFromBytes(bytes_arr,RS_NUMBER,chunk_size,segment_len,delimiterChar)
    print("encodeFromVedioAsFrame: 编码后每个序列长", len(ACGT_str_lists[0]),"序列数目：", len(ACGT_str_lists))
    return ACGT_str_lists,date_seq_cnt



## 从ACGT碱基序列转换为原数据内容
def decodeToVedio(output_vedio_path,RS_ACGT_str_lists,RS_NUMBER,Data_seq_cnt,erase_list,chunk_size, image_format='PNG'):
    print("decodeToVedioAsFrame: 序列重构后后每个序列长", len(RS_ACGT_str_lists[0]),"序列数目：", len(RS_ACGT_str_lists))
    bytes_arr = decodeToBytes(RS_ACGT_str_lists,RS_NUMBER, Data_seq_cnt, erase_list,chunk_size)
    print("decodeToVedioAsFrame :", type(bytes_arr), len(bytes_arr))

    # 将Bytes转换为帧
    # 初始化视频帧的数组
    frames = []
    frame = np.zeros((FrameShape[0], FrameShape[1], 3), dtype=np.uint8)
    # 初始化字节序列的索引
    index = 0
    lastpos = 0

    while index < len(bytes_arr)-Config.VIDEO_IMGSIZE_BYTE_CNT-3:
        # 读取位置信息，位置使用3个字节

        pos = int.from_bytes(bytes_arr[index:index + Config.VIDEO_IMGSIZE_BYTE_CNT], 'little')
        index += Config.VIDEO_IMGSIZE_BYTE_CNT
        if(pos<0 or pos >= FrameShape[0] * FrameShape[1]):
            index += 3
            continue
        if(pos == 0  and lastpos >= FrameShape[0] * FrameShape[1] * Config.VIDEO_VALID_END): # 保存一个帧
            frames.append(frame.copy())
        #print(pos,lastpos)
        pos_x = int(pos / FrameShape[1])
        pos_y = int(pos % FrameShape[1])

        if(pos_x < FrameShape[0] and pos_y < FrameShape[1]):
        # 读取三个元素的值，每个通道值使用1个字节
            frame[pos_x,pos_y,0] = bytes_arr[index]
            frame[pos_x,pos_y,1] = bytes_arr[index+1]
            frame[pos_x,pos_y,2] = bytes_arr[index+2]
        index += 3
        lastpos = pos

    frames.append(frame.copy())
    # 将帧数组转换为视频
    print("重构后帧数目:",len(frames),"开始写入视频......")
    out = cv2.VideoWriter(output_vedio_path, cv2.VideoWriter_fourcc(*'mp4v'), min(len(frames),30), (FrameShape[1],FrameShape[0]))
    for frame in frames:
        # cv2.imshow('Frame', frame)
        # time.sleep(2)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        out.write(frame)
    out.release()



def finddataindex(image_path,RS_NUMBER,chunk_size,segment_len,delimiterChar='M'):
    # 1 打开图片,转换为字节流
    with Image.open(image_path) as img:
        # 将图片转换为字节流
        img_array = np.array(img)
        global ImageShape
        ImageShape = img_array.shape
        print("encodeFromImage:图片尺寸",img_array.shape)
    byte_array = img_array.tobytes()
    print("encodeFromImage : 原图片转换为bytes，字节数目",len(byte_array))
    # 1.分割成32长的字节串;对第一个字节串和最后一个字节串进行处理，统一长度为57
    bytes_list = [byte_array[i:i + chunk_size] for i in range(0, len(byte_array), chunk_size)]
    bytes_list.insert(0, bytes(len(byte_array)))

    bytes_len = len(byte_array)
    bytes_list[0] = bytes_len.to_bytes(length=chunk_size, byteorder='little', signed=False)
    bytes_list[-1] = bytes_list[-1] + (' ' * (chunk_size - len(bytes_list[-1]))).encode()
    data_seq_cnt = len(bytes_list)
    print("encodeFromBytes:总数据长度为", bytes_len, "共分割为", data_seq_cnt, "个短字节串数组：", "每个长度为",
          chunk_size)
    Config.Dprint(Config.bytes_list)

    #bytes_list =bytes_list[0:300]
    # 2.RS编码
    RS_bytes_lists = RSencode(bytes_list,RS_NUMBER)
    print("encodeFromBytes:进行RS编码后数组长度为", len(RS_bytes_lists))
    Config.Dprint("RS_bytes_lists：", Config.RS_bytes_lists)

    # bytes_list是原来的数据内容， ebytes现在是对原来的数据内容去进行遍历，求原来数据部分在生成的rs码编码数部分对应的序列下标
    res = []
    cnt = 0
    for ebytes in bytes_list:
        for idx in range(0, len(RS_bytes_lists)):
            if (ebytes ==  RS_bytes_lists[idx]):
                # if(len(res)>1 and idx!=res[-1]+1):
                print("第",cnt,"个序列对应",idx)
                res.append(idx)
                break
        cnt+=1
    # print(len(res),res)
    return res


# finddataindex("D:\Desktop\Dna-encoding\data\Image6.jpg",COnfig.RS_NUMBER,57,57)
