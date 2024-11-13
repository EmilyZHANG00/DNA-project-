import matplotlib.pyplot as plt
import numpy as np
from reedsolo import RSCodec
import math
import itertools
import random
from PIL import Image
import io
import time
import os

#字节流形式读取文本
def read_text(text_path):
    bytes_list=[]
    with open(text_path,'rb') as file:
    #with open(text_path, 'r', encoding='utf-8') as file:
      while True:
        content=file.read(40)
        if not content:
            break
        bytes_list.append(content)
    #print(bytes_list)
    #print(len(bytes_list))
    return bytes_list

def write_text(write_path,content):
    with open(write_path,'wb') as file:
        file.write(content)
    print("\n重构序列写入")

#字节流形式读取图片
def read_image(image_path):
    byte_lists=[]
    with open(image_path,'rb') as image_file:
        while True:
          image_bytes=image_file.read(40)
          if not image_bytes:
              break
          byte_lists.append(image_bytes)
    print(len(byte_lists))
    return byte_lists

def image_save(imageBytes,path):
    image=Image.open(io.BytesIO(imageBytes))
    image.save(path)

#生成所有n长二元序列
def generate_binary_sequences(n):
  sequences = list(itertools.product([0, 1], repeat=n))
  return np.array(sequences)

#汉明距离计算
def hamming_distance(arr1, arr2):
  if len(arr1) != len(arr2):
    raise ValueError("两个序列的长度必须相同")
  return np.sum(arr1 != arr2)

#返回一个集合，其中所有序列，不在S中的下标处的比特跟z相同
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
  #print(len(U))
  for u in U:
      u = u.astype(int)
      x, data_0 = decode(u, ecc)
      flag = True
      for z in Z_matrix:
            if (hamming_distance(z, x)) > t: flag = False
      if flag: return ''.join(x.astype(str)), data_0
  return None,None



def decode(codeword,ecc):
  #解码时二元序列变成字节形式处理
  codeword=''.join(codeword.astype(str))
  bytes_msg=bytes((int)(codeword[i:i+8],2) for i in range(0,len(codeword),8))
  array_msg = bytearray(bytes_msg)
  data = ecc.decode(array_msg)
  strrr=''.join(format(x, '08b') for x in data[1])
  return np.array(list(map(int, strrr))),data[0]

#threshold
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

#集合Z两两序列之间汉明距离之和
def sum_of_hammingDistance(Z):
  Z_matrix = np.array([list(map(int, s)) for s in Z])
  m = len(Z_matrix)
  n = len(Z_matrix[0])
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

#找到符合重构条件的集合，两两序列之间汉明距离之和应该大于D
def get_Z(reads, m, threshold):
   random_samples = random.sample(reads, m)
   while sum_of_hammingDistance(random_samples) < threshold:
       random_samples = random.sample(reads, m)
   return random_samples

#RS编码，以二元序列形式存储
def encode(message, ecc):
  byte_msg = ecc.encode(message)
  binary_code = ''.join(format(x, '08b') for x in byte_msg)
  return binary_code

#字节流变成二元序列
def bytes_to_binary(s):
    return ''.join(format(ord(char),'08b') for char  in s)

#二元序列转字节流
def binary_to_bytes(b):
    chars = [chr(int(b[i:i+8],2)) for i in range(0,len(b),8)]
    return ''.join(chars)

#保存reads,
def save_Z(Z,z_path):
    with open(z_path,'w') as f:
        for item in Z:
            f.write(f"{item}\n\n")

#读取，返回一个列表
def read_Z(z_path):
    with open(z_path,'r') as f:
        content=f.read().strip().split('\n\n')
    result_list=[item for item in content if item]
    return result_list


def text_process(message,d,t,m,ecc,z_path):
    x = encode(message, ecc)
    n = len(x)
    #if ind==1: print(n)
    D = get_D(n, m, t, d)
    tau = get_tau(m, t, n, d)
    c = 500
    reads = substitution_channel(x, t, c)
    Z = get_Z(reads, m, D)
    #print("用于重构序列的集合：", Z)
    save_Z(Z,z_path)
    return tau

def text_reconstruction(z_path,tau,t,ecc,d):
    #先读取reads
    Z=read_Z(z_path)
    #print(Z)
    rece, data_0 = reconstruction(Z, tau, t, ecc, d)
    return data_0
    #write_text(write_path, data_0.decode('utf-8', errors='ignore'))

def image_process(ima_bytes,d,t,m,ecc ,z_path):
    # image_bytes=read_image(ima_path)
    # d = int(input("码的最小距离d(>=2):"))
    # assert d >= 2
    # t = int(input("错误球半径t: "))
    # assert t >= math.ceil(d / 2)
    # m = int(input("用于重构的序列数量m:"))
    # assert m >= 2
    # ecc = RSCodec(d)
    x = encode(ima_bytes, ecc)
    n = len(x)
    #print(n)
    D = get_D(n, m, t, d)
    tau = get_tau(m, t, n, d)
    c = 1000
    reads = substitution_channel(x, t, c)
    Z = get_Z(reads, m, D)
    #print("用于重构序列的集合：", Z)
    print("Z")
    save_Z(Z, z_path)
    return tau

