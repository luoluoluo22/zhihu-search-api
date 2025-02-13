#!/bin/bash

# 安装依赖
pip install -r requirements.txt

# 创建目录
mkdir -p /opt/render/.local/share/pyppeteer/local-chromium/

# 预先下载Chromium
python -c "
from pyppeteer.chromium_downloader import download_chromium
download_chromium()
"

# 设置权限
chmod -R 755 /opt/render/.local/share/pyppeteer/local-chromium/

echo "Chromium下载完成！" 