# -*- coding: utf-8 -*-
import wave
import pywt
import random
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


# 对bytes数据进行里所编码
def reedSolomonCoding(Bytes):
    # 双方约定好，这里是RS(8,8)编码
    rsc = RSCodec(8)
    return rsc.encode(Bytes)


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


# 矩阵写入文件
def writeMatrixData(matrix, filename):
    file = open(filename, "w")
    [rows, cols] = matrix.shape
    for i in range(rows):
        for j in range(cols):
            file.write(str(matrix[i][j]))
            file.write(" ")
        file.write("\n")

    file.close()


# 命令行传参
if len(sys.argv) != 3:
    print("")
    print("  Usage: py -3 Hide.py [Carrier audio filepath] [Secret Audio filepath]")
    print("  If you are using python3 only, you can use python Hide.py ... instead.")
    print("")
    exit(-1)
# 对输入进行判断
CarrierAudioFileName = sys.argv[1]
SecretAudioFileName = sys.argv[2]
if os.path.exists(CarrierAudioFileName) == False:
    print("Carrier audio file does not exists! please check again!")
    exit(-1)
if os.path.exists(SecretAudioFileName) == False:
    print("Secret audio file does not exists! please check again!")
    exit(-1)
if (CarrierAudioFileName.endswith('.wav') == False) or (SecretAudioFileName.endswith('.wav') == False):
    print("Wav file only!")
    exit(-1)

# bit数组
CarrierAudioFileBit = openWavFile(CarrierAudioFileName)
print("Open Carrier audio Successfully!")
SecretAudioFileBit = openWavFile(SecretAudioFileName)
print("Open Secret audio Successfully!")

# 一维离散提升小波变换
CL, CH = pywt.dwt(CarrierAudioFileBit, 'haar')
print("Carrier audio DWT Successfully!")

# 对秘密消息数组进行混沌处理
SecretAudioFileBit = logisticChaos(SecretAudioFileBit)
print("Secret audio logistic Successfully!")
# bits字符串转为bytes
SecretAudioFileBytes = bitsToBytes(SecretAudioFileBit)
# 进行里所编码
RSSecretAudioFileBytes = reedSolomonCoding(SecretAudioFileBytes)
# 里所编码最后生成bits数组
RSSecretAudioFileBits = list(bytesToBits(RSSecretAudioFileBytes))
print("Secret audio RS coding Successfully!")

if len(CL) < len(RSSecretAudioFileBits):
    print("Secret audio file is longer than Carrier audio file can carry! Please change one of it!")
    exit(-1)

# D是更新的低频系数D
D = CL.copy()
# K是嵌入强度
K = 0.1
# CL原始长度
CLOriginLength = len(CL)
# 矩阵重构
dim1, dim2 = factorization(CLOriginLength)
CL = CL.reshape(dim1, dim2)

# SVD变换，注意P只记录了奇异值，需要还原
U, P, V = la.svd(CL)
print("SVD for CL Successfully!")

# 随机生成动态嵌入点
q = random.randint(0, CLOriginLength - len(RSSecretAudioFileBits) - 1)

# 低频嵌入
for i in range(len(D)):
    if i < len(RSSecretAudioFileBits):
        D[q + i] = D[q + i] + K * float(RSSecretAudioFileBits[i])
    else:
        break

# 矩阵重构
D = D.reshape(dim1, dim2)

# SVD变换，注意P只记录了奇异值，需要还原
U1, P1, V1 = la.svd(D)
print("SVD for D Successfully!")

P = createMatrix(U.shape[0], V.shape[0], P)
P1 = createMatrix(U1.shape[0], V1.shape[0], P1)

# CL'的有关运算，我命名为CL2
CL2 = np.matmul(U, P1)
CL2 = np.matmul(CL2, V)
# 最后输出CL'
CL2 = CL2.reshape((1, CLOriginLength))
CL2 = np.squeeze(CL2)

# 反小波变换
ReverseDWTData = pywt.idwt(CL2, CH, 'haar')
print("Reverse DWT Successfully!")

# 取整数，载密二进制数组
CarrierAudioFileWithSecretBit = []
for item in ReverseDWTData:
    if item >= 1:
        CarrierAudioFileWithSecretBit.append(1)
    else:
        CarrierAudioFileWithSecretBit.append(0)

CarrierAudioFileWithSecretBit = listToStr(CarrierAudioFileWithSecretBit)

# bits转bytes
CarrierAudioFileWithSecret = bitsToBytes(CarrierAudioFileWithSecretBit)

# 打开WAV
f = wave.open(CarrierAudioFileName[0: len(CarrierAudioFileName) - 4] + "WithSecret.wav", "wb")

# 配置声道数、量化位数和取样频率
f.setnchannels(2)
f.setsampwidth(2)
f.setframerate(44100)
# 将wav_data转换为二进制数据写入文件
f.writeframes(CarrierAudioFileWithSecret)
f.close()
print("New Audio with secret audio write Successfully!")

writeMatrixData(U1, "U1.dat")
writeMatrixData(V1, "V1.dat")
writeMatrixData(P, "P.dat")
