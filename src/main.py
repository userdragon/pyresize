name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build with PyInstaller
      run: |
        pyinstaller --onefile --windowed src/main.py --icon=icon.ico --name=pyresize --hidden-import=tkinterdnd2 --collect-all=tkinterdnd2

    - name: Upload release asset
      uses: softprops/action-gh-release@v2
      with:
        files: dist/pyresize.exe
    
