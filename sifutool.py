# -*- coding:gbk -*
'''
������֡�����ɴ���˽�����ø�ʽ����
- ����ü�����
- �ü�ͼƬ������
- ��������ƫ���ļ�

����EXE
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
    ��ȡ��Ч���ر߽磬������������
    �����Ͻ�Ϊԭ��
    '''
    imarr = numpy_array(im)
    # height,width,channel
    h, w, __ = imarr.shape
    x1, y1, x2, y2 = w, h, 0, 0
    for x in range(w):
        for y in range(h):
            if imarr[y, x][3] > 0:
                # ��͸������
                x1 = min(x1, x)
                y1 = min(y1, y)
                x2 = max(x2, x)
                y2 = max(y2, y)
    return (x1, y1, x2, y2)


def getOffset(im: Image, box: Tuple) -> Tuple:
    '''
    ��ȡͼƬ�������λ��ƫ��
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
    parser = argparse.ArgumentParser(description='����˽�������زĸ�ʽ')
    parser.add_argument('-p', '--path', required=True, help='֡����ͼƬ�ļ���·��')
    parser.add_argument('-o', '--output', help='����ļ���·��')
    args = parser.parse_args()
    # print(args)
    if not os.path.exists(args.path):
        exit('�ļ��в�����')
    exit(process(args.path, args.output))
