#!/bin/bash

# 安装依赖
pip install -r requirements.txt

# 预先下载Chromium并获取路径
CHROMIUM_PATH=$(python -c "
from pyppeteer.chromium_downloader import download_chromium, chromium_executable
download_chromium()
print(chromium_executable())
")

echo "Chromium下载完成！路径: ${CHROMIUM_PATH}"

# 将Chromium路径写入render环境变量
echo "CHROMIUM_PATH=${CHROMIUM_PATH}" >> .env 