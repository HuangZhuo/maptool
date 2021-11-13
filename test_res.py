import unittest

from splitLayaAtlas.splitLayaAtlas import dispose1file


class TestResFetch(unittest.TestCase):
    def test_atlasSplit(self):
        '''精灵帧动画图集拆分测试'''
        dir = 'manifest/res/atlas/effect/160001'
        dispose1file(dir)