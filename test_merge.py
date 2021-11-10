# -*- coding:gbk -*

import unittest

from mapmerge import mergeMap


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

    def test_mergeMap5(self):
        '''
        ͼƬƴ��ģʽ(XY��ת + ���½�ԭ��)��
        0_2|1_2|2_2|3_2
        0_1|1_1|2_1|3_1
        0_0|1_0|2_0|3_0
        '''
        args = {'path': 'tmp\\front', 'mode': 2, 'file_format': 'pic{i}_{11-j}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap6(self):
        '''
        ���[57]��BUG�޸������������ͼƬΪ0�ֽ�
        '''
        args = {'path': 'tmp\\57', 'mode': 2, 'file_format': '{i}_{j}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap6(self):
        '''
        ������0-27, 0-18
        '''
        args = {'path': 'tmp\\159', 'mode': 3, 'file_format': '{(i*28+j):05}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap7(self):
        '''
        ������0-27, 0-18
        �����������Чͼ�飬������������
        '''
        args = {'path': 'tmp\\159', 'mode': 3, 'file_format': '{(i*26+j+2*(i+1)):05}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap8(self):
        '''
        ����ļ�����vƴ���ַ��������ڳ���`\v`(python�еĴ�ֱ�Ʊ��)���ת���ַ�`\x0b`(ascii���еĴ�ֱ�Ʊ��)�������Ҳ����ļ�
        tmp\\v103\x0b103_r1_c1.jpg
        '''
        args = {'path': 'tmp\\v103', 'mode': 1, 'file_format': 'v103_r{i+1}_c{j+1}.jpg'}
        ret, err = mergeMap(args['path'], args['mode'], args['file_format'])
        self.assertEqual(0, ret, err)

    def test_mergeMap9(self):
        '''
        223
        ͬtest_mergeMap5
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