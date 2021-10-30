# -*- coding:gbk -*

import os
import os.path as path
import math
import encodings.idna  # LookupError: unknown encoding: idna
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Notebook
from tkinter.ttk import Progressbar
from tkinter.filedialog import askdirectory, askopenfile

from mapmerge import mergeMap
from mapfetch import checkMapResExist
from mapfetch import fetchMapRes
from splitLayaAtlas.splitLayaAtlas import dispose1file
import resfetch

_VERSION = '0.0.6'


class CFG:
    CLI_UPDATE_TIME_IN_MS = 100
    THREAD_CHECK_TIME_IN_MS = 10


TaskExecutor = ThreadPoolExecutor(max_workers=1)


class CLICache:
    __queue = Queue()

    @classmethod
    def write(cls, str):
        cls.__queue.put(str)

    @classmethod
    def empty(cls):
        return cls.__queue.empty()

    @classmethod
    def get(cls):
        return cls.__queue.get()


class FrameInput(tk.Frame):
    def __init__(self, *args, text="����", width=15):
        super().__init__(*args, pady=5)
        tk.Label(self, text=text).pack(side=tk.LEFT)
        self._text = text
        self._edit = tk.Entry(self, width=width, bg='white', fg='black')
        self._edit.pack(side=tk.LEFT, fill=tk.X, ipady=1)

    def pack(self, **kwargs):
        super().pack(**kwargs)
        return self

    def get(self, bCheckEmpty=False):
        ret = self._edit.get().strip()
        if bCheckEmpty and len(ret) == 0:
            messagebox.showinfo(message=f'{self._text}����Ϊ��')
            return None
        return ret

    def set(self, input):
        self._edit.delete(0, tk.END)
        self._edit.insert(0, input)
        return self

    def setEnabled(self, st):
        self._edit.config(state=tk.NORMAL if st else tk.DISABLED)
        return self


class FrameEdit(FrameInput):
    '''
    ������װ
    '''
    def __init__(self, *args, text="����", hint=None, width=15):
        super().__init__(*args, text=text, width=width)
        if hint:
            tk.Label(self, text=hint, fg='blue').pack(side=tk.LEFT)


class FrameDirSelect(FrameInput):
    '''
    ·��ѡ���װ
    '''
    def __init__(self, *args, text='·��'):
        super().__init__(*args, text=text, width=50)
        tk.Button(self, text='ѡ��', command=self.onSelectClick).pack(side=tk.LEFT)

    def onSelectClick(self):
        dir = askdirectory(initialdir=os.getcwd()).strip()
        if len(dir) > 0:
            self._edit.delete(0, tk.END)
            self._edit.insert(0, dir)

    def get(self, bCheck=False):
        dir = self._edit.get().strip()
        if bCheck:
            if len(dir) == 0:
                messagebox.showinfo(message='������·��')
                return None
            dir = path.abspath(dir)
            if not path.exists(dir):
                messagebox.showerror(message='Ŀ¼������')
                return None
        return dir


class FrameFileSelect(FrameDirSelect):
    def __init__(self, *args, text='�ļ�·��'):
        super().__init__(*args, text=text)

    def onSelectClick(self):
        dir = askopenfile(initialdir=os.getcwd())
        if dir and len(dir.name) > 0:
            self._edit.delete(0, tk.END)
            self._edit.insert(0, dir.name)


