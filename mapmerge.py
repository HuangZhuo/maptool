# -*- coding:gbk -*

import os.path
import argparse
from PIL import Image
from sys import exit


def getMapPieceCount(fmt, resdir):
    '''��ȡ���ص�ͼ�� imax,jmax'''
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
    '''��ȡ��ͼ���ļ���׺��'''
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
            return None, '�޷��ҵ���ͼ���ļ�: ' + filename
        return Image.open(filename), None
    except:
        return None, 'ͼƬ����ʽ���쳣'


def mergeMap(resdir, mode=None, file_format=None, i_max=None, j_max=None, outputfile=None):
    '''
    ͼƬƴ��ģʽ(mode=1 / Ĭ��)��
    0_0|0_1|0_2|0_3
    1_0|1_1|1_2|1_3
    2_0|2_1|2_2|2_3

    ͼƬƴ��ģʽ(mode=2 / XY��ת)��
    0_0|1_0|2_0|3_0
    0_1|1_1|2_1|3_1
    0_2|1_2|2_2|3_2

    ͼƬƴ��ģʽ(mode=3 / һά����)��
    1| 2| 3| 4
    5| 6| 7| 8
    9|10|11|12

    �����ص�ͼ��ƴ�ӳ�������ͼ���ɹ�����0�����򷵻ظ����ʹ�������
    ref: https://www.jb51.net/article/165457.htm
    '''
    mode = mode if mode else 1
    if not mode in set([1, 2, 3]):
        return -2, '��֧�ֵ�ģʽƴ��ģʽ: ' + str(mode)
    if mode == 3:
        return mergeMap3(resdir, mode, file_format, i_max, j_max, outputfile)
    if file_format:
        # if file_format.find('{i}') < 0 or file_format.find('{j}') < 0:
        #     return -4, '�ļ�����ʽ����'
        pass
    else:
        file_format = '{i}_{j}.jpg'

    if not i_max or not j_max:
        # �ƶϿ���
        i_max, j_max = getMapPieceCount(file_format, resdir)
    if i_max == 0:
        return -3, f'û�е�ͼ�飺{file_format}'
    meta, err = image(file_format, resdir, 0, 0)
    if not meta:
        return -1, err
    # print(meta)
    w, h = meta.width, meta.height
    margin, err = image(file_format, resdir, i_max - 1, j_max - 1)
    padx, pady = meta.width - margin.width, meta.height - margin.height
    imgRet, imgMode = None, meta.mode
    if imgMode == 'P':
        # png���⴦��
        imgMode = 'RGBA'
    if imgMode == 'L':
        # sRGB ���⴦������ᵼ��Ϊ��ͼ
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
    return 0, '�ɹ�'


def tryGetMapPieceCount3(resdir, ext):
    '''
    ���Ի�ȡһά���ص�ͼ�� imax,jmax
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
    һά�����ļ���ʽƴ�ӣ�˼·
    1. ���Ը��ݵ�ͼ���С���ƶϳ��߽��������Լ���Ч����
    2. ���������ֽ⣨�����ֽ���Ҳ��Ψһ����ʱ����������
    3. ʶ��ͼƬ��Ե�Ƿ������������õ�ͼ��ʶ����ؼ�����Ҳ�Ȳ��о���

    '''
    if file_format == None:
        ext = getMapPieceExt(resdir)
        if not ext:
            return -5, '�޷��ƶ��ļ�����׺'
        if not j_max:
            i_max, j_max = tryGetMapPieceCount3(resdir, ext)
            if j_max == 0:
                return -6, '�޷��ƶ�ͼƬ���'
        file_format = '{i*%d+j+1}%s' % (j_max, ext)
    else:
        # master user
        pass

    # ת��Ϊ��ά����
    return mergeMap(resdir, 1, file_format, i_max, j_max, outputfile)


if __name__ == '__main__':
    # �����й���
    parser = argparse.ArgumentParser(description='����ͼ��ƴ�ӳ�������ͼ')
    parser.add_argument('-p', '--path', required=True, help='��ͼ���ļ���·��')
    parser.add_argument('-m', '--mode', type=int, choices=[1, 2, 3], help='ƴ��ģʽ��1-��ά������2-��ά������ת��3-һά����')
    parser.add_argument('-i', '--i_max', type=int, help='{i}�������ֵ')
    parser.add_argument('-j', '--j_max', type=int, help='{j}�������ֵ')
    parser.add_argument('-f', '--file-format', help='�ļ�ƥ���ʽ�����磺{i}_{j}.jpg')
    parser.add_argument('-o', '--output', help='������ͼ�ļ�·��')

    args = parser.parse_args()
    print(args)
    args.path = os.path.abspath(args.path)
    if not os.path.exists(args.path) or not os.path.isdir(args.path):
        print('�ļ��в�����')
        exit(-1)

    exit(mergeMap(args.path, args.output, args.mode, args.i_max, args.j_max, args.file_format))
