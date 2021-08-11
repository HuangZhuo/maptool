# maptool
用于传奇地图的小工具，目前功能：
- 从链接下载指定地图所有地图块
- 将地图块合并成大地图

## demo
![maptool_demo.gif](assets/maptool_demo.gif)

## build
python3 only!
> pip install -r requirements.txt  
> pyinstaller -F .\maptool.py -w

## history
### V0.0.1
- 完成基本功能
### V0.0.2
- 多线程改造，下载不阻塞UI
### V0.0.3
- 下载模式可扩展，支持更多源
- 支持一维索引地图块拼接
### V0.0.4
- 拼接功能优化

## dev
### gen requirements
> pip install pipreqs  
> pipreqs . --encoding=gbk --force