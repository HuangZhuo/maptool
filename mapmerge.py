# -*- coding:gbk -*

import os.path
import re
import argparse
from PIL import Image
from sys import exit

parser = argparse.ArgumentParser(description='将地图块拼接成完整地图')
parser.add_argument('-p', '--path', required=True, help='地图块文件夹路径')
parser.add_argument('-m',
                    '--mode',
                    default=1,
                    type=int,
                    choices=[1, 2, 3],
                    help='合并模式，暂时支持1|2|3(一维索引)，如果生成错乱图片可以切换模式再试')
parser.add_argument('-o', '--output', help='输出大地图文件路径')


def getMapPieceCount(resdir):
    '''
    获取本地地图块X,Y方向块数
    '''
    i, j = 0, 0
    for dir in os.listdir(resdir):
        if os.path.isdir(os.path.join(resdir, dir)):
            continue
        match = re.match(r'^[m]?(\d+)_(\d+).jpg$', dir)
        if not match:
            continue
        # print(match.group(1))
        i = max(i, int(match.group(1)) + 1)
        j = max(j, int(match.group(2)) + 1)
    return i, j


def mergeMap(resdir, outputfile, mode=1):
    '''
    将本地地图块拼接成完整地图，成功返回0，否则返回负数和错误描述
    ref: https://www.jb51.net/article/165457.htm
    '''
    if mode == 3:
        return mergeMap3(resdir, outputfile)

    def image(i, j):
        filename = '%s\\%d_%d.jpg' % (resdir, i, j)
        if not os.path.exists(filename):
            filename = '%s\\m%d_%d.jpg' % (resdir, i, j)
        if not os.path.exists(filename):
            return None, '无法找到地图块文件: ' + filename
        return Image.open(filename), None

    pw, ph = getMapPieceCount(resdir)
    if pw == 0:
        return -3, '没有地图块'
    meta, err = image(0, 0)
    if not meta:
        return -1, err
    w, h = meta.width, meta.height
    # print(meta)
    imgRet = None
    if mode == 1:
        imgRet = Image.new(meta.mode, (w * ph, h * pw))
    elif mode == 2:
        imgRet = Image.new(meta.mode, (w * pw, h * ph))
    else:
        return -2, '不支持的模式拼接模式: ' + str(mode)
    for i in range(pw):
        for j in range(ph):
            tmp, err = image(i, j)
            if not tmp:
                return -1, err
            if mode == 1:
                imgRet.paste(tmp, box=(j * w, i * h))
            elif mode == 2:
                imgRet.paste(tmp, box=(i * w, j * h))
            else:
                return -2, '不支持的模式拼接模式: ' + str(mode)

    imgRet.save(outputfile)
    return 0, '成功'


def getMapPieceCount3(resdir, meta):
    '''
    获取本地地图块X,Y方向块数
    图片拼接模式：
    1| 2| 3| 4
    5| 6| 7| 8
    9|10|11|12
    '''
    i, j, total = 0, 0, 0
    while True:
        fdir = f'{resdir}\\{total+1}.jpg'
        if not os.path.exists(fdir):
            break
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


def mergeMap3(resdir, outputfile):
    '''
    一维索引文件格式拼接，思路
    1. 尝试根据地图块大小，推断出边界块数（相对简单有效！）
    2. 尝试因数分解（因数分解结果也不唯一，暂时不打算做）
    3. 识别图片边缘是否相连（可能用到图像识别相关技术，也先不研究）
    '''
    def image(n):
        filename = f'{resdir}\\{n}.jpg'
        if not os.path.exists(filename):
            return None, '无法找到地图块文件: ' + filename
        return Image.open(filename), None

    meta, err = image(1)
    if not meta:
        return -1, err
    # pv:pieces vertical; ph:pices horizontal
    pv, ph = getMapPieceCount3(resdir, meta)
    if pv <= 1:
        return -4, '无法推断地图边界块数'
    w, h = meta.width, meta.height

    # 不均匀裁切计算实际大小
    margin, err = image(pv * ph)
    padx, pady = meta.width - margin.width, meta.height - margin.height
    imgRet = Image.new(meta.mode, (w * ph - padx, h * pv - pady))
    for i in range(pv):
        for j in range(ph):
            tmp, err = image(i * ph + j + 1)
            if not tmp:
                return -1, err
            # 左上角顶点坐标系
            imgRet.paste(tmp, box=(j * w, i * h))
    imgRet.save(outputfile)
    return 0, '成功'


if __name__ == '__main__':
    args = parser.parse_args()
    # print(args)
    args.path = os.path.abspath(args.path)
    if not os.path.exists(args.path) or not os.path.isdir(args.path):
        print('文件夹不存在')
        exit(-1)
    if not args.output:
        args.output = args.path + '.jpg'

    exit(mergeMap(args.path, args.output, args.mode))