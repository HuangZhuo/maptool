# -*- coding:gbk -*

import os.path
import argparse
from PIL import Image
from sys import exit


def getMapPieceCount(fmt, resdir):
    '''获取本地地图块 imax,jmax'''
    def exist(resdir, i, j):
        filename = eval("f'{resdir}\\\\%s'" % fmt)
        return os.path.exists(filename)

    i, j = 0, 0
    while exist(resdir, i, j):
        i += 1
    if i == 0:
        return 0, 0
    while exist(resdir, i - 1, j):
        j += 1
    return i, j


def getMapPieceExt(resdir):
    '''获取地图块文件后缀名'''
    for dir in os.listdir(resdir):
        filename = os.path.join(resdir, dir)
        if os.path.isdir(filename):
            continue
        _, ext = os.path.splitext(filename)
        return ext
    return None


def image(fmt, resdir, i, j):
    try:
        filename = eval("f'{resdir}\\\\%s'" % fmt)
        if not os.path.exists(filename):
            return None, '无法找到地图块文件: ' + filename
        return Image.open(filename), None
    except:
        return None, '图片名格式化异常'


def mergeMap(resdir, mode=None, file_format=None, i_max=None, j_max=None, outputfile=None):
    '''
    图片拼接模式(mode=1 / 默认)：
    0_0|0_1|0_2|0_3
    1_0|1_1|1_2|1_3
    2_0|2_1|2_2|2_3

    图片拼接模式(mode=2 / XY反转)：
    0_0|1_0|2_0|3_0
    0_1|1_1|2_1|3_1
    0_2|1_2|2_2|3_2

    图片拼接模式(mode=3 / 一维索引)：
    1| 2| 3| 4
    5| 6| 7| 8
    9|10|11|12

    将本地地图块拼接成完整地图，成功返回0，否则返回负数和错误描述
    ref: https://www.jb51.net/article/165457.htm
    '''
    mode = mode if mode else 1
    if not mode in set([1, 2, 3]):
        return -2, '不支持的模式拼接模式: ' + str(mode)
    if mode == 3:
        return mergeMap3(resdir, mode, file_format, i_max, j_max, outputfile)
    if file_format:
        # if file_format.find('{i}') < 0 or file_format.find('{j}') < 0:
        #     return -4, '文件名格式错误'
        pass
    else:
        file_format = '{i}_{j}.jpg'

    if not i_max or not j_max:
        # 推断块数
        i_max, j_max = getMapPieceCount(file_format, resdir)
    if i_max == 0:
        return -3, f'没有地图块：{file_format}'
    meta, err = image(file_format, resdir, 0, 0)
    if not meta:
        return -1, err
    # print(meta)
    w, h = meta.width, meta.height
    margin, err = image(file_format, resdir, i_max - 1, j_max - 1)
    padx, pady = meta.width - margin.width, meta.height - margin.height
    imgRet, imgMode = None, meta.mode
    if imgMode == 'P':
        # png特殊处理
        imgMode = 'RGBA'
    if imgMode == 'L':
        # sRGB 特殊处理，否则会导出为灰图
        imgMode = 'RGB'
    if mode == 1:
        imgRet = Image.new(imgMode, (w * j_max - padx, h * i_max - pady))
    elif mode == 2:
        imgRet = Image.new(imgMode, (w * i_max - padx, h * j_max - pady))
    for i in range(i_max):
        for j in range(j_max):
            tmp, err = image(file_format, resdir, i, j)
            if not tmp:
                return -1, err
            if mode == 1:
                imgRet.paste(tmp, box=(j * w, i * h))
            elif mode == 2:
                imgRet.paste(tmp, box=(i * w, j * h))

    if not outputfile:
        _, ext = os.path.splitext(meta.filename)
        if imgMode == 'RGBA':
            ext = '.png'
        outputfile = resdir + ext
    try:
        imgRet.save(outputfile)
    except Exception as e:
        print(str(e))
        return -5, repr(e)
    return 0, '成功'


def tryGetMapPieceCount3(resdir, ext):
    '''
    尝试获取一维本地地图块 imax,jmax
    '''
    if not ext:
        return 0, 0
    meta = None
    i, j, total = 0, 0, 0
    while True:
        fdir = f'{resdir}\\{total+1}{ext}'
        if not os.path.exists(fdir):
            break
        if total == 0:
            meta = Image.open(fdir)
        total += 1
        if meta:
            j = total
            tmp = Image.open(fdir)
            if tmp.width != meta.width or tmp.height != meta.height:
                meta = None
    i = int(total / j) if j > 0 else 0
    if i * j != total:
        return 0, 0
    return i, j


def mergeMap3(resdir, mode=None, file_format=None, i_max=None, j_max=None, outputfile=None):
    '''
    一维索引文件格式拼接，思路
    1. 尝试根据地图块大小，推断出边界块数（相对简单有效！）
    2. 尝试因数分解（因数分解结果也不唯一，暂时不打算做）
    3. 识别图片边缘是否相连（可能用到图像识别相关技术，也先不研究）

    '''
    if file_format == None:
        ext = getMapPieceExt(resdir)
        if not ext:
            return -5, '无法推断文件名后缀'
        if not j_max:
            i_max, j_max = tryGetMapPieceCount3(resdir, ext)
            if j_max == 0:
                return -6, '无法推断图片宽高'
        file_format = '{i*%d+j+1}%s' % (j_max, ext)
    else:
        # master user
        pass

    # 转化为二维处理
    return mergeMap(resdir, 1, file_format, i_max, j_max, outputfile)


if __name__ == '__main__':
    # 命令行规则
    parser = argparse.ArgumentParser(description='将地图块拼接成完整地图')
    parser.add_argument('-p', '--path', required=True, help='地图块文件夹路径')
    parser.add_argument('-m', '--mode', type=int, choices=[1, 2, 3], help='拼接模式：1-二维索引，2-二维索引反转，3-一维索引')
    parser.add_argument('-i', '--i_max', type=int, help='{i}索引最大值')
    parser.add_argument('-j', '--j_max', type=int, help='{j}索引最大值')
    parser.add_argument('-f', '--file-format', help='文件匹配格式，例如：{i}_{j}.jpg')
    parser.add_argument('-o', '--output', help='输出大地图文件路径')

    args = parser.parse_args()
    print(args)
    args.path = os.path.abspath(args.path)
    if not os.path.exists(args.path) or not os.path.isdir(args.path):
        print('文件夹不存在')
        exit(-1)

    exit(mergeMap(args.path, args.output, args.mode, args.i_max, args.j_max, args.file_format))
