# -*- coding:gbk -*

import unittest

from mapmerge import mergeMap
from mapfetch import fetchMapRes


class TestMerge(unittest.TestCase):
    def test_mergeMap1(self):
        '''测试最基本二维索引拼接'''
        args = {'path': 'tmp\\104', 'mode': 1}
        ret, err = mergeMap(args['path'], args['mode'])
        self.assertEqual(0, ret, err)

    def test_mergeMap2(self):
        '''测试二维索引反转拼接'''
        args = {'path': 'tmp\\12', 'mode': 2, 'file_format': 'm{i}_{j}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap3(self):
        '''测试一维索引拼接'''
        args = {'path': 'tmp\\10013_205', 'mode': 3, 'file_format': None}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    @unittest.skip('merge .png will take more time!')
    def test_mergeMap4(self):
        '''测试一维索引拼接 PNG格式'''
        args = {'path': 'tmp\\10116_2264', 'mode': 3, 'file_format': None}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'], i_max=None, j_max=35)
        self.assertEqual(0, ret, err)


class TestFetch(unittest.TestCase):
    def test_fetchMapRes1(self):
        '''测试一维索引地图块下载'''
        ret, err = fetchMapRes('https://cdn-hhzz.qixia.ltd/res/map/{name}/tiles/{i+1}.jpg', '10013_205', 'tmp')
        self.assertEqual(0, ret, err)

    def test_fetchMapRes2(self):
        '''测试二维索引地图块下载'''
        url = 'https://reszsfy.cqzq6.com/cdn/zsjx/res/map/{name}/tiles/y{i}_x{j}.jpg'
        ret, err = fetchMapRes(url, '20133_349', 'tmp')
        self.assertEqual(0, ret, err)


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestMerge('test_mergeMap1'))
    suite.addTest(TestMerge('test_mergeMap2'))
    suite.addTest(TestMerge('test_mergeMap3'))
    suite.addTest(TestMerge('test_mergeMap4'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)