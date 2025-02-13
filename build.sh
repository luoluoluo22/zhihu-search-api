#!/bin/bash

# 安装依赖
pip install -r requirements.txt

# 预先下载Chromium
python -c "from pyppeteer.chromium_downloader import download_chromium; download_chromium()"

echo "Chromium下载完成！" 