class FrameFetch(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self._task = None
        self.initUI()
        self.after(CFG.THREAD_CHECK_TIME_IN_MS, self._update)

    def initUI(self):
        self._editUrl = FrameEdit(self, text='��   ��:', width=55).pack(fill=tk.X)
        self._editMap = FrameEdit(self, text='��ͼ��:', hint='���Ӳ�ֵ {name}').pack(fill=tk.X)
        self._editRow = FrameEdit(self, text='�����:',
                                  hint='���Ӳ�ֵ {i} | {i+1}��ʾ������1��ʼ').set('�Զ���ȡ').setEnabled(False).pack(fill=tk.X)
        self._editCol = FrameEdit(self, text='�����:', hint='���Ӳ�ֵ {j}').set('�Զ���ȡ').setEnabled(False).pack(fill=tk.X)

        self._dir = FrameDirSelect(self, text='����·��').pack(fill=tk.X)
        tk.Button(self, text='��  ��', command=self.onTestClick).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(self, text='��  ��', bg='green', command=self.onFetchClick).pack(side=tk.LEFT, fill=tk.X, expand=True)

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

    def onTestClick(self):
        url = self._editUrl.get().strip()
        if len(url) == 0:
            messagebox.showinfo(message='����������')
            return
        mapname = self._editMap.get().strip()
        if len(mapname) == 0:
            messagebox.showinfo(message='�������ͼID')
            return
        if checkMapResExist(url, mapname):
            messagebox.showinfo(message='��Դ��������')
        else:
            messagebox.showerror(message='��Դ������')

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
        dir = self._dir.get()
        if len(dir) == 0:
            messagebox.showinfo(message='�����뱣��·��')
            return
        dir = path.abspath(dir)
        if not path.exists(dir):
            os.makedirs(dir)

        self._task = TaskExecutor.submit(fetchMapRes, url, mapname, dir)


class FrameMerge(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.initUI()

    def initUI(self):
        self._dir = FrameDirSelect(self, text='ѡ��·��').pack(fill=tk.X)
        self._editMode = FrameEdit(self, text='ƴ��ģʽ', hint='*1-��ά������2-��ά������ת��3-һά����').set('1').pack(fill=tk.X)
        self._editFmt = FrameEdit(self, text='�ļ�ƥ��', hint='*���磺{i}_{j}.jpg').set('{i}_{j}.jpg').pack(fill=tk.X)
        self._editJMax = FrameEdit(self, text='�������', hint='*һά����ģʽ��').pack(fill=tk.X)
        self._editIMax = FrameEdit(self, text='�������').set('�Զ���ȡ').setEnabled(False).pack(fill=tk.X)

        self._btn = tk.Button(self, text='�ϲ�', bg='green', command=self.onMergeClick)
        self._btn.pack(fill=tk.X)

    def onMergeClick(self):
        # dir
        dir = self._dir.get(True)
        if not dir:
            return
        # mode
        mode = self._editMode.get().strip()
        try:
            mode = int(mode)
        except ValueError:
            messagebox.showerror(message='ģʽ��������')
            return
        # jmax
        jmax = self._editJMax.get().strip()
        try:
            if len(jmax) == 0:
                jmax = None
            else:
                jmax = int(jmax)
        except ValueError:
            messagebox.showerror(message='������������')
            return
        # fmt
        fmt = self._editFmt.get().strip()
        fmt = fmt if len(fmt) > 0 else None

        ret, err = mergeMap(dir, mode=mode, file_format=fmt, j_max=jmax)
        if ret == 0:
            messagebox.showinfo(message='���')
        else:
            messagebox.showerror(message=err)


class FrameAtlasSplit(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.initUI()

    def initUI(self):
        tk.Label(self, text='��Ŀ¼������.atlasͼ�������Ϊɢͼ').pack(fill=tk.X)
        self._dir = FrameDirSelect(self, text='ѡ��·��').pack(fill=tk.X)
        self._btn = tk.Button(self, text='���', bg='green', command=self.onSplitClick)
        self._btn.pack(fill=tk.X)

    def onSplitClick(self):
        dir = self._dir.get()
        if not dir:
            return
        count = 0
        for d in os.listdir(dir):
            filename = path.join(dir, d)
            if path.isdir(filename):
                continue
            name, ext = path.splitext(filename)
            if ext == '.atlas':
                try:
                    dispose1file(name)
                    count += 1
                except Exception as e:
                    print(repr(e))
                    break
        messagebox.showinfo(message=f'��ɲ��{count}��ͼ��')


class FrameResFetch(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self._task = None
        self._progress = 0
        self.initUI()
        self.after(CFG.THREAD_CHECK_TIME_IN_MS, self._update)

    def initUI(self):
        self._editUrl = FrameEdit(self, text='��   ��:', width=55).pack(fill=tk.X)
        self._dir = FrameFileSelect(self, text='�嵥·��:').pack(fill=tk.X)
        self._namePattrn = FrameEdit(self, text='�ļ�ƥ��:', hint='*�����嵥��ƥ����ļ�', width=25).pack(fill=tk.X)
        self._saveDir = FrameDirSelect(self, text='����·��:').pack(fill=tk.X)
        self._btn = tk.Button(self, text='����', bg='green', command=self.onFetchClick)
        self._btn.pack(fill=tk.X)

        self._bar = Progressbar(self, maximum=100, value=0)
        self._bar.pack(pady=5, fill=tk.X)

    def _update(self):
        if self._task:
            self._bar['value'] = self._progress
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
        url = self._editUrl.get(True)
        if not url:
            return
        savedir = self._saveDir.get(True)
        if not savedir:
            return
        dir = self._dir.get(True)
        if not dir:
            return
        mani = resfetch.parseManifest(dir)
        if not mani:
            messagebox.showerror(message=f'�嵥�ļ�{dir}����ʧ��')
            return
        pattrn = self._namePattrn.get(True)
        if not pattrn:
            return
        tmp = resfetch.getResList(mani, pattrn)
        if len(tmp) == 0:
            messagebox.showinfo(message=f'ƥ��������б�Ϊ��')
            return
        if not messagebox.askokcancel(message=f'ƥ�䵽{len(tmp)}���ļ����Ƿ�ȷ������'):
            return

        self._progress = 0
        self._task = TaskExecutor.submit(resfetch.fetchAll, url, tmp, savedir, self.onProgress)

    def onProgress(self, total, cur, data):
        self._progress = math.ceil(cur * 100 / total)
        print(f'({cur}/{total}) {data}')


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
        self._notebook.add(FrameAtlasSplit(), text='atlas���')
        self._notebook.add(FrameResFetch(), text='�嵥����')
        self._notebook.pack(fill=tk.BOTH, expand=1)
        # self._notebook.select(3)  # ѡ�е�4��

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