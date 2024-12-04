import numpy as np
from reedsolo import RSCodec
import math
import itertools
import random
from PIL import Image
import io
import os
import time
#字节流形式读取数据
def read_file(file_path,len):
    bytes_list = []
    with open(file_path, 'rb') as file:
        while True:
            content = file.read(len)
            if not content:
                break
            bytes_list.append(content)
    return bytes_list

def write_text(write_path,content):
    with open(write_path,'wb') as file:
        file.write(content)
    print("\n重构序列写入")

#保存图片到指定路径
def image_save(imageBytes,path):
    image=Image.open(io.BytesIO(imageBytes))
    image.show();
    image.save(path)
    print("\n图片保存")

#检查参数设置是否合理
def check(m,t,d):
    if(d<2):
        raise Exception("d应该不小于2")
    if(m<2):
        raise Exception("m应该不小于2")
    if(t < math.ceil(d / 2)):
        raise Exception("t应大于最小距离的一半")

#生成所有n长二元序列
def generate_binary_sequences(n):
  sequences = list(itertools.product([0, 1], repeat=n))
  return np.array(sequences)

#汉明距离计算
def hamming_distance(arr1, arr2):
  if len(arr1) != len(arr2):
    raise ValueError("两个序列的长度必须相同")
  return np.sum(arr1 != arr2)

#threshold,逐位比对置信值
def get_tau(m, t, n, d):
  assert m >= 2
  assert t >= math.ceil(d / 2)
  assert n >= m * (t - math.ceil(d / 2)) + d
  return math.sqrt(8 / d * (m * (m - 1) * t - get_D(n, m, t, 2 * math.ceil(d / 2))) + 1) - m + 1

#论文中D（n.m.t.d)
def get_D(n, m, t, d):
  assert t >= math.ceil(d / 2)
  assert n >= m * (t - math.ceil(d / 2)) + d
  return m * (m - 1) * (t - math.ceil(d / 2)) + math.ceil(m / 2) * math.floor(m / 2) * d

#集合Z两两序列之间汉明距离总和
def sum_of_hammingDistance(Z):
  Z_matrix = np.array([list(map(int, s)) for s in Z])
  m = len(Z_matrix)
  sum = 0
  for i in range(m):
    for j in range(i + 1, m):
      sum += hamming_distance(Z_matrix[i], Z_matrix[j])
  return sum

#z是信道输入，至多发生t个替换错误，返回reads数量为c
def substitution_channel(z, t, c):
  reads = []
  for _ in range(c):
    subs = np.random.randint(0, t + 1)
    read = replace_bits(z, subs)
    reads.append(read)
  return reads

#模拟序列x中发生替换错误
def replace_bits(x, num_replacements):
  indices = np.random.choice(len(x), num_replacements, replace=False)
  new_sequence = list(x)
  for index in indices:
     new_sequence[index] = '1' if x[index] == '0' else '0'
  return ''.join(new_sequence)

#找到符合重构条件的集合，两两序列之间汉明距离之和应该大于threshold
def get_Z(reads, m, threshold):
   random_samples = random.sample(reads, m)
   while sum_of_hammingDistance(random_samples) <= threshold:
       random_samples = random.sample(reads, m)
   return random_samples

#返回一个集合，其中所有序列，S以外下标对应bit跟z相同
def get_U(z, S):
  S = list(S)
  binary_seq = generate_binary_sequences(len(S))
  res_array = np.array([z])
  for bseq in binary_seq:
     u = z
     for ind in range(len(S)):
       u[S[ind]] = bseq[ind]
     res_array = np.append(res_array, [u], axis=0)
  return res_array[1:]


def decode(codeword,ecc):
  #解码时二元序列变成字节形式处理
  codeword=''.join(codeword.astype(str))
  bytes_msg=bytes((int)(codeword[i:i+8],2) for i in range(0,len(codeword),8))
  array_msg = bytearray(bytes_msg)
  data = ecc.decode(array_msg)
  strrr=''.join(format(x, '08b') for x in data[1])
  return np.array(list(map(int, strrr))),data[0]

