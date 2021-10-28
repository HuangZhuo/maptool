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

    def test_mergeMap5(self):
        '''
        图片拼接模式(XY反转 + 左下角原点)：
        0_2|1_2|2_2|3_2
        0_1|1_1|2_1|3_1
        0_0|1_0|2_0|3_0
        '''
        args = {'path': 'tmp\\front', 'mode': 2, 'file_format': 'pic{i}_{11-j}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestMerge('test_mergeMap1'))
    suite.addTest(TestMerge('test_mergeMap2'))
    suite.addTest(TestMerge('test_mergeMap3'))
    suite.addTest(TestMerge('test_mergeMap4'))
    suite.addTest(TestMerge('test_mergeMap5'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)