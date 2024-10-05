import numpy as np
import math
import random


def Syn(y, q):
    """
    Compute Syn(y) = sum(j * y_j).
    """
    return sum(j * y_j for j, y_j in enumerate(y, start=1))


def q_ary_representation(a_prime, q, t):
    """
    Compute the q-ary representation of a_prime.
    """
    z = []
    for i in range(t):
        z.append(a_prime % q)
        a_prime //= q
    return z


def calculate_n(k, q):
    """Calculates the value of n given k and q, satisfying k = n - ceil(log_q n) - 1."""
    for n in range(k + 2, k + 100):  # Start from k+2 and iterate until a solution is found
        if k == n - math.ceil(math.log(n, q)) - 1:
            return n
    return None  # If no solution found within the range


def diff_reverse(x, q):
    c = [0] * len(x)
    for i in range(len(x)):
        c[i] = sum(x[j] for j in range(i, len(x))) % q
    return c


def enc_diff_vt(c, q, a):
    """
    Encodes the message x into VT_a^*(n; q) according to Encoder 2 in the image.
    """
    # convert c from string to list
    x = [int(i) for i in c]

    n = calculate_n(len(x), q)
    t = math.ceil(math.log(n, q))  # Calculate t
    S = {q ** j - 1 for j in range(t)} | {n - 1}  # Set S with powers of q and n-1
    I = sorted(set(range(n)) - S)  # Indices not in S

    # Step II: Fill y
    y = [0] * n
    for i, ix in enumerate(I):
        y[ix] = x[i]

    # Step III: Compute the difference a' and find alpha
    a_prime = (a - Syn(y, q)) % (q * n)
    alpha = a_prime // n
    a_double_prime = a_prime - alpha * n

    # Step IV: Set the values of y for j in S
    y[n - 1] = alpha
    z = q_ary_representation(a_double_prime, q, t)
    for j in range(t):
        y[q ** j - 1] = z[j]

    # Step V: Compute c = Diff^{-1}(y)
    c = diff_reverse(y, q)
    # convert c from list to string
    c = ''.join(str(i) for i in c)
    return c


# obtain the value of the deleted symbol
def get_deleted_symbol(x_prime, q, a):
    return (a - sum(x_prime_i for x_prime_i in x_prime)) % q


def diff(x, q):
    c = [0] * len(x)
    for i in range(len(x) - 1):
        c[i] = (x[i] - x[i + 1]) % q
    c[-1] = x[-1]
    return c


# deletion_correcting
def del_correcting(x_prime, q, a):
    n = len(x_prime) + 1
    gamma = get_deleted_symbol(x_prime, q, a)  # deleted symbol: gamma
    y_prime = diff(x_prime, q)
    Delta = (a - Syn(y_prime, q)) % (q * n)
    s = sum(y_prime[j] for j in range(len(y_prime)))
    y = [0] * n

    if Delta > s and Delta < q + s:
        for j in range(1, n):
            y[j] = x_prime[j - 1]
        y[0] = gamma
        return y

    if Delta <= s:
        for h in range(n - 2, -1, -1):
            if sum(y_prime[h] for h in range(h, n - 1)) > Delta:
                break
        y[h + 1] = gamma
        for j in range(0, h + 1):
            y[j] = x_prime[j]
        for j in range(h + 2, n):
            y[j] = x_prime[j - 1]
        return y

    if Delta >= q + s:
        for h in range(n - 2, -1, -1):
            if q * (h + 1) + sum(y_prime[h] for h in range(h, n - 1)) < Delta:
                break
        y[h + 1] = gamma
        for j in range(0, h + 1):
            y[j] = x_prime[j]
        for j in range(h + 2, n):
            y[j] = x_prime[j - 1]
        return y


def dec_diff_vt(c_prime, q, a):
    c_prime_list = []
    for i in c_prime:
        c_prime_list.append(int(i))
    n = len(c_prime_list) + 1
    c = del_correcting(c_prime_list, q, a)
    y = diff(c, q)
    t = math.ceil(math.log(n, q))
    S = {q ** j - 1 for j in range(t)} | {n - 1}  # Set S with powers of q and n-1
    I = sorted(set(range(n)) - S)  # Indices not in S
    x = [0] * (n - t - 1)
    for i, ix in enumerate(I):
        x[i] = y[ix]

    x = ''.join(str(i) for i in x)
    return x


# test

# prompt: generate random q-ary string
def generate_q_ary_string(length, q):
    """Generates a random q-ary string of the given length."""
    return ''.join(str(random.randint(0, q - 1)) for _ in range(length))


# prompt: generate the single deletion ball of string x
def generate_single_deletion_ball(x):
    """Generates the single deletion ball for a given string x."""
    ball = set()
    for i in range(len(x)):
        ball.add(x[:i] + x[i + 1:])
    return ball


# n = 61
# q = 4
# a = 0
# string = generate_q_ary_string(n, q)
# print("Random q-ary string:", string)
# x = enc_diff_vt(string, q, a)
# print("Encoded message:", x)
# ball = generate_single_deletion_ball(x)
# print("Single deletion ball:", ball)
# dec_ball = set()
# for s in ball:
#     dec_ball.add(dec_diff_vt(s, q, a))  # 译码所有单删错误
# if len(dec_ball) > 1:
#     print("decoding failure")
# else:
#     element, = dec_ball
#     if element == string:
#         print("decoding successfully, original string is:", element)
#     else:
#         print("fail")
