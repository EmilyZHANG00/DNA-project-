

CLUSTER_LOSS_RATE = 0.001   # 簇丢失率
BASE_LOSS_RATE  = 0.01    # 碱基丢失率
CLUSTER_SIZE = 20         # 每个簇的平均大小


# RS码
RS_ENCODE_VALID = True   # 是否启用RS编码
RS_NUMBER =40         # 生成RS冗余序列数目
RS_FIELD_SIZE = 255
# DEL_NUM = 5            # 平均每个序列的删除个数

SEGMENT_LEN = 57
CHUNK_SIZE = SEGMENT_LEN       # 一个序列中每个段的长度大小（单位为bytes） = 每个碱基序列中segments长度 (1bytes = 8bit = 4碱基)
delimiterChar = 'M'
DEBUG = False
ImageShape = (1,1,1)


#VT编码部分
VT_REDANDANT=6
VT_CODE_LEN=63
VT_M=64
VT_SYNDROME=2



#视频编码参数
VIDEO_IMGSIZE_BYTE_CNT = 3
VIDEO_VALID_END = 0.9


outputinfo_path=r"outputinfo.txt"

def Dprint(*args, **kwargs):
    """一个重载的print函数，可以通过全局变量控制是否输出内容。"""
    global DEBUG
    if DEBUG:
        print(*args, **kwargs)


def FilePrint(message):
    # 使用'a'模式打开文件，这将以追加模式打开文件
    with open(outputinfo_path, 'w') as file:
        # 将信息写入文件
        file.write(message)  # 添加换行符以便于阅读