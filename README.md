# An Audio Information Hide Program Using DWT and SVD
# 基于离散小波变换和奇异值分解的音频信息隐藏
本程序完成了一个音频信息隐藏的功能，其中涉及到Logistic混沌、里所（RS）编码、一维离散提升小波变换（haar）、奇异值分解（SVD）

需要的Python包有

- PyWavelets
- reedsolo

因此只需要在CMD命令行中首先使用

```shell
pip3 install PyWavelets
pip3 install reedsolo
```

注：建议使用相同路径下的文件，不同路径还没测试过。

1. Hide程序对应的是隐藏程序

   使用方法

   ```shell
   py -3 Hide.py "载体音频文件名" "秘密音频文件名"
   ```

   或者Python3环境下

   ```shell
   python Hide.py "载体音频文件名" "秘密音频文件名"
   ```

   最终输出，[载体音频文件名]WithSecret.wav
   
   
   
2. Extract程序对应的是提取程序
   使用方法

   ```shell
   py -3 Extract.py "载密音频文件名" [K值]
   ```
   或者Python3环境下

   ```shell
   python Extract.py "载密音频文件名" [K值]
   ```
   最终输出，Secret Audio.wav
   注：解密需要U1.dat、P.dat、V1.dat、K值作为密钥，否则不能解密成功