#核心重构算法
def reconstruction(Z, tau, t,ecc,d):
  m = len(Z)  # m sequences
  n = len(Z[0])  # sequence length
  Z_matrix = np.array([list(map(int, s)) for s in Z])
  S = set()
  z = np.zeros(n)
  for k in range(n):
    m_0 = 0
    m_1 = 0
    for i in range(m):
       if Z_matrix[i, k] == 0:
          m_0 += 1
       elif Z_matrix[i, k] == 1:
          m_1 += 1
    if abs(m_0 - m_1) < tau:
       z[k] = -1
       S.add(k)
    else:
        if m_0 > m_1: z[k] = 0
        elif m_1 > m_0: z[k] = 1
  U = get_U(z, S)
  for u in U:
      u = u.astype(int)
      x, data_0 = decode(u, ecc)
      flag = True
      for z in Z_matrix:
            if (hamming_distance(z, x)) > t: flag = False
      if flag: return ''.join(x.astype(str)), data_0
  #遍历集合U之后没有符合条件的码字，返回None
  return None,None

#RS编码之后以二元序列形式存储
def encode(message, ecc):
  byte_msg = ecc.encode(message)
  binary_code = ''.join(format(x, '08b') for x in byte_msg)
  return binary_code

#保存reads中间结果
def save_Z(Z,z_path):
    with open(z_path,'w') as f:
        for item in Z:
            f.write(f"{item}\n\n")

#读取中间结果，返回一个列表
def read_Z(z_path):
    with open(z_path,'r') as f:
        content=f.read().strip().split('\n\n')
    result_list=[item for item in content if item]
    return result_list


def process(bytes,d,t,m,ecc,z_path):
    x = encode(bytes, ecc)
    n = len(x)
    D = get_D(n, m, t, d)
    tau = get_tau(m, t, n, d)
    c = 500
    reads = substitution_channel(x, t, c)
    Z = get_Z(reads, m, D)
    save_Z(Z,z_path)
    return tau
'''
 file_path 文件路径
 d：码字最小距离
 t：替换球半径
 m：reads数目
'''

# def text_reconstruction(z_path,tau,t,ecc,d):
#     #先读取reads
#     Z=read_Z(z_path)
#     #print(Z)
#     rece, data_0 = reconstruction(Z, tau, t, ecc, d)
#     return data_0




def text_reconstruction(file_Path,d,t,m):
    beginTime = time.time()

    ecc=RSCodec(d)
    z_path = 'z.txt' #存储reads
    byte_lists = read_file(file_Path,40)
    datas = []

    #重构后的文件默认路径
    (filepath, filename) = os.path.split(file_Path)
    write_path = os.path.join(filepath,"reconstruction_" + filename)

    for i in range(len(byte_lists)):
        bytes = byte_lists[i]
        tau = process(bytes, d, t, m, ecc, z_path)
        Z=read_Z(z_path)
        _,data=reconstruction(Z, tau, t, ecc, d)
        datas.append(data)
    write_bytes = b''.join(datas)
    write_text(write_path, write_bytes)

    endTime = time.time()
    time_str = "{:.4f}s".format(endTime - beginTime)
    return  time_str,f"{write_path}"

def image_reconstruction(file_Path,d,t,m):
    beginTime = time.time()
    ecc=RSCodec(d)
    z_path = 'z.txt' #存储reads
    byte_lists = read_file(file_Path,40)
    datas = []

    #重构后的文件默认路径
    (filepath, filename) = os.path.split(file_Path)
    write_path = os.path.join(filepath,"reconstruction_" + filename)

    for i in range(len(byte_lists)):
        bytes = byte_lists[i]
        tau = process(bytes, d, t, m, ecc, z_path)
        Z=read_Z(z_path)
        _,data=reconstruction(Z, tau, t, ecc, d)
        datas.append(data)
    write_bytes = b''.join(datas)
    image_save(write_bytes,write_path)

    endTime = time.time()
    time_str = "{:.4f}s".format(endTime - beginTime)
    return  time_str,f"{write_path}"



def check(m,t,d):
    if(d<2):
        # raise Exception("d应该不小于2")
        return f"m={m},t={t},d={d}, d应该不小于2 "
    if(m<2):
        # raise Exception("m应该不小于2")
        return  f"m={m},t={t},d={d}, m应该不小于2"
    if(t < math.ceil(d / 2)):
        # raise Exception("t应大于最小距离的一半")
        return  f"m={m},t={t},d={d}, t应大于最小距离的一半"
    return  f"pass";



# image_reconstruction("D:\Desktop\Dna-encoding\TestData\Image1.jpg",,t,m):