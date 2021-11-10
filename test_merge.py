# -*- coding:gbk -*

import unittest

from mapmerge import mergeMap


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

    def test_mergeMap6(self):
        '''
        针对[57]的BUG修复，打包出来的图片为0字节
        '''
        args = {'path': 'tmp\\57', 'mode': 2, 'file_format': '{i}_{j}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap6(self):
        '''
        块数：0-27, 0-18
        '''
        args = {'path': 'tmp\\159', 'mode': 3, 'file_format': '{(i*28+j):05}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap7(self):
        '''
        块数：0-27, 0-18
        左边有两列无效图块，进行跳过处理
        '''
        args = {'path': 'tmp\\159', 'mode': 3, 'file_format': '{(i*26+j+2*(i+1)):05}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap8(self):
        '''
        如果文件名带v拼接字符串会由于出现`\v`(python中的垂直制表符)变成转义字符`\x0b`(ascii码中的垂直制表符)，导致找不到文件
        tmp\\v103\x0b103_r1_c1.jpg
        '''
        args = {'path': 'tmp\\v103', 'mode': 1, 'file_format': 'v103_r{i+1}_c{j+1}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap9(self):
        '''
        223
        同test_mergeMap5
        '''
        args = {'path': 'tmp\\223', 'mode': 2, 'file_format': 'pic{i}_{9-j}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

if __name__ == '__main__':
    # unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestMerge('test_mergeMap1'))
    # suite.addTest(TestMerge('test_mergeMap2'))
    # suite.addTest(TestMerge('test_mergeMap3'))
    # suite.addTest(TestMerge('test_mergeMap4'))
    # suite.addTest(TestMerge('test_mergeMap5'))
    # suite.addTest(TestMerge('test_mergeMap6'))

    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)
    pass