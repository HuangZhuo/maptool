# -*- coding:gbk -*

import os.path
import re
import argparse
from PIL import Image
from sys import exit

parser = argparse.ArgumentParser(description='将地图块拼接成完整地图')
parser.add_argument('-p', '--path', required=True, help='地图块文件夹路径')
parser.add_argument('-m', '--mode', default=1, type=int, choices=[1, 2], help='合并模式，暂时支持1|2，如果生成错乱图片可以切换模式再试')
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


def _test():
    args = {'path': 'tmp\\12', 'mode': 2, 'output': 'tmp\\12.jpg'}
    print(mergeMap(args['path'], args['output'], args['mode']))


if __name__ == '__main__':
    global args
    args = parser.parse_args()
    # print(args)
    args.path = os.path.abspath(args.path)
    if not os.path.exists(args.path) or not os.path.isdir(args.path):
        print('文件夹不存在')
        exit(-1)
    if not args.output:
        args.output = args.path + '.jpg'

    exit(mergeMap(args.path, args.output, args.mode))