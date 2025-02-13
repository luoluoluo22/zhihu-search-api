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

# 将Chromium路径写入系统环境变量
export CHROMIUM_PATH="${CHROMIUM_PATH}"

# 创建持久化的环境变量文件
mkdir -p /opt/render/project/
echo "export CHROMIUM_PATH=${CHROMIUM_PATH}" > /opt/render/project/.env

# 确保当前用户可以访问Chromium
chmod -R 755 $(dirname "${CHROMIUM_PATH}") 