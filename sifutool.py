# -*- coding:gbk -*
'''
处理精灵帧，生成传奇私服可用格式数据
- 计算裁剪区域
- 裁剪图片并保存
- 生成坐标偏移文件

导出EXE
> pyinstaller -F .\sifutool.py
'''

import os
import os.path
import argparse
from sys import exit
from typing import Tuple
from math import ceil
from numpy import array as numpy_array
from PIL import Image

POS_DIR_NAME = 'Placements'


def getBoundingBox(im: Image) -> Tuple:
    '''
    获取有效像素边界，返回两个坐标
    以左上角为原点
    '''
    imarr = numpy_array(im)
    # height,width,channel
    h, w, __ = imarr.shape
    x1, y1, x2, y2 = w, h, 0, 0
    for x in range(w):
        for y in range(h):
            if imarr[y, x][3] > 0:
                # 非透明像素
                x1 = min(x1, x)
                y1 = min(y1, y)
                x2 = max(x2, x)
                y2 = max(y2, y)
    return (x1, y1, x2, y2)


def getOffset(im: Image, box: Tuple) -> Tuple:
    '''
    获取图片相对中心位置偏移
    '''
    imcenter = (im.size[0] / 2, im.size[1] / 2)
    boxcenter = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
    return (boxcenter[0] - imcenter[0], boxcenter[1] - imcenter[1])


def process(dir, outdir=None):
    if not outdir:
        outdir = dir + '_sifu'
    posdir = os.path.join(outdir, POS_DIR_NAME)
    if not os.path.exists(posdir):
        os.makedirs(posdir)
    for f in os.listdir(dir):
        base, ext = os.path.splitext(f)
        if ext != '.png':
            continue
        filename = os.path.join(dir, f)
        print(f'process:{filename}')
        with Image.open(filename) as im:
            box = getBoundingBox(im)
            offset = getOffset(im, box)
            crop = im.crop(box)
            crop.save(os.path.join(outdir, f))
            posfile = os.path.join(posdir, f'{base}.txt')
            with open(posfile, 'w') as f:
                for v in offset:
                    f.writelines(str(ceil(v)) + '\n')
    print('finished!')
    return 0


def test():
    process('tmpsf/a11048')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成私服可用素材格式')
    parser.add_argument('-p', '--path', required=True, help='帧动画图片文件夹路径')
    parser.add_argument('-o', '--output', help='输出文件夹路径')
    args = parser.parse_args()
    # print(args)
    if not os.path.exists(args.path):
        exit('文件夹不存在')
    exit(process(args.path, args.output))
