# -*- coding:gbk -*

import os
import os.path
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Notebook
from tkinter.filedialog import askdirectory

from mapmerge import mergeMap
from mapfetch import fetchMapRes

_VERSION = '0.0.4'


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


class FrameEdit(tk.Frame):
    '''
    ������װ
    '''
    def __init__(self, *args, text="����", hint=None, width=15):
        super().__init__(*args, pady=5)
        tk.Label(self, text=text).pack(side=tk.LEFT)
        self._edit = tk.Entry(self, width=width, bg='white', fg='black')
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
    ·��ѡ���װ
    '''
    def __init__(self, *args, text='·��'):
        super().__init__(*args, pady=5)
        tk.Label(self, text=text).pack(side=tk.LEFT)
        self._edit = tk.Entry(self, width=50, bg='white', fg='black')
        self._edit.pack(side=tk.LEFT, fill=tk.X)
        tk.Button(self, text='ѡ��', command=self.onSelectClick).pack(side=tk.LEFT)

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
        dir = self._dir.get().strip()
        if len(dir) == 0:
            messagebox.showinfo(message='������·��')
            return
        dir = os.path.abspath(dir)
        if not os.path.exists(dir):
            messagebox.showerror(message='Ŀ¼������')
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