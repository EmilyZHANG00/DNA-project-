


CLUSTER_LOSS_RATE = 0.001   # 簇丢失率
BASE_LOSS_RATE  = 0.005    # 碱基丢失率
CLUSTER_SIZE = 5         # 每个簇的平均大小
RS_NUMBER = 50          # 生成RS冗余序列数目
# DEL_NUM = 5            # 平均每个序列的删除个数

SEGMENT_LEN = 57
CHUNK_SIZE = SEGMENT_LEN       # 一个序列中每个段的长度大小（单位为bytes） = 每个碱基序列中segments长度 (1bytes = 8bit = 4碱基)
delimiterChar = 'M'
DEBUG = False
ImageShape = (1,1,1)


print("ifififif")