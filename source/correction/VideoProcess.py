import cv2
import numpy as np
from . import ImageProccess
import sys
from reedsolo import RSCodec, ReedSolomonError
from .utils import *
from .DNA_BinaryEncoder import DNA_binary_encode, DNA_binary_decode
from .DNA_QaryEncoder import DNA_qary_encode, DNA_qary_decode


def video_encode(cap, type=0):
    total_frames = -1
    # 读取第一帧作为参考帧
    ret, frame = cap.read()
    if not ret:
        raise ValueError("无法读取视频帧")
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_shape = frame.shape
    bytes_arr = bytearray()
    lastframe = np.zeros_like(frame)

    frame_idx = 0
    while True:
        frame_idx += 1
        # 计算当前帧与上一帧的差分
        diff = frame.astype(np.int8) - lastframe
        points_cnt = 0
        for y in range(diff.shape[0]):
            for x in range(diff.shape[1]):
                if diff[y, x, 0] != 0 or diff[y, x, 1] != 0 or diff[y, x, 2] != 0 or (x == 0 and y == 0) or (
                        x == diff.shape[1] - 1 and y == diff.shape[0] - 1):
                    # 位置用3个字节表示（假设视频帧大小不超过1G像素）
                    pos = y * frame.shape[1] + x
                    bytes_arr.extend(pos.to_bytes(config.VIDEO_IMGSIZE_BYTE_CNT, 'little'))  # 位置
                    bytes_arr.append(frame[y, x, 0])
                    bytes_arr.append(frame[y, x, 1])
                    bytes_arr.append(frame[y, x, 2])
                    points_cnt += 1
        if (frame_idx % 10 == 0):
            print("encoding ", frame_idx, "/", total_frames, "size:", frame.shape, points_cnt, "......")
        # 更新参考帧
        lastframe = frame.astype(np.int8)
        # 读取下一帧
        ret, frame = cap.read()
        if not ret:
            break
    cap.release()

    if type == 0:
        length = config.SEGMENT_LEN
    else:
        length = (config.q_SEGMENT_LEN + config.q_ENCODE_LEN) // 2
    date_seq_cnt = len(bytes_arr)
    arr_segments = split_segments(bytes_arr, length)
    print("分段成功")
    # rs编码（n+k段）
    rs_segments = RS_encode(arr_segments, config.RS_video)
    print("RS成功")
    DNA_matrix = byte2DNA_arr(rs_segments)
    print("转DNA成功")
    if type == 0:
        encode_DNA = DNA_binary_encode(DNA_matrix)
    else:
        encode_DNA = DNA_qary_encode(DNA_matrix)
    return encode_DNA, date_seq_cnt, frame_shape


def video_decode(deleted_DNA, n, frame_shape, type=0):
    if type == 0:
        length = config.SEGMENT_LEN
    else:
        length = (config.q_SEGMENT_LEN + config.q_ENCODE_LEN) // 2
    if type == 0:
        decode_DNA = DNA_binary_decode(deleted_DNA)
    else:
        decode_DNA = DNA_qary_decode(deleted_DNA)
    byte_matrix = DNA2byte_arr(decode_DNA)
    # rs译码
    try:
        video_matrix = RS_decode(byte_matrix, config.RS_video)
        flag = True
    except ReedSolomonError:
        print("rs译码失败！")
        flag = False
        video_matrix = extractInformationFromRS(byte_matrix)
    # 合并多列
    estimate_arr = merge_segments(video_matrix, length)
    bytes_arr = estimate_arr[:n]  # 因为分段的不能整除，最后一个段补0了

    VIDEO_IMGSIZE_BYTE_CNT = config.VIDEO_IMGSIZE_BYTE_CNT
    VIDEO_VALID_END = config.VIDEO_VALID_END
    frames = []
    frame = np.zeros((frame_shape[0], frame_shape[1], 3), dtype=np.uint8)
    # 初始化字节序列的索引
    index = 0
    lastpos = 0

    while index < len(bytes_arr) - VIDEO_IMGSIZE_BYTE_CNT - 3:
        # 读取位置信息，位置使用3个字节
        pos = int.from_bytes(bytes_arr[index:index + VIDEO_IMGSIZE_BYTE_CNT], 'little')
        index += VIDEO_IMGSIZE_BYTE_CNT
        if (pos < 0 or pos >= frame_shape[0] * frame_shape[1]):
            index += 3
            continue
        if (pos == 0 and lastpos >= frame_shape[0] * frame_shape[1] * VIDEO_VALID_END):  # 保存一个帧
            frames.append(frame.copy())
        # print(pos,lastpos)
        pos_x = int(pos / frame_shape[1])
        pos_y = int(pos % frame_shape[1])

        if (pos_x < frame_shape[0] and pos_y < frame_shape[1]):
            # 读取三个元素的值，每个通道值使用1个字节
            frame[pos_x, pos_y, 0] = bytes_arr[index]
            frame[pos_x, pos_y, 1] = bytes_arr[index + 1]
            frame[pos_x, pos_y, 2] = bytes_arr[index + 2]
        index += 3
        lastpos = pos
    frames.append(frame.copy())
    return frames, flag


def extractInformationFromRS(byte_matrix):
    chunk_size = config.RS_SIZE
    num_chunks = len(byte_matrix) // chunk_size
    result = []
    for i in range(num_chunks):
        start_row = i * chunk_size
        end_row = start_row + chunk_size
        result.append(byte_matrix[start_row:end_row - config.RS_video])
    if len(byte_matrix) % chunk_size != 0:
        remaining_rows = byte_matrix[num_chunks * chunk_size:]
        result.append(remaining_rows[:-config.RS_video])
    return np.vstack(result)
