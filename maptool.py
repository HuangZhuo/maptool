# -*- coding:gbk -*

from urllib import parse
from urllib.request import urlretrieve
from urllib.error import HTTPError
import os
import os.path
import time

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Notebook
from tkinter.filedialog import askdirectory

from mapmerge import mergeMap

_VERSION = '0.0.1'


class CFG:
    MAX_FETCH_TRY_TIMES = 5


def getResUrl(url, mapid, i, j):
    if not url.endswith('/'):
        url += '/'
    return parse.urljoin(url, '%s/%d_%d.jpg' % (mapid, i, j))


def fetchMapRes(url, mapid, savedir, nrows=100, ncols=100):
    '''
    从文件服务器抓取地图块，保存到本地文件夹
    '''
    savedir = os.path.join(savedir, str(mapid))
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    jmax = None
    for i in range(nrows + 1):
        for j in range(ncols + 1):
            if jmax and j >= jmax:
                break
            resurl = getResUrl(url, mapid, i, j)
            print('fetch url: ' + resurl)
            filename = '%s\\%d_%d.jpg' % (savedir, i, j)
            resp, trytimes = None, 0
            while resp == None:
                try:
                    trytimes = trytimes + 1
                    _, resp = urlretrieve(resurl, filename)
                except HTTPError:
                    print('404 Not Found')
                    break
                except IOError:
                    if trytimes > CFG.MAX_FETCH_TRY_TIMES:
                        return -1, '下载失败，请检查链接是否正确'
                    print('try again')
                    time.sleep(0.1)
                    pass
            if not resp:
                if jmax == None:
                    jmax = j
                else:
                    print('finished!')
                    return 0, None
            else:
                print('file saved: ' + filename)


def _draft():
    '''
    草稿
    '''
    resurl = 'http://tx14.static.xyimg.net/lycq/res_x/map/75/104/0_46.jpg'
    f, r = urlretrieve(resurl, 'tmp.jpg')
    print(f)


class FrameDirSelect(tk.Frame):
    def __init__(self, *args, text='路径'):
        super().__init__(*args)
        self._lbl = tk.Label(self, text=text)
        self._edit = tk.Entry(self, width=50, bg='white', fg='black')
        self._btn = tk.Button(self, text='选择', command=self.onSelectClick)
        self._lbl.pack(side=tk.LEFT)
        self._edit.pack(side=tk.LEFT, fill=tk.X)
        self._btn.pack(side=tk.LEFT)

    def onSelectClick(self):
        dir = askdirectory(initialdir=os.getcwd())
        self._edit.delete(0, tk.END)
        self._edit.insert(0, dir)

    def get(self):
        return self._edit.get()


class FrameFetch(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.initUI()

    def initUI(self):
        self._lblUrl = tk.Label(self, text='链接')
        self._editUrl = tk.Entry(self, bg='white', fg='black')
        self._lblMap = tk.Label(self, text='地图ID')
        self._editMap = tk.Entry(self, bg='white', fg='black')
        self._dir = FrameDirSelect(self, text='保存路径')

        self._btn = tk.Button(self, text='下载', bg='green', command=self.onFetchClick)

        self._lblUrl.pack(fill=tk.X)
        self._editUrl.pack(fill=tk.X)
        self._lblMap.pack(fill=tk.X)
        self._editMap.pack(fill=tk.X)
        self._dir.pack(fill=tk.X)

        self._btn.pack(fill=tk.X)

    def onFetchClick(self):
        url = self._editUrl.get().strip()
        if len(url) == 0:
            messagebox.showinfo(message='请输入链接')
            return
        mapid = self._editMap.get().strip()
        if len(mapid) == 0:
            messagebox.showinfo(message='请输入地图ID')
            return
        dir = self._dir.get().strip()
        if len(dir) == 0:
            messagebox.showinfo(message='请输入保存路径')
            return
        dir = os.path.abspath(dir)
        if not os.path.exists(dir):
            os.makedirs(dir)

        ret, err = fetchMapRes(url, mapid, dir)
        if ret == 0:
            messagebox.showinfo(message='下载完成')
        else:
            messagebox.showerror(message=err)


class FrameMerge(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.initUI()

    def initUI(self):
        self._dir = FrameDirSelect(self, text='选择路径')
        self._lblMode = tk.Label(self, text='拼接模式（目前支持1|2）')
        self._editMode = tk.Entry(self, bg='white', fg='black')
        self._editMode.insert(0, '1')
        self._btn = tk.Button(self, text='合并', bg='green', command=self.onMergeClick)

        self._dir.pack(fill=tk.X)
        self._lblMode.pack(fill=tk.X)
        self._editMode.pack(fill=tk.X)
        self._btn.pack(fill=tk.X)

    def onMergeClick(self):
        dir = self._dir.get().strip()
        if len(dir) == 0:
            messagebox.showinfo(message='请输入保存路径')
            return
        dir = os.path.abspath(dir)
        if not os.path.exists(dir):
            messagebox.showerror(message='目录不存在')
            return
        mode = self._editMode.get().strip()
        try:
            mode = int(mode)
        except ValueError:
            messagebox.showerror(message='模式输入有误')
            return
        ret, err = mergeMap(dir, dir + '.jpg', mode=mode)
        if ret == 0:
            messagebox.showinfo(message='完成')
        else:
            messagebox.showerror(message=err)


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('地图工具 v%s' % (_VERSION))
        self.geometry('450x200')
        self.resizable(False, False)
        self.initUI()

    def initUI(self):
        self._notebook = Notebook(self)
        self._notebook.add(FrameFetch(), text='下载')
        self._notebook.add(FrameMerge(), text='合并')
        self._notebook.pack(fill=tk.BOTH, expand=1)


if __name__ == '__main__':
    GUI().mainloop()