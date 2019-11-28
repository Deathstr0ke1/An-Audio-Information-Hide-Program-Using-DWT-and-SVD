# -*- coding: utf-8 -*-
import wave
import sys
import os
import matplotlib.pyplot as plt
import numpy as np


# 读取音频文件信息
def readWaveData(filepath):
    f = wave.open(filepath, "rb")
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    StrData = f.readframes(nframes)
    f.close()
    
    WaveData = np.frombuffer(StrData, dtype=np.short)

    WaveData.shape = -1, 2

    WaveData = WaveData.T

    time = np.arange(0, nframes) * (1.0 / framerate)
    return WaveData, time


# 命令行传参，分别有两个和三个的情况
if len(sys.argv) == 3:
    # 对输入进行判断
    AudioFileName1 = sys.argv[1]
    AudioFileName2 = sys.argv[2]
    if os.path.exists(AudioFileName1) == False:
        print("audio file 1 does not exists! please check again!")
        exit(-1)
    if os.path.exists(AudioFileName2) == False:
        print("audio file 2 does not exists! please check again!")
        exit(-1)
    if (AudioFileName1.endswith('.wav') == False) or (AudioFileName2.endswith('.wav') == False):
        print("Wav file only!")
        exit(-1)
    WaveData1, time1 = readWaveData(AudioFileName1)
    WaveData2, time2, = readWaveData(AudioFileName2)
    
    time = time1
    WaveData = WaveData1 - WaveData2
    
    plt.subplot(211)
    plt.plot(time, WaveData[0])
    plt.subplot(212)
    plt.plot(time, WaveData[1], c="g")
    plt.savefig("Compare Wav.png")
    print("Output Wav Compare Picture Successfully!")
   
elif len(sys.argv) == 2:
    # 对输入进行判断
    AudioFileName = sys.argv[1]
    if os.path.exists(AudioFileName) == False:
        print("audio file does not exists! please check again!")
        exit(-1)
    if AudioFileName.endswith('.wav') == False:
        print("Wav file only!")
        exit(-1)
    WaveData, time = readWaveData(AudioFileName)
    
    
    plt.subplot(211)
    plt.plot(time, WaveData[0])
    plt.subplot(212)
    plt.plot(time, WaveData[1], c="g")
    plt.savefig(AudioFileName[0: len(AudioFileName) - 4]+".png")
    print("Output Wav Picture Successfully!")

else:
    print("")
    print("  Usage 1: py -3 Wav.py [audio filepath]")
    print("  This will output its image")
    print("  Usage 2: py -3 Wav.py [Audio filepath1] [Audio filepath2]")
    print("  This will output their compare image")
    print("")
    exit(-1)



