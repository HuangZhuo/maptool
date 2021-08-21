# -*- coding:gbk -*

import os
import os.path
import time
from urllib.request import urlretrieve
from urllib.error import HTTPError

MAX_FETCH_TRY_TIMES = 5


def getResUrl(url, name, i, j):
    # not good code but simple here
    try:
        return eval("f'%s'" % url)
    except:
        return None


def getFileName(url):
    return os.path.basename(url)


def fetchMapRes(url, mapname, savedir, nrows=10000, ncols=10000):
    '''
    ���ļ�������ץȡ��ͼ�飬���浽�����ļ���
    '''
    savedir = os.path.join(savedir, str(mapname))
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    # ��{j}/ncols�޹أ�����һά����
    if getResUrl(url, '', 0, 0) == getResUrl(url, '', 0, 1):
        ncols = 1

    jmax = None
    for i in range(nrows):
        for j in range(ncols):
            if jmax and j >= jmax:
                break
            resurl = getResUrl(url, mapname, i, j)
            if not resurl:
                return -2, '���Ӹ�ʽ����'
            print('fetch url: ' + resurl)
            filename = os.path.join(savedir, getFileName(resurl))
            resp, trytimes = None, 0
            while resp == None:
                try:
                    trytimes = trytimes + 1
                    _, resp = urlretrieve(resurl, filename)
                except HTTPError:
                    print('404 Not Found')
                    if jmax == None:
                        jmax = j
                    break
                except IOError:
                    if trytimes > MAX_FETCH_TRY_TIMES:
                        return -1, '����ʧ�ܣ����������Ƿ���ȷ'
                    print('try again')
                    time.sleep(0.1)
                    pass
            if not resp:
                if i == 0 and j == 0:
                    return -1, '����ʧ�ܣ����������Ƿ���ȷ'
                if i > 0 and j == 0:
                    print('finished!')
                    return 0, None
            else:
                print('file saved: ' + filename)
