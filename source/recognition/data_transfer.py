from reedsolo import RSCodec



CLUSTER_SIZE = 10       # 每个簇的平均大小
DEL_NUM = 1             # 平均每个序列的删除个数
SEGMENT_LEN = 57
CHUNK_SIZE = SEGMENT_LEN       # 一个序列中每个段的长度大小（单位为bytes） = 每个碱基序列中segments长度 (1bytes = 8bit = 4碱基)
RS_NUMBER = 8          # 生成RS冗余序列数目
delimiterChar = 'M'

rsc = RSCodec(RS_NUMBER)

def RSencode(origin_bytes_list):
    rs_col_byte_arr_list=[]
    for col in range(0,len(origin_bytes_list[0])):
        """创建新的n长字节串并进行RS编码"""
        col_byte_arr = bytearray()
        for byte_str in origin_bytes_list:
            col_byte_arr.append(byte_str[col])
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
def RSdecode(rs_bin_str_lists,Data_seq_cnt):
    # 01字符串转换为bytes 字节串
    rs_bytes_lines = []
    for rs_bin_str in rs_bin_str_lists:
        bytes_from_binary = bytes([int(rs_bin_str[i:i + 8], 2) for i in range(0, len(rs_bin_str), 8)])
        rs_bytes_lines.append(bytes_from_binary)

    col_bytestr_list = []
    for col in range(0,len(rs_bytes_lines[0])):
        """按列进行RS解码"""
        col_k_rs_bytes_arr = bytearray()
        for bytes_str in rs_bytes_lines:
            col_k_rs_bytes_arr.append(bytes_str[col])
        # RS解码
        try:
            repaired_message, repaired_message_with_ecc, additional_info = rsc.decode(col_k_rs_bytes_arr)
            # print("RS解码后的消息:", repaired_message)
            # print("修复后的消息 + ECC:", repaired_message_with_ecc)
            # print("附加信息:", additional_info)
            col_bytestr_list.append(repaired_message)

        except ValueError as e:
            print("解包错误:", e)
            return rs_bytes_lines[:Data_seq_cnt]
        except Exception as e:
            print("其他错误:", e)
            return rs_bytes_lines[:Data_seq_cnt]

    origin_byte_arr_lines = []
    for row in range(0,len(col_bytestr_list[0])):
        origin_bytes = bytearray()
        for col_k_bytestr in col_bytestr_list:
            origin_bytes.append(col_k_bytestr[row])
        origin_byte_arr_lines.append(origin_bytes)
    return origin_byte_arr_lines



## 编码流程:文本->二进制序列->RS编码->碱基序列
def encodeFromText(original_text,chunk_size=57,segment_len=57,delimiterChar='M'):
    # 1.变成bytes类型  字节串
    utf8_bytes = original_text.encode('utf-8')
    print("1 编码为字节串内容:",type(utf8_bytes),len( utf8_bytes),utf8_bytes)

    # 2.分割成32长的字节串;对第一个字节串和最后一个字节串进行处理，统一长度为57
    bytes_list = [utf8_bytes[i:i + chunk_size] for i in range(0, len(utf8_bytes), chunk_size)]
    bytes_list.insert(0,bytes(len(utf8_bytes)))


    bytes_len = len(utf8_bytes)
    bytes_list[0] = bytes_len.to_bytes(length=chunk_size, byteorder='little', signed=False)
    bytes_list[-1] = bytes_list[-1] + (' '*(chunk_size-len(bytes_list[-1] ))).encode()
    date_seq_cnt = len(bytes_list)
    print("2 分割为短字节串数组： " , bytes_len,bytes_list)


    # 3.RS编码
    RS_bytes_lists = RSencode(bytes_list)
    print("3: 对字节串并进行RS编码：", RS_bytes_lists)


    # 4 bytes变成01序列，再进一步变成碱基
    conversion = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
    ACGT_str_lists=[]
    for bytestr  in  RS_bytes_lists:
        binstr=''.join(format(byte, '08b') for byte in bytestr)
        ACGT_str=''
        for i in range(0,len(binstr),2):
            ACGT_str += conversion[binstr[i:i+2]]
        ACGT_str_lists.append(ACGT_str)
    print("4：原数据信息对应的碱基数目为:",len(bytes_list),"经过RS编码后总碱基序列数目为",len(ACGT_str_lists),"碱基序列内容：",ACGT_str_lists)

    # 5.添加分隔符
    for i in range(0,len(ACGT_str_lists)):
        str = ACGT_str_lists[i]
        result_str=''
        result_str = str[0:segment_len]
        for idx in range(segment_len,len(str), segment_len):
            result_str += delimiterChar+str[idx:idx+segment_len]
        ACGT_str_lists[i] = result_str
    return ACGT_str_lists,date_seq_cnt


## 从ACGT碱基序列转换为原数据内容
def decodeToText(RS_ACGT_str_lists,Data_seq_cnt,chunk_size=57):
    # 1.转换为01序列
    conversion = {'A':'00', 'C':'01','G':'10', 'T':'11'}
    bin_str_lists = []
    for str in RS_ACGT_str_lists:
        bin_str = ''
        for  ch in str:
            bin_str += conversion[ch]
        bin_str_lists.append(bin_str)
    print("1 二进制字符串序列：",bin_str_lists)

    # 2.01序列转换为字节串，并进行RS解码
    bytes_list = RSdecode(bin_str_lists,Data_seq_cnt)
    print("2 RS解码后字节串内容：", bytes_list)

    # 3.求出第一个字节序所代表的内容（也就是数据总长度）
    total_len = int.from_bytes(bytes_list[0], byteorder = 'little', signed = False)
    print("3 解码出原序列总字节数目为:",type(total_len), total_len)


    # 4.拼接得到原始数据对应的字节串
    bytes_str = bytearray()
    for i in range(1,len(bytes_list)-1):
        bytes_str += bytes_list[i]
    bytes_str += bytes_list[len(bytes_list)-1][:(total_len % chunk_size)]
    print("4 二进制字节串内容：" ,bytes_str,total_len % chunk_size)

    # 5.尝试恢复原始数据
    try:
        restored_text = bytes_str.decode('utf-8')
        print(f"5 恢复后的文本: {restored_text}")
    except UnicodeDecodeError as e:
        print("[ ######## 解码失败,错误过多，无法恢复原信息! #########] details:",e)
        return ""



## 编码流程:文本->二进制序列->RS编码->碱基序列
def encodeFromImage(image_path,chunk_size=57,segment_len=57,delimiterChar='M'):
    print("encodeFromImage")


## 从ACGT碱基序列转换为原数据内容
def decodeToImage(RS_ACGT_str_lists,Data_seq_cnt,chunk_size = 57):
    print("decodeToImage")
