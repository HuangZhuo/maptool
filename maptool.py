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
    def __init__(self, *args, text="输入", width=15):
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
            messagebox.showinfo(message=f'{self._text}输入为空')
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
    输入框封装
    '''
    def __init__(self, *args, text="输入", hint=None, width=15):
        super().__init__(*args, text=text, width=width)
        if hint:
            tk.Label(self, text=hint, fg='blue').pack(side=tk.LEFT)


class FrameDirSelect(FrameInput):
    '''
    路径选择封装
    '''
    def __init__(self, *args, text='路径'):
        super().__init__(*args, text=text, width=50)
        tk.Button(self, text='选择', command=self.onSelectClick).pack(side=tk.LEFT)

    def onSelectClick(self):
        dir = askdirectory(initialdir=os.getcwd()).strip()
        if len(dir) > 0:
            self._edit.delete(0, tk.END)
            self._edit.insert(0, dir)

    def get(self, bCheck=False):
        dir = self._edit.get().strip()
        if bCheck:
            if len(dir) == 0:
                messagebox.showinfo(message='请输入路径')
                return None
            dir = path.abspath(dir)
            if not path.exists(dir):
                messagebox.showerror(message='目录不存在')
                return None
        return dir


class FrameFileSelect(FrameDirSelect):
    def __init__(self, *args, text='文件路径'):
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
        self._editUrl = FrameEdit(self, text='链   接:', width=55).pack(fill=tk.X)
        self._editMap = FrameEdit(self, text='地图名:', hint='链接插值 {name}').pack(fill=tk.X)
        self._editRow = FrameEdit(self, text='最大行:',
                                  hint='链接插值 {i} | {i+1}表示索引从1开始').set('自动获取').setEnabled(False).pack(fill=tk.X)
        self._editCol = FrameEdit(self, text='最大列:', hint='链接插值 {j}').set('自动获取').setEnabled(False).pack(fill=tk.X)

        self._dir = FrameDirSelect(self, text='保存路径').pack(fill=tk.X)
        tk.Button(self, text='测  试', command=self.onTestClick).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(self, text='下  载', bg='green', command=self.onFetchClick).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _update(self):
        if self._task:
            if self._task.done():
                ret, err = self._task.result()
                if ret == 0:
                    messagebox.showinfo(message='下载完成')
                else:
                    messagebox.showerror(message=err)
                self._task = None
        self.after(CFG.THREAD_CHECK_TIME_IN_MS, self._update)

    def onTestClick(self):
        url = self._editUrl.get().strip()
        if len(url) == 0:
            messagebox.showinfo(message='请输入链接')
            return
        mapname = self._editMap.get().strip()
        if len(mapname) == 0:
            messagebox.showinfo(message='请输入地图ID')
            return
        if checkMapResExist(url, mapname):
            messagebox.showinfo(message='资源可以下载')
        else:
            messagebox.showerror(message='资源不存在')

    def onFetchClick(self):
        if self._task:
            messagebox.showwarning(message='请等待当前任务完成')
            return
        url = self._editUrl.get().strip()
        if len(url) == 0:
            messagebox.showinfo(message='请输入链接')
            return
        mapname = self._editMap.get().strip()
        if len(mapname) == 0:
            messagebox.showinfo(message='请输入地图ID')
            return
        dir = self._dir.get()
        if len(dir) == 0:
            messagebox.showinfo(message='请输入保存路径')
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
        self._dir = FrameDirSelect(self, text='选择路径').pack(fill=tk.X)
        self._editMode = FrameEdit(self, text='拼接模式', hint='*1-二维索引，2-二维索引反转，3-一维索引').set('1').pack(fill=tk.X)
        self._editFmt = FrameEdit(self, text='文件匹配', hint='*例如：{i}_{j}.jpg').set('{i}_{j}.jpg').pack(fill=tk.X)
        self._editJMax = FrameEdit(self, text='横向块数', hint='*一维索引模式用').pack(fill=tk.X)
        self._editIMax = FrameEdit(self, text='竖向块数').set('自动获取').setEnabled(False).pack(fill=tk.X)

        self._btn = tk.Button(self, text='合并', bg='green', command=self.onMergeClick)
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
            messagebox.showerror(message='模式输入有误')
            return
        # jmax
        jmax = self._editJMax.get().strip()
        try:
            if len(jmax) == 0:
                jmax = None
            else:
                jmax = int(jmax)
        except ValueError:
            messagebox.showerror(message='块数输入有误')
            return
        # fmt
        fmt = self._editFmt.get().strip()
        fmt = fmt if len(fmt) > 0 else None

        ret, err = mergeMap(dir, mode=mode, file_format=fmt, j_max=jmax)
        if ret == 0:
            messagebox.showinfo(message='完成')
        else:
            messagebox.showerror(message=err)


class FrameAtlasSplit(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.initUI()

    def initUI(self):
        tk.Label(self, text='将目录下所有.atlas图集，拆分为散图').pack(fill=tk.X)
        self._dir = FrameDirSelect(self, text='选择路径').pack(fill=tk.X)
        self._btn = tk.Button(self, text='拆分', bg='green', command=self.onSplitClick)
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
        messagebox.showinfo(message=f'完成拆分{count}个图集')


class FrameResFetch(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self._task = None
        self._progress = 0
        self.initUI()
        self.after(CFG.THREAD_CHECK_TIME_IN_MS, self._update)

    def initUI(self):
        self._editUrl = FrameEdit(self, text='链   接:', width=55).pack(fill=tk.X)
        self._dir = FrameFileSelect(self, text='清单路径:').pack(fill=tk.X)
        self._namePattrn = FrameEdit(self, text='文件匹配:', hint='*下载清单中匹配的文件', width=25).pack(fill=tk.X)
        self._saveDir = FrameDirSelect(self, text='保存路径:').pack(fill=tk.X)
        self._btn = tk.Button(self, text='下载', bg='green', command=self.onFetchClick)
        self._btn.pack(fill=tk.X)

        self._bar = Progressbar(self, maximum=100, value=0)
        self._bar.pack(pady=5, fill=tk.X)

    def _update(self):
        if self._task:
            self._bar['value'] = self._progress
            if self._task.done():
                ret, err = self._task.result()
                if ret == 0:
                    messagebox.showinfo(message='下载完成')
                else:
                    messagebox.showerror(message=err)
                self._task = None
        self.after(CFG.THREAD_CHECK_TIME_IN_MS, self._update)

    def onFetchClick(self):
        if self._task:
            messagebox.showwarning(message='请等待当前任务完成')
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
            messagebox.showerror(message=f'清单文件{dir}解析失败')
            return
        pattrn = self._namePattrn.get(True)
        if not pattrn:
            return
        tmp = resfetch.getResList(mani, pattrn)
        if len(tmp) == 0:
            messagebox.showinfo(message=f'匹配的下载列表为空')
            return
        if not messagebox.askokcancel(message=f'匹配到{len(tmp)}个文件，是否确认下载'):
            return

        self._progress = 0
        self._task = TaskExecutor.submit(resfetch.fetchAll, url, tmp, savedir, self.onProgress)

    def onProgress(self, total, cur, data):
        self._progress = math.ceil(cur * 100 / total)
        print(f'({cur}/{total}) {data}')


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('地图工具 v%s' % (_VERSION))
        self.geometry('450x350')
        self.resizable(False, False)
        self.initUI()
        self.after(CFG.CLI_UPDATE_TIME_IN_MS, self._update)

    def initUI(self):
        self._notebook = Notebook(self)
        self._notebook.add(FrameFetch(), text=' 下 载 ')
        self._notebook.add(FrameMerge(), text=' 合 并 ')
        self._notebook.add(FrameAtlasSplit(), text='atlas拆分')
        self._notebook.add(FrameResFetch(), text='清单下载')
        self._notebook.pack(fill=tk.BOTH, expand=1)
        # self._notebook.select(3)  # 选中第4个

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