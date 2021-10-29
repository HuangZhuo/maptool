# maptool
用于传奇地图的小工具，目前功能：
- 从链接下载指定地图所有地图块（仅供参考学习）
- 将地图块合并成大地图

## build
python3 only!
> build.bat

## plan
- [x] 添加测试按钮检查资源是否可用
- [ ] 停止下载功能
- [ ] 设置地图id搜索区间批量下载地图并自动完成合并

## history
### V0.0.5
- 集成.atlas拆分功能
### V0.0.4
- 拼接功能优化
### V0.0.3
- 下载模式可扩展，支持更多源
- 支持一维索引地图块拼接
### V0.0.2
- 多线程改造，下载不阻塞UI
### V0.0.1
- 完成基本功能

## dev
### todo
- [ ] 文件资源释放问题，应该是使用`with Image.open`
### gen requirements
> pip install pipreqs  
> pipreqs . --encoding=gbk --force

### refs
[pillow](https://pillow.readthedocs.io/en/latest/index.html)