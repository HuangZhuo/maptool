# -*- coding:gbk -*
'''
提供：
- root url
- 资源清单文件
- 资源名称匹配字符串
下载满足匹配的所有文件
'''

import json
import re
import os
import time
from urllib.parse import urljoin
from urllib.request import urlretrieve
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_FETCH_TRY_TIMES = 5


def parseManifest(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        s = f.read()
        if len(s) > 0:
            return json.loads(s)
    return None


def getResList(manifest: dict, pattrn):
    ret = {}
    for k, v in manifest.items():
        if re.match(pattrn, k):
            ret[k] = v
    return ret


def fetchAll(url: str, manifest, savedir, onProgress):
    if not url.endswith('/'):
        url += '/'
    with ThreadPoolExecutor(max_workers=8) as t:
        tasks = []
        for k, v in manifest.items():
            resurl = urljoin(url, v)
            filename = os.path.normpath(os.path.join(savedir, k))
            tasks.append(t.submit(fetchOne, resurl, filename))
        total, finished = len(tasks), 0
        for future in as_completed(tasks):
            data = future.result()
            finished += 1
            onProgress(total, finished, data)
    return 0, None


def fetchOne(url, filename):
    '''
    下载位于url的文件，保存到至filename
    '''
    # return url, filename
    dir = os.path.dirname(filename)
    if not os.path.exists(dir):
        os.makedirs(dir)
    resp, trytimes = None, 0
    while resp == None:
        try:
            trytimes = trytimes + 1
            _, resp = urlretrieve(url, filename)
        except HTTPError:
            return -2, '404 Not Found'
        except IOError:
            if trytimes > MAX_FETCH_TRY_TIMES:
                return -1, '下载失败，请检查链接是否正确'
            time.sleep(0.1)
            pass
    return 0, filename


def test():
    pass


if __name__ == '__main__':
    test()
