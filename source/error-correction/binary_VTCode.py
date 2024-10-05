import numpy as np

REDANDANT = 6
CODE_LEN = 60
M = 61


def _compute_syndrome(m: 64, SYN, array_y):
    len_y = array_y.size
    return np.mod(SYN - np.sum((1 + np.arange(len_y)) * array_y), m)


def _is_codeword(y, SYNDROME):
    if y is None or y.size != CODE_LEN:
        return False
    return _compute_syndrome(M, SYNDROME, y) == 0


# 57长input  63长output
def vt_encode(message, SYNDROME):
    x = message
    # 消息长度57？冗余位6
    parity_positions = np.zeros(REDANDANT, dtype=np.int64)
    for i in range(REDANDANT):
        parity_positions[i] = np.power(2, i)
    systematic_positions = np.setdiff1d(np.arange(1, CODE_LEN + 1), parity_positions)
    # print(systematic_positions)
    # print(parity_positions)
    y = np.zeros(CODE_LEN, dtype=np.int64)
    # first set systematic positions
    y[systematic_positions - 1] = x
    syn = _compute_syndrome(M, SYNDROME, y)
    if syn != 0:
        for pos in reversed(parity_positions):
            if syn >= pos:
                y[pos - 1] = 1
                syn -= pos
                if syn == 0:
                    break
    assert _is_codeword(y, SYNDROME)
    return y


def vt_decode(codeword, SYNDROME):
    '''
    y:n-1 length
    a:VT syndrome,default 0
    return codeword x with length n
    '''
    assert len(codeword) == CODE_LEN - 1
    d = codeword
    n = CODE_LEN
    a = SYNDROME
    n = len(d) + 1
    ones_indices = np.where(d == 1)[0] + 1
    zero_indices = np.where(d == 0)[0] + 1
    sum = np.sum(ones_indices) % (n + 1)
    diff = (a + n + 1 - sum) % (n + 1)
    ones = np.sum(d == 1)  # 11
    if diff == 0:
        array_x = np.insert(d, n - 1, 0)
    elif diff <= ones:
        pos = ones_indices[ones - diff] - 1
        array_x = np.insert(d, pos, 0)
    elif ones < diff and diff < n:
        pos = zero_indices[diff - ones - 1] - 1
        array_x = np.insert(d, pos, 1)
    else:
        array_x = np.insert(d, n - 1, 1)
    return np.array(list(_remove_redundant_bits(array_x)), dtype=np.int64)


def _remove_redundant_bits(array_x):
    parity_positions = np.zeros(REDANDANT, dtype=np.int64)
    for i in range(REDANDANT):
        parity_positions[i] = np.power(2, i)
    codeword_str = ''
    for i in range(len(array_x)):
        if i + 1 not in parity_positions:
            codeword_str += str(array_x[i])
    return codeword_str


if __name__ == "__main__":
    message = np.array(
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    print(message)
    codeword = vt_encode(message, 45)
    print(codeword)
    codeword = np.delete(codeword, 29)
    print(codeword)
    print(vt_decode(codeword, 45) == message)
    # codeword = "10010110100000000000001100000000001000000000000000000000000000"
    # print(vt_decode(codeword, 0))
    # print(message)
    # dele_one_code="10000010000000000000001100000010001000000000000000000000000000"
    # #print(len(dele_one_code))
    # decoded=vt_decode(dele_one_code)
    # print(decoded)
    # print(message)
