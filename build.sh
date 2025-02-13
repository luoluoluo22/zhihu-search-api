#!/bin/bash

# 安装依赖
pip install -r requirements.txt

# 创建目录
mkdir -p /opt/render/.local/share/pyppeteer/local-chromium/588429/chrome-linux/

# 预先下载Chromium
python -c "
import os
from pyppeteer.chromium_downloader import download_chromium
os.environ['PYPPETEER_HOME'] = '/opt/render/.local/share/pyppeteer'
download_chromium()
"

# 设置权限
chmod -R 755 /opt/render/.local/share/pyppeteer/local-chromium/

echo "Chromium下载完成！"
ls -la /opt/render/.local/share/pyppeteer/local-chromium/588429/chrome-linux/ 