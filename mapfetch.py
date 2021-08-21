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
    从文件服务器抓取地图块，保存到本地文件夹
    '''
    savedir = os.path.join(savedir, str(mapname))
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    # 与{j}/ncols无关，兼容一维索引
    if getResUrl(url, '', 0, 0) == getResUrl(url, '', 0, 1):
        ncols = 1

    jmax = None
    for i in range(nrows):
        for j in range(ncols):
            if jmax and j >= jmax:
                break
            resurl = getResUrl(url, mapname, i, j)
            if not resurl:
                return -2, '链接格式错误'
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
                        return -1, '下载失败，请检查链接是否正确'
                    print('try again')
                    time.sleep(0.1)
                    pass
            if not resp:
                if i == 0 and j == 0:
                    return -1, '下载失败，请检查链接是否正确'
                if i > 0 and j == 0:
                    print('finished!')
                    return 0, None
            else:
                print('file saved: ' + filename)
