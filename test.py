# -*- coding:gbk -*

from mapmerge import mergeMap
from maptool import fetchMapRes


def test_mergeMap():
    args = {'path': 'tmp\\10013_205', 'mode': 3, 'output': 'tmp\\10013_205.jpg'}
    print(mergeMap(args['path'], args['output'], args['mode']))


def test_mergeMap1():
    '''
    测试最基本二维索引拼接
    '''
    args = {
        'path': 'tmp\\104',
        'mode': 1,
    }
    print(mergeMap(args['path'], args['mode']))


def test_mergeMap2():
    '''
    测试二维索引反转拼接
    '''
    args = {'path': 'tmp\\12', 'mode': 2, 'file_format': 'm{i}_{j}.jpg'}
    print(mergeMap(args['path'], args['mode'], args['file_format']))


def test_mergeMap3():
    '''
    测试一维索引拼接
    '''
    args = {'path': 'tmp\\10013_205', 'mode': 3, 'file_format': None}
    print(mergeMap(args['path'], args['mode'], args['file_format']))


def test_mergeMap4():
    '''
    测试一维索引拼接 PNG格式
    '''
    args = {'path': 'tmp\\10116_2264', 'mode': 3, 'file_format': None}
    print(mergeMap(args['path'], args['mode'], args['file_format'], i_max=None, j_max=35))


def test_fetchMapRes():
    fetchMapRes('https://cdn-hhzz.qixia.ltd/res/map/{name}/tiles/{i+1}.jpg', '10013_205', 'tmp')


def test_fetchMapRes3():
    fetchMapRes('https://reszsfy.cqzq6.com/cdn/zsjx/res/map/{name}/tiles/y{i}_x{j}.jpg', '20133_349', 'tmp')


if __name__ == '__main__':
    # test_mergeMap1()
    # test_mergeMap2()
    # test_mergeMap3()
    # test_mergeMap4()
    pass