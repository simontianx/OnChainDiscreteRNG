# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 15:16:21 2021
@author: Simon Tian
"""

#%%
from web3 import Web3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import string

import itertools


asciichars = string.ascii_letters + string.punctuation + string.digits;

#%%
def keccak256(val):
    """Compute keccak256 hash with the same algorithm used by Solidity"""
    if type(val) == int:
        return Web3.solidityKeccak(['uint256'], [val]).hex();
    elif type(val) == str:
        return Web3.solidityKeccak(['string'], [val]).hex();

def hashToBinary(hashValue):
    """Convert hashed value of type bytes32 into an array of binary digits in a string"""
    tmp = bin(int(hashValue, 16))[2:];
    prefix = '0' * (256 - len(tmp))
    return prefix + tmp;

def split(binaryArray):
    """Split binary digits into separate digits"""
    return [int(char) for char in binaryArray];

def helper(x):
    """Given an input value x, output an array of binary digits"""
    hashVal = keccak256(x);
    binaryVal = hashToBinary(hashVal);
    arr = split(binaryVal);
    return arr;

def pearson_r(x, y):
    """Compute Pearson correlation coefficient between two arrays."""
    # Compute correlation matrix: corr_mat
    corr_mat = np.corrcoef(x, y)

    # Return entry [0,1]
    return corr_mat[0, 1]

def acf(series):
    """
    http://en.wikipedia.org/wiki/Autocorrelation#Estimation
    """
    n = len(series)
    data = np.asarray(series)
    avg = np.mean(data)
    c0 = np.sum((data - avg) ** 2) / n

    def r(h):
        acf_lag = ((data[:n - h] - avg) * (data[h:] - avg)).sum() / n / c0
        return round(acf_lag, 3)

    # Avoid lag 0 calculation
    x = np.arange(1, 31)
    acf_coeffs = list(map(r, x))
    return acf_coeffs

def drawGraph(df, figId):
    c = 3.725
    # c = 1.96
    plt.figure(figId);
    line_mid, = plt.plot(df[:,0], label='Avg')
    plt.xlabel("Digit Index")
    plt.ylabel("Probability")
    plt.xlim(0, 256)
    plt.ylim(0.46, 0.54)
    plt.hlines(0.5, 0, 256, linestyles='dashed', colors='red')
    line_up, = plt.plot(df[:,0] + c * df[:,1], label="95% CB Upper")
    line_down, = plt.plot(df[:,0] - c * df[:,1], label="95% CB Lower")
    plt.legend(
        handles=(line_up, line_mid, line_down),
        labels=('Upper', 'Avg', 'Lower'),
        loc='lower center',
        ncol=3)


def getStr(m):
    n = np.random.choice(np.arange(2, m));
    sentence = np.random.choice(np.array(list(asciichars)), n);
    return "".join(sentence)


def RogersTanmoto(x1, x2):
    assert(len(x1) == len(x2))
    x3 = x1 ^ x2
    num = np.sum(list(map(lambda x: 0 if x else 1, x3)))
    den = len(x1) + np.sum(x3)
    return num/den


def Correlation(x1, x2):
    assert(len(x1) == len(x2))
    S11 = np.sum(x1 & x2)
    def f(x):
        return np.array(list(map(lambda x: 0 if x else 1, x)))
    S00 = np.sum(f(x1) & f(x2))
    S10 = np.sum(x1 & f(x2))
    S01 = np.sum(f(x1) & x2)
    sigma = np.sqrt((S10+S11)*(S01+S00))*np.sqrt((S11+S01)*(S00+S10))
    num = S11 * S00 - S10 * S01
    return num / sigma

    
def SokalMichener(x1, x2):
    assert(len(x1) == len(x2))
    S11 = np.sum(x1 & x2)
    def f(x):
        return np.array(list(map(lambda x: 0 if x else 1, x)))
    S00 = np.sum(f(x1) & f(x2))
    return (S11 + S00) / len(x1)


#%%
"""
Experiment 1: numerical values
1.1: 0, 1, ..., 10000
1.2: 2^128 + (0, 1, ..., 10000)
Experiment 2: string + numerical values
2.1: "Transaction Number: " + 0, 1, ..., 10000
2.2: "Transaction Number: " + 0, 1, ..., 10000 + 2^128
Experiment 3: Strings
3.1: any permutation and combination of up to 7 ASCII characters
3.2: any permutation and combination of up to 32 ASCII characters
"""

#%%
## Experiment 1
n = 10000
digits_exp1_1 = np.array([helper(int(x)) for x in np.arange(n)]);
rslt_exp1_1 = np.array([(np.mean(digits_exp1_1[:,i]), np.std(digits_exp1_1[:,i])/np.sqrt(n)) for i in np.arange(256)])
drawGraph(rslt_exp1_1, 1)


# 1 point and interval estimation
# 2 independence among outcomes
# 3 independence between inputs and outputs
# 4 autocorrelation

acfs1_1 = list(map(lambda x: acf(x)[1], digits_exp1_1.T))
plt.plot(acfs1_1)


#%%

combinations = np.array(list(itertools.combinations(range(digits_exp1_1.shape[1]), 2)))

results = np.array([])

for i, j in combinations:
    rt = RogersTanmoto(digits_exp1_1[:,i], digits_exp1_1[:,j])
    c = Correlation(digits_exp1_1[:,i], digits_exp1_1[:,j])
    sm = SokalMichener(digits_exp1_1[:,i], digits_exp1_1[:,j])
    row = (i, j, rt, c, sm);
    results = np.append(results, row);


plt.hist(results[2:-1:5], bins=50)
plt.hist(results[3:-1:5], bins=50)
plt.hist(results[4:-1:5], bins=50)


#%%
digits_exp1_2 = np.array([helper(x + 2 ** 128) for x in np.arange(n)]);
rslt_exp1_2 = np.array([(np.mean(digits_exp1_2[:,i]), np.std(digits_exp1_2[:,i])/np.sqrt(n)) for i in np.arange(256)])
drawGraph(rslt_exp1_2, 2)

acfs1_2 = list(map(lambda x: acf(x)[1], digits_exp1_2.T))
plt.plot(acfs1_2)

#%%
## Experiment 2
## 2.1
digits_exp2_1 = np.array([helper("Transaction Number: " + str(x)) for x in np.arange(n)]);
rslt_exp2_1 = np.array([(np.mean(digits_exp2_1[:,i]), np.std(digits_exp2_1[:,i])/np.sqrt(n)) for i in np.arange(256)])
drawGraph(rslt_exp2_1, 3)

#%%
## 2.2
digits_exp2_2 = np.array([helper("Transaction Number: " + str(x + 2 ** 128)) for x in np.arange(n)]);
rslt_exp2_2 = np.array([(np.mean(digits_exp2_2[:,i]), np.std(digits_exp2_2[:,i])/np.sqrt(n)) for i in np.arange(256)])
drawGraph(rslt_exp2_2, 4)

#%%
## Experiment 3
## 3.1
digits_exp3_1 = np.array([helper(getStr(7)) for x in np.arange(n)]);
rslt_exp3_1 = np.array([(np.mean(digits_exp3_1[:,i]), np.std(digits_exp3_1[:,i])/np.sqrt(n)) for i in np.arange(256)])
drawGraph(rslt_exp3_1, 5)

#%%
## 3.2
digits_exp3_2 = np.array([helper(getStr(32)) for x in np.arange(n)]);
rslt_exp3_2 = np.array([(np.mean(digits_exp3_2[:,i]), np.std(digits_exp3_2[:,i])/np.sqrt(n)) for i in np.arange(256)])
drawGraph(rslt_exp3_2, 6)