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
    
    # 复制整个chrome-linux目录到项目目录
    source_dir = os.path.dirname(chrome_path)  # chrome-linux目录
    project_chrome_dir = '/opt/render/project/src/.local-chromium/chrome-linux'
    
    # 如果目标目录已存在，先删除
    if os.path.exists(project_chrome_dir):
        shutil.rmtree(project_chrome_dir)
    
    # 复制整个目录
    shutil.copytree(source_dir, project_chrome_dir)
    print(f'已复制Chrome目录到: {project_chrome_dir}')
    
    # 设置所有文件的权限
    for root, dirs, files in os.walk(project_chrome_dir):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            os.chmod(os.path.join(root, f), 0o755)
    
    print('已设置所有文件的执行权限')
    
    # 列出复制的文件
    print('\n复制的文件列表:')
    for root, dirs, files in os.walk(project_chrome_dir):
        for f in files:
            print(os.path.join(root, f))
else:
    print('Chromium下载可能失败')
    exit(1)
"

# 检查项目目录中的Chrome
PROJECT_CHROME_PATH="/opt/render/project/src/.local-chromium/chrome-linux/chrome"
if [ -f "$PROJECT_CHROME_PATH" ]; then
    echo "项目目录中的Chrome文件存在"
    ls -l "$PROJECT_CHROME_PATH"
    
    # 将Chrome路径写入环境变量文件
    echo "CHROMIUM_PATH=$PROJECT_CHROME_PATH" > /opt/render/project/.env
    echo "已将Chrome路径写入环境变量文件"
    
    # 确保当前会话也能使用
    export CHROMIUM_PATH="$PROJECT_CHROME_PATH"
    
    # 列出chrome-linux目录的完整内容
    echo "chrome-linux目录内容:"
    ls -la $(dirname "$PROJECT_CHROME_PATH")
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