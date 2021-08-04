# -*- coding:gbk -*

from urllib.request import urlretrieve
from urllib.error import HTTPError
import os
import os.path
import time
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Notebook
from tkinter.filedialog import askdirectory

from mapmerge import mergeMap

_VERSION = '0.0.3'


class CFG:
    MAX_FETCH_TRY_TIMES = 5
    CLI_UPDATE_TIME_IN_MS = 100
    THREAD_CHECK_TIME_IN_MS = 10


class CLICache:
    _queue = Queue()

    @staticmethod
    def write(str):
        CLICache._queue.put(str)

    @staticmethod
    def empty():
        return CLICache._queue.empty()

    @staticmethod
    def get():
        return CLICache._queue.get()


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

    # trick����{j}/ncols�޹أ�����һά����
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
                    if trytimes > CFG.MAX_FETCH_TRY_TIMES:
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


def _draft():
    '''
    �ݸ�
    '''
    resurl = 'http://tx14.static.xyimg.net/lycq/res_x/map/75/104/0_46.jpg'
    f, r = urlretrieve(resurl, 'tmp.jpg')
    print(f)


class FrameEdit(tk.Frame):
    '''
    ������װ
    '''
    def __init__(self, *args, text="����", hint=None, width=15):
        super().__init__(*args, pady=5)
        self._lbl = tk.Label(self, text=text)
        self._edit = tk.Entry(self, width=width, bg='white', fg='black')
        self._lbl.pack(side=tk.LEFT)
        self._edit.pack(side=tk.LEFT, fill=tk.X)
        if hint:
            tk.Label(self, text=hint, fg='blue').pack(side=tk.LEFT)

    def get(self):
        return self._edit.get().strip()

    def set(self, input):
        self._edit.delete(0, tk.END)
        self._edit.insert(0, input)
        return self

    def pack(self, **kwargs):
        super().pack(**kwargs)
        return self

    def setEnabled(self, st):
        self._edit.config(state=tk.NORMAL if st else tk.DISABLED)
        return self


class FrameDirSelect(tk.Frame):
    '''
    ·��ѡ��
    '''
    def __init__(self, *args, text='·��'):
        super().__init__(*args, pady=5)
        self._lbl = tk.Label(self, text=text)
        self._edit = tk.Entry(self, width=50, bg='white', fg='black')
        self._btn = tk.Button(self, text='ѡ��', command=self.onSelectClick)
        self._lbl.pack(side=tk.LEFT)
        self._edit.pack(side=tk.LEFT, fill=tk.X)
        self._btn.pack(side=tk.LEFT)

    def onSelectClick(self):
        dir = askdirectory(initialdir=os.getcwd()).strip()
        if len(dir) > 0:
            self._edit.delete(0, tk.END)
            self._edit.insert(0, dir)

    def get(self):
        return self._edit.get()

    def pack(self, **kwargs):
        super().pack(**kwargs)
        return self


class FrameFetch(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self._pool = ThreadPoolExecutor(max_workers=1)
        self._task = None
        self.initUI()
        self.after(CFG.THREAD_CHECK_TIME_IN_MS, self._update)

    def initUI(self):
        self._editUrl = FrameEdit(self, text='��   ��:', width=55).pack(fill=tk.X)
        self._editMap = FrameEdit(self, text='��ͼ��:', hint='���Ӳ�ֵ {name}').pack(fill=tk.X)
        self._editRow = FrameEdit(self, text='�����:', hint='���Ӳ�ֵ {i} | {i+1}��ʾ������1��ʼ').set('�Զ���ȡ').setEnabled(False).pack(fill=tk.X)
        self._editCol = FrameEdit(self, text='�����:', hint='���Ӳ�ֵ {j}').set('�Զ���ȡ').setEnabled(False).pack(fill=tk.X)

        self._dir = FrameDirSelect(self, text='����·��').pack(fill=tk.X)
        self._btn = tk.Button(self, text='����', bg='green', command=self.onFetchClick)

        self._btn.pack(fill=tk.X)

    def _update(self):
        if self._task:
            if self._task.done():
                ret, err = self._task.result()
                if ret == 0:
                    messagebox.showinfo(message='�������')
                else:
                    messagebox.showerror(message=err)
                self._task = None
        self.after(CFG.THREAD_CHECK_TIME_IN_MS, self._update)

    def onFetchClick(self):
        if self._task:
            messagebox.showwarning(message='��ȴ���ǰ�������')
            return
        url = self._editUrl.get().strip()
        if len(url) == 0:
            messagebox.showinfo(message='����������')
            return
        mapname = self._editMap.get().strip()
        if len(mapname) == 0:
            messagebox.showinfo(message='�������ͼID')
            return
        dir = self._dir.get().strip()
        if len(dir) == 0:
            messagebox.showinfo(message='�����뱣��·��')
            return
        dir = os.path.abspath(dir)
        if not os.path.exists(dir):
            os.makedirs(dir)

        self._task = self._pool.submit(fetchMapRes, url, mapname, dir)


class FrameMerge(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.initUI()

    def initUI(self):
        self._dir = FrameDirSelect(self, text='ѡ��·��').pack(fill=tk.X)
        self._editMode = FrameEdit(self, text='ƴ��ģʽ', hint='*Ŀǰ֧��1|2|3(һά����)').set('1').pack(fill=tk.X)

        self._btn = tk.Button(self, text='�ϲ�', bg='green', command=self.onMergeClick)
        self._btn.pack(fill=tk.X)

    def onMergeClick(self):
        dir = self._dir.get().strip()
        if len(dir) == 0:
            messagebox.showinfo(message='�����뱣��·��')
            return
        dir = os.path.abspath(dir)
        if not os.path.exists(dir):
            messagebox.showerror(message='Ŀ¼������')
            return
        mode = self._editMode.get().strip()
        try:
            mode = int(mode)
        except ValueError:
            messagebox.showerror(message='ģʽ��������')
            return
        ret, err = mergeMap(dir, dir + '.jpg', mode=mode)
        if ret == 0:
            messagebox.showinfo(message='���')
        else:
            messagebox.showerror(message=err)


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('��ͼ���� v%s' % (_VERSION))
        self.geometry('450x350')
        self.resizable(False, False)
        self.initUI()
        self.after(CFG.CLI_UPDATE_TIME_IN_MS, self._update)

    def initUI(self):
        self._notebook = Notebook(self)
        self._notebook.add(FrameFetch(), text=' �� �� ')
        self._notebook.add(FrameMerge(), text=' �� �� ')
        self._notebook.pack(fill=tk.BOTH, expand=1)

        self._cli = tk.Text(self, bg="white", fg="black")
        self._cli.pack(fill=tk.BOTH)

    def _update(self):
        while not CLICache.empty():
            self._cli.config(state=tk.NORMAL)
            self._cli.insert(tk.END, CLICache.get())
            self._cli.see(tk.END)
        self._cli.config(state=tk.DISABLED)
        self.after(CFG.CLI_UPDATE_TIME_IN_MS, self._update)


if __name__ == '__main__':
    os.sys.stdout = CLICache
    GUI().mainloop()