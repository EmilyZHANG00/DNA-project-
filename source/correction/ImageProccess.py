from reedsolo import RSCodec, ReedSolomonError
from .utils import *
from .DNA_BinaryEncoder import DNA_binary_encode, DNA_binary_decode
from .DNA_QaryEncoder import DNA_qary_encode, DNA_qary_decode


def array2image(flattened_array, original_shape):  # 通过imshow函数展示照片
    image_reconstructed = np.reshape(flattened_array, original_shape)
    return image_reconstructed


def image_encode(image_numpy, type=0):
    if type == 0:
        length = config.SEGMENT_LEN
    else:
        length = (config.q_SEGMENT_LEN + config.q_ENCODE_LEN) // 2
    arr = image_numpy.ravel()
    if arr is None:
        print("文件路径无效!")
        sys.exit()
    # 分段（n段）
    arr_segments = split_segments(arr, length)
    # rs编码（n+k段）
    rs_segments = RS_encode(arr_segments)
    # 数组转四进制
    quaternary_matrix_1 = byte2quaternary_matrix(rs_segments)
    # 转DNA序列
    DNA_matrix = quaternary2DNA_matrix(quaternary_matrix_1)
    # 对DNA序列编码（结果含人工碱基）
    if type == 0:
        encode_DNA = DNA_binary_encode(DNA_matrix)
    else:
        encode_DNA = DNA_qary_encode(DNA_matrix)
    return encode_DNA


def image_decode(deleted_DNA, shape, type=0):
    if type == 0:
        length = config.SEGMENT_LEN
    else:
        length = (config.q_SEGMENT_LEN + config.q_ENCODE_LEN) // 2
    if type == 0:
        decode_DNA = DNA_binary_decode(deleted_DNA)
    else:
        decode_DNA = DNA_qary_decode(deleted_DNA)
    # print(np.array_equal(decode_DNA, DNA_matrix))
    quaternary_matrix = DNA2quaternary_matrix(decode_DNA)
    # 四进制转数组
    byte_matrix = quaternary2byte_matrix(quaternary_matrix)
    # rs译码
    try:
        image_matrix = RS_decode(byte_matrix)
        flag = True
    except ReedSolomonError:
        print("rs译码失败！")
        flag = False
        image_matrix = extractInformationFromRS(byte_matrix)
    # 合并多列
    estimate_arr = merge_segments(image_matrix, length)
    modified_arr = estimate_arr[:np.prod(shape)]  # 因为分段的不能整除，最后一个段补0了
    estimate_image = array2image(modified_arr, shape)
    return estimate_image, flag


def extractInformationFromRS(byte_matrix):
    chunk_size = config.RS_SIZE
    num_chunks = len(byte_matrix) // chunk_size
    result = []
    for i in range(num_chunks):
        start_row = i * chunk_size
        end_row = start_row + chunk_size
        result.append(byte_matrix[start_row:end_row - config.RS_image])
    if len(byte_matrix) % chunk_size != 0:
        remaining_rows = byte_matrix[num_chunks * chunk_size:]
        result.append(remaining_rows[:-config.RS_image])
    return np.vstack(result)
