# ResConfig.py
DEL_NUM = 1  # 平均每个序列的删除个数
SEGMENT_LEN = 54
ENCODE_LEN = 60
CHUNK_SIZE = SEGMENT_LEN  # 一个序列中每个段的长度大小（单位为bytes） = 每个碱基序列中segments长度 (1bytes = 8bit = 4碱基)
RS_NUMBER = 10  # 生成RS冗余序列数目
delimiterChar = 'M'
modulo = 61
Belta = 0
Gamma = 0
