# -*- coding: utf-8 -*-
import wave
import pywt
import sys
import os
import numpy as np
from reedsolo import RSCodec
from numpy import linalg as la


# 尤其注意，bits字符串和bits数组的区别，以及bits数组是字符串型还是int型

# bytes转为bits字符串
def bytesToBits(Bytes):
    return ''.join(format(x, '08b') for x in Bytes)


# bits字符串转为bytes
def bitsToBytes(Bits):
    return bytes(int(Bits[i:i + 8], 2) for i in range(0, len(Bits), 8))


# list转为str
def listToStr(List):
    return ''.join([str(x) for x in List])


# 打开一个wav文件，返回bit数组
def openWavFile(Filename):
    File = wave.open(Filename, "rb")
    params = File.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # bytes数据
    StrData = File.readframes(nframes)
    File.close()
    # bit数据
    BinaryWaveData = bytesToBits(StrData)
    # bit数组
    BinaryWaveDataList = list(BinaryWaveData)
    return BinaryWaveDataList


# 读取矩阵信息
def readMatrixData(filename):
    file = open(filename, 'r')
    a = file.read()
    b = a.split('\n')
    # 注意，我的数据多了一行空行在最后
    b.pop()
    for i in range(len(b)):
        b[i] = b[i].split()
        for j in range(len(b[i])):
            b[i][j] = float(b[i][j])

    b = np.array(b)
    return b


# 对bit数组进行logistic混沌，返回二进制字符串
def logisticChaos(BitArray):
    ChaosResult = []
    # logistic混沌初始值
    B = 0.61
    u = 3.90
    for i in BitArray:
        if (B >= 0.5):
            # 1
            ChaosResult.append(int(i) ^ 1)
        else:
            # 0
            ChaosResult.append(int(i) ^ 0)
        B = u * B * (1 - B)

    ChaosResult = listToStr(ChaosResult)
    return ChaosResult


# 重构计算：分解一个大整数，使得其分解为最近的两个整数之和
def factorization(num):
    # 开根号
    sqrt = num ** 0.5
    sqrtInt = int(sqrt)
    # 平方数的情况
    if sqrtInt == sqrt:
        return sqrtInt, sqrtInt
    # 可能的因子
    factor1 = []
    factor2 = []

    for i in range(sqrtInt - int(sqrtInt / 2), sqrtInt):
        for j in range(sqrtInt, sqrtInt + int(sqrtInt / 2)):
            if i * j == num:
                factor1.append(i)
                factor2.append(j)

    min = abs(factor1[0] - factor2[0])
    for i in range(len(factor1)):
        if abs(factor1[i] - factor2[i]) < min:
            min = abs(factor1[i] - factor2[i])
            index = i
    return factor1[index], factor2[index]


# 对奇异值生成对角矩阵
def createMatrix(len1, len2, P):
    # 最小对角
    if len1 < len2:
        minlength = len1
    else:
        minlength = len2

    MatrixP = np.zeros((len1, len2))

    for i in range(minlength):
        MatrixP[i][i] = P[i]

    return MatrixP


# 输入为bits数组，其中内容是int型
def reedSolomonDecoding(Bits):
    # 嵌入点q未知，约定好的RS(8.8)
    rsc = RSCodec(8)
    # 里所编码的性质决定，如果是错误的位置开始，无法解码成功，因此找可能的嵌入位置
    ProperStartLocation = []
    # 可能结尾的位置
    ProperEndLocation = []

    # 全为0无意义，但前一个byte有可能，因此使用枚举
    for i in range(len(Bits)):
        if Bits[i] == 1:
            ProperStartLocation.append(i)
            lastOne = i
            if i > 8:
                for j in range(1, 9):
                    ProperStartLocation.append(i - j)
    # 可能的结束位置
    for i in range(17):
        ProperEndLocation.append(i + lastOne)

    # 用于退出外循环
    flag = 1
    # 枚举并抛出异常，成功后便可解码
    for item in ProperStartLocation:
        if flag == 0:
            break
        for end in ProperEndLocation:
            RealBits = Bits[item:end]
            # 转成16进制
            RealBytes = bitsToBytes(listToStr(RealBits))
            try:
                RSRealBytes = rsc.decode(RealBytes)
                flag = 0
                break
            except:
                continue

    return bytesToBits(RSRealBytes)


# 命令行传参
if len(sys.argv) != 3:
    print("")
    print("  Usage: py -3 Extract.py [Audio filepath] [K]")
    print("  If you are using python3 only, you can use python Extract.py ... instead.")
    print("  Remember to put the U1.dat V1.dat P.dat in the same path with the program!")
    print("")
    exit(-1)

# 对输入进行判断
AudioFileName = sys.argv[1]
K = float(sys.argv[2])

if os.path.exists("U1.dat") == False or os.path.exists("P.dat") == False or os.path.exists("V1.dat") == False:
    print("Matrix data as Key is not complete! please check again!")
    exit(-1)
if os.path.exists(AudioFileName) == False:
    print("Audio file does not exists! please check again!")
    exit(-1)
if K < 0 or K > 1:
    print("K must between 0 and 1")
    exit(-1)

# bit数组
AudioFileBit = openWavFile(AudioFileName)
print("Open Audio Successfully!")

P = readMatrixData("P.dat")
U1 = readMatrixData("U1.dat")
V1 = readMatrixData("V1.dat")
print("Open Matrixes Successfully!")

# 一维离散提升小波变换
CL, CH = pywt.dwt(AudioFileBit, 'haar')
print("Audio DWT Successfully!")

# 升维，平方根升二维
CLOriginLength = len(CL)
dim1, dim2 = factorization(CLOriginLength)
CL = CL.reshape(dim1, dim2)

# SVD变换，注意P只记录了奇异值，需要还原
U2, P2, V2 = la.svd(CL)
print("SVD for CL Successfully!")

P2 = createMatrix(U2.shape[0], V2.shape[0], P2)

D2 = np.matmul(U1, P2)
D2 = np.matmul(D2, V1)

CL2 = np.matmul(U2, P)
CL2 = np.matmul(CL2, V2)

# 最后输出
D2 = D2.flatten()
CL2 = CL2.flatten()
S = (D2 - CL2) / K
print("S is out Successfully!")

# 直接提取出来的bits数组
SecretOriginBits = []

for item in S:
    if abs(item) <= 0.5:
        SecretOriginBits.append(0)
    else:
        SecretOriginBits.append(1)

# RS解码
RealBits = reedSolomonDecoding(SecretOriginBits)
print("RS Decode Successfully!")

# logistic混沌解码
RealBits = logisticChaos(RealBits)
print("Reverse logistic Successfully!")

RealBytes = bitsToBytes(RealBits)
# 打开WAV
f = wave.open(r"Secret Audio.wav", "wb")
# 配置声道数、量化位数和取样频率
f.setnchannels(2)
f.setsampwidth(2)
f.setframerate(44100)
# 将wav_data转换为二进制数据写入文件
f.writeframes(RealBytes)
print("Get Secret Audio Successfully!")
f.close()
