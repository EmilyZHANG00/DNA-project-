from reedsolo import RSCodec, ReedSolomonError
from .utils import *
from .DNA_BinaryEncoder import DNA_binary_encode, DNA_binary_decode
from .DNA_QaryEncoder import DNA_qary_encode, DNA_qary_decode


def array2image(flattened_array, original_shape):  # 通过imshow函数展示照片
    image_reconstructed = np.reshape(flattened_array, original_shape)
    return image_reconstructed


def image_encode(image_numpy, type=0):
    if type == 0:
        length = Config.SEGMENT_LEN
    else:
        length = (Config.q_SEGMENT_LEN + Config.q_ENCODE_LEN) // 2
    arr = image_numpy.ravel()
    if arr is None:
        print("文件路径无效!")
        sys.exit()
    date_seq_cnt = len(arr)
    # 分段（n段）
    arr_segments = split_segments(arr, length)
    # rs编码（n+k段）
    rs_segments = RS_encode(arr_segments, Config.RS_image)
    # 数组转四进制
    DNA_matrix = byte2DNA_arr(rs_segments)
    if type == 0:
        encode_DNA = DNA_binary_encode(DNA_matrix)
    else:
        encode_DNA = DNA_qary_encode(DNA_matrix)
    return encode_DNA, date_seq_cnt


def image_decode(deleted_DNA, shape, type=0):
    if type == 0:
        length = Config.SEGMENT_LEN
    else:
        length = (Config.q_SEGMENT_LEN + Config.q_ENCODE_LEN) // 2
    if type == 0:
        decode_DNA, result_str = DNA_binary_decode(deleted_DNA)
    else:
        decode_DNA, result_str = DNA_qary_decode(deleted_DNA)
    byte_matrix = DNA2byte_arr(decode_DNA)
    try:
        image_matrix = RS_decode(byte_matrix, Config.RS_image)
    except ReedSolomonError:
        print("rs译码失败！")
        result_str = result_str + "\nrs译码失败！"
        image_matrix = extractInformationFromRS(byte_matrix)
    # 合并多列
    estimate_arr = merge_segments(image_matrix, length)
    modified_arr = estimate_arr[:np.prod(shape)]  # 因为分段的不能整除，最后一个段补0了
    estimate_image = array2image(modified_arr, shape)
    return estimate_image, result_str


def extractInformationFromRS(byte_matrix):
    chunk_size = Config.RS_SIZE
    num_chunks = len(byte_matrix) // chunk_size
    result = []
    for i in range(num_chunks):
        start_row = i * chunk_size
        end_row = start_row + chunk_size
        result.append(byte_matrix[start_row:end_row - Config.RS_image])
    if len(byte_matrix) % chunk_size != 0:
        remaining_rows = byte_matrix[num_chunks * chunk_size:]
        result.append(remaining_rows[:-Config.RS_image])
    return np.vstack(result)
