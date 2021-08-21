# -*- coding:gbk -*

import unittest

from mapmerge import mergeMap
from mapfetch import fetchMapRes


class TestMerge(unittest.TestCase):
    def test_mergeMap1(self):
        '''�����������ά����ƴ��'''
        args = {'path': 'tmp\\104', 'mode': 1}
        ret, err = mergeMap(args['path'], args['mode'])
        self.assertEqual(0, ret, err)

    def test_mergeMap2(self):
        '''���Զ�ά������תƴ��'''
        args = {'path': 'tmp\\12', 'mode': 2, 'file_format': 'm{i}_{j}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap3(self):
        '''����һά����ƴ��'''
        args = {'path': 'tmp\\10013_205', 'mode': 3, 'file_format': None}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    @unittest.skip('merge .png will take more time!')
    def test_mergeMap4(self):
        '''����һά����ƴ�� PNG��ʽ'''
        args = {'path': 'tmp\\10116_2264', 'mode': 3, 'file_format': None}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'], i_max=None, j_max=35)
        self.assertEqual(0, ret, err)


class TestFetch(unittest.TestCase):
    def test_fetchMapRes1(self):
        '''����һά������ͼ������'''
        ret, err = fetchMapRes('https://cdn-hhzz.qixia.ltd/res/map/{name}/tiles/{i+1}.jpg', '10013_205', 'tmp')
        self.assertEqual(0, ret, err)

    def test_fetchMapRes2(self):
        '''���Զ�ά������ͼ������'''
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