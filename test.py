# -*- coding:gbk -*

from mapmerge import mergeMap
from maptool import fetchMapRes


def test_mergeMap():
    args = {'path': 'tmp\\10013_205', 'mode': 3, 'output': 'tmp\\10013_205.jpg'}
    print(mergeMap(args['path'], args['output'], args['mode']))


def test_fetchMapRes():
    fetchMapRes('https://cdn-hhzz.qixia.ltd/res/map/{name}/tiles/{i+1}.jpg', '10013_205', 'tmp')


if __name__ == '__main__':
    pass