#!/bin/bash

# 安装依赖
pip install -r requirements.txt

# 设置pyppeteer的home目录
export PYPPETEER_HOME="/opt/render/.local/share/pyppeteer"

# 创建必要的目录
mkdir -p /opt/render/.local/share/pyppeteer/local-chromium/588429/chrome-linux/

# 预先下载Chromium
python -c "
import os
import shutil
from pyppeteer.chromium_downloader import download_chromium, chromium_executable

# 设置环境变量
os.environ['PYPPETEER_HOME'] = '/opt/render/.local/share/pyppeteer'

# 下载Chromium
download_chromium()

# 获取下载后的路径
chrome_path = chromium_executable()
print(f'Chromium路径: {chrome_path}')

# 确保目录存在
os.makedirs(os.path.dirname(chrome_path), exist_ok=True)

# 检查文件是否存在
if os.path.exists(chrome_path):
    print('Chromium已成功下载')
    # 设置执行权限
    os.chmod(chrome_path, 0o755)
    print('已设置执行权限')
else:
    print('Chromium下载可能失败')
"

# 检查文件是否存在和权限
CHROME_PATH="/opt/render/.local/share/pyppeteer/local-chromium/588429/chrome-linux/chrome"
if [ -f "$CHROME_PATH" ]; then
    echo "Chrome文件存在"
    ls -l "$CHROME_PATH"
    # 确保有执行权限
    chmod 755 "$CHROME_PATH"
else
    echo "Chrome文件不存在: $CHROME_PATH"
    # 列出目录内容以供调试
    echo "目录内容:"
    ls -la /opt/render/.local/share/pyppeteer/local-chromium/ 