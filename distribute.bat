REM deleted old data
rmdir /s /q dist
rmdir /s /q build

REM package
pyinstaller main.py
