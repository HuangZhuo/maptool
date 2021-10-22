pip install -r requirements.txt  
pyinstaller -F .\maptool.py -w
rmdir /q /s .\build
