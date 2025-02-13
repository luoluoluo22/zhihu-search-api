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
    
    # 复制到项目目录
    project_chrome_dir = '/opt/render/project/src/.local-chromium/chrome-linux'
    os.makedirs(project_chrome_dir, exist_ok=True)
    project_chrome_path = os.path.join(project_chrome_dir, 'chrome')
    shutil.copy2(chrome_path, project_chrome_path)
    os.chmod(project_chrome_path, 0o755)
    print(f'已复制Chrome到项目目录: {project_chrome_path}')
else:
    print('Chromium下载可能失败')
"

# 检查项目目录中的Chrome
PROJECT_CHROME_PATH="/opt/render/project/src/.local-chromium/chrome-linux/chrome"
if [ -f "$PROJECT_CHROME_PATH" ]; then
    echo "项目目录中的Chrome文件存在"
    ls -l "$PROJECT_CHROME_PATH"
    # 确保有执行权限
    chmod 755 "$PROJECT_CHROME_PATH"
    
    # 将Chrome路径写入环境变量文件
    echo "CHROMIUM_PATH=$PROJECT_CHROME_PATH" > /opt/render/project/.env
    echo "已将Chrome路径写入环境变量文件"
    
    # 确保当前会话也能使用
    export CHROMIUM_PATH="$PROJECT_CHROME_PATH"
else
    echo "项目目录中的Chrome文件不存在: $PROJECT_CHROME_PATH"
    exit 1
fi

# 验证环境变量
echo "当前CHROMIUM_PATH环境变量: $CHROMIUM_PATH"
echo "环境变量文件内容:"
cat /opt/render/project/.env

# 输出最终状态
echo "构建脚本完成" 