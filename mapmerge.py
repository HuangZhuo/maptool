# -*- coding:gbk -*

import os.path
import re
import argparse
from PIL import Image
from sys import exit

parser = argparse.ArgumentParser(description='����ͼ��ƴ�ӳ�������ͼ')
parser.add_argument('-p', '--path', required=True, help='��ͼ���ļ���·��')
parser.add_argument('-m',
                    '--mode',
                    default=1,
                    type=int,
                    choices=[1, 2, 3],
                    help='�ϲ�ģʽ����ʱ֧��1|2|3(һά����)��������ɴ���ͼƬ�����л�ģʽ����')
parser.add_argument('-o', '--output', help='������ͼ�ļ�·��')


def getMapPieceCount(resdir):
    '''
    ��ȡ���ص�ͼ��X,Y�������
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
    �����ص�ͼ��ƴ�ӳ�������ͼ���ɹ�����0�����򷵻ظ����ʹ�������
    ref: https://www.jb51.net/article/165457.htm
    '''
    if mode == 3:
        return mergeMap3(resdir, outputfile)

    def image(i, j):
        filename = '%s\\%d_%d.jpg' % (resdir, i, j)
        if not os.path.exists(filename):
            filename = '%s\\m%d_%d.jpg' % (resdir, i, j)
        if not os.path.exists(filename):
            return None, '�޷��ҵ���ͼ���ļ�: ' + filename
        return Image.open(filename), None

    pw, ph = getMapPieceCount(resdir)
    if pw == 0:
        return -3, 'û�е�ͼ��'
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
        return -2, '��֧�ֵ�ģʽƴ��ģʽ: ' + str(mode)
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
                return -2, '��֧�ֵ�ģʽƴ��ģʽ: ' + str(mode)

    imgRet.save(outputfile)
    return 0, '�ɹ�'


def getMapPieceCount3(resdir, meta):
    '''
    ��ȡ���ص�ͼ��X,Y�������
    ͼƬƴ��ģʽ��
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
    һά�����ļ���ʽƴ�ӣ�˼·
    1. ���Ը��ݵ�ͼ���С���ƶϳ��߽��������Լ���Ч����
    2. ���������ֽ⣨�����ֽ���Ҳ��Ψһ����ʱ����������
    3. ʶ��ͼƬ��Ե�Ƿ������������õ�ͼ��ʶ����ؼ�����Ҳ�Ȳ��о���
    '''
    def image(n):
        filename = f'{resdir}\\{n}.jpg'
        if not os.path.exists(filename):
            return None, '�޷��ҵ���ͼ���ļ�: ' + filename
        return Image.open(filename), None

    meta, err = image(1)
    if not meta:
        return -1, err
    # pv:pieces vertical; ph:pices horizontal
    pv, ph = getMapPieceCount3(resdir, meta)
    if pv <= 1:
        return -4, '�޷��ƶϵ�ͼ�߽����'
    w, h = meta.width, meta.height

    # �����Ȳ��м���ʵ�ʴ�С
    margin, err = image(pv * ph)
    padx, pady = meta.width - margin.width, meta.height - margin.height
    imgRet = Image.new(meta.mode, (w * ph - padx, h * pv - pady))
    for i in range(pv):
        for j in range(ph):
            tmp, err = image(i * ph + j + 1)
            if not tmp:
                return -1, err
            # ���ϽǶ�������ϵ
            imgRet.paste(tmp, box=(j * w, i * h))
    imgRet.save(outputfile)
    return 0, '�ɹ�'


if __name__ == '__main__':
    args = parser.parse_args()
    # print(args)
    args.path = os.path.abspath(args.path)
    if not os.path.exists(args.path) or not os.path.isdir(args.path):
        print('�ļ��в�����')
        exit(-1)
    if not args.output:
        args.output = args.path + '.jpg'

    exit(mergeMap(args.path, args.output, args.mode))