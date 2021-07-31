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

## dev
### gen requirements
> pip install pipreqs  
> pipreqs . --encoding=gbk --force