def image_reconstruction(z_path,tau,t,ecc,d):
    Z = read_Z(z_path)
    rece, data_0 = reconstruction(Z, tau, t, ecc, d)
    return data_0
    #image_save(data_0,write_path)

def video_read(video_path):
    with open(video_path,'rb') as video_file:
        video_bytes=video_file.read()
    return video_bytes

def video_save(vbytes,write_path):
    with open(write_path,'wb') as video_file:
        video_file.write(vbytes)

def video_process(video_path,z_path):
    video_bytes=video_read(video_path)
    d = int(input("码的最小距离d(>=2):"))
    assert d >= 2
    t = int(input("错误球半径t: "))
    assert t >= math.ceil(d / 2)
    m = int(input("用于重构的序列数量m:"))
    assert m >= 2
    ecc = RSCodec(d)
    x = encode(video_bytes, ecc)
    n = len(x)
    D = get_D(n, m, t, d)
    tau = get_tau(m, t, n, d)
    c = 1000
    reads = substitution_channel(x, t, c)
    Z = get_Z(reads, m, D)
    print("用于重构序列的集合：", Z)
    save_Z(Z, z_path)
    return tau, t, ecc, d

def video_reconstruction(z_path,tau,t,ecc,d,write_path):
    Z = read_Z(z_path)
    rece, data_0 = reconstruction(Z, tau, t, ecc, d)
    video_save(data_0,write_path)

def leven_recons_thres(n,t,q=2):
    N=1
    for i in range(0,t):
        N=N+math.comb(n-1,i)
    return N

def substitution_reconstruction(file_Path,d,t,m):
    ecc=RSCodec(d)
    z_path = 'z.txt'
    byte_lists = read_text(file_Path)
    datas = []
    #重构后的文件默认路径
    (filepath, filename) = os.path.split(file_Path)
    write_path = os.path.join(filepath,"reconstruction_" + filename)

    for i in range(len(byte_lists)):
        message = byte_lists[i]
        tau = text_process(message, d, t, m, ecc, z_path)
        datas.append(text_reconstruction(z_path, tau, t, ecc, d))
    write_bytes = b''.join(datas)
    write_text(write_path, write_bytes)
    return "重构结果已经保存至{write_path}\n"

def check(m,t,d):
    if(d<2):
        raise Exception("d应该不小于2")
        return "d应该不小于2"
    if(m<2):
        raise Exception("m应该不小于2")
        return "m应该不小于2"
    if(t < math.ceil(d / 2)):
        raise Exception("t应大于最小距离的一半")
        return "t应大于最小距离的一半"
    return "pass"

if __name__ == '__main__':
    #print(leven_recons_thres(400,15))
    # file_Path=str(input("文本文件路径:"))
    # d = int(input("码的最小距离d(>=2):"))
    # #assert d >= 2
    # t = int(input("错误球半径t: "))
    # #assert t >= math.ceil(d / 2)
    # m = int(input("用于重构的序列数量m:"))
    file_Path = r"D:\Desktop\Dna-encoding\test\test.txt"
    d=2
    t=3
    m=10
    print(check(m,t,d))
    '''
    file_path文件路径
    d：RS码的最小距离
    t：替换球半径
    m： reads数量
    重构后的文件默认路径：write_path = 'reconstruction_' + file_Path
    '''
    substitution_reconstruction(file_Path,d,t,m)




    # ecc = RSCodec(d)
    # #也可以输入啦
    # #file_Path = 'm.txt'
    # z_path = 'z.txt'
    # byte_lists = read_text(file_Path)
    # datas = []
    # start=time.perf_counter();
    # write_path='reconstruction_'+file_Path
    # for i in range(len(byte_lists)):
    #     message=byte_lists[i]
    #     tau=text_process(message,d,t,m,ecc,z_path)
    #     datas.append(text_reconstruction(z_path,tau,t,ecc,d))
    #     a = "*" * i
    #     b = "." * (len(byte_lists) - i)
    #     c = (i / len(byte_lists)) * 100
    #     dur = time.perf_counter() - start
    #     print("\r[{}->{}]{:.2f}s".format( a, b, dur), end="")
    #     #print("\r[{}->{}]".format( a, b), end="")
    #     time.sleep(0.1)
    # write_bytes=b''.join(datas)
    # write_text(write_path,write_bytes)


    # image_path='Image1.jpg'
    # write_path='test.jpg'
    # ima_bytes=read_image(image_path)
    # datas=[]
    # for bts in ima_bytes:
    #     tau=image_process(bts,d,t,m,ecc,'z.txt')
    #     datas.append(image_reconstruction('z.txt',tau,t,ecc,d,write_path))
    # write_bytes=b''.join(datas)
    # image_save(write_bytes,write_path)

    # file_Path = 'cube.mp4'
    # z_path = 'z.txt'
    # tau, t, ecc, d = video_process(file_Path, z_path)
    # video_reconstruction(z_path, tau, t, ecc, d, write_path='ican.mp4')
