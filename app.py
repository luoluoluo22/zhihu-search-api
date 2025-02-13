import asyncio
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pyppeteer import launch
from dotenv import load_dotenv
import sys
import platform
import glob

# 加载环境变量
load_dotenv()

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def search_zhihu(query: str):
    browser = None
    try:
        # 设置Chrome启动参数
        chrome_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--window-size=1920,1080',
            '--start-maximized',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer',
            '--disable-extensions',
            '--no-first-run',
            '--disable-notifications'
        ]

        # 配置浏览器启动选项
        launch_options = {
            'headless': True,
            'args': chrome_args,
            'ignoreHTTPSErrors': True,
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False
        }

        # 获取Chromium路径
        chromium_path = os.getenv('CHROMIUM_PATH')
        if not chromium_path:
            raise Exception("未找到Chromium路径环境变量")
        
        print(f"当前工作目录: {os.getcwd()}")
        print(f"环境变量中的Chromium路径: {chromium_path}")
        
        # 检查目录结构
        base_dir = "/opt/render/.local/share/pyppeteer/local-chromium/588429"
        print(f"\n检查基础目录是否存在: {os.path.exists(base_dir)}")
        
        # 检查pyppeteer的home目录
        pyppeteer_home = os.getenv('PYPPETEER_HOME', '/opt/render/.local/share/pyppeteer')
        print(f"\nPYPPETEER_HOME: {pyppeteer_home}")
        if os.path.exists(pyppeteer_home):
            print("PYPPETEER_HOME目录内容:")
            for root, dirs, files in os.walk(pyppeteer_home):
                print(f"\n当前目录: {root}")
                if dirs:
                    print("子目录:", dirs)
                if files:
                    print("文件:", files)

        # 尝试不同的可能路径
        possible_paths = [
            chromium_path,  # 环境变量中的路径
            "/opt/render/.local/share/pyppeteer/local-chromium/588429/chrome-linux/chrome",  # 预期路径
            os.path.join(os.getcwd(), ".local-chromium/chrome-linux/chrome"),  # 相对于当前目录
            os.path.join(pyppeteer_home, "local-chromium/588429/chrome-linux/chrome")  # 相对于PYPPETEER_HOME
        ]

        chrome_found = False
        for path in possible_paths:
            print(f"\n检查路径: {path}")
            if os.path.exists(path):
                print(f"找到Chrome: {path}")
                try:
                    os.chmod(path, 0o755)
                    print("已设置执行权限")
                    chromium_path = path
                    chrome_found = True
                    break
                except Exception as e:
                    print(f"设置权限失败: {e}")
            else:
                print("路径不存在")

        if not chrome_found:
            # 搜索整个目录树
            print("\n开始全局搜索chrome可执行文件...")
            search_paths = [
                "/opt/render/.local/share/pyppeteer",
                "/opt/render/.local/share",
                os.getcwd()
            ]
            for search_path in search_paths:
                if os.path.exists(search_path):
                    for root, dirs, files in os.walk(search_path):
                        if 'chrome' in files:
                            found_path = os.path.join(root, 'chrome')
                            print(f"找到可能的Chrome: {found_path}")
                            chromium_path = found_path
                            chrome_found = True
                            try:
                                os.chmod(found_path, 0o755)
                                print("已设置执行权限")
                                break
                            except Exception as e:
                                print(f"设置权限失败: {e}")

        if not chrome_found:
            raise Exception("未找到可用的Chrome可执行文件")

        print(f"\n最终使用的Chromium路径: {chromium_path}")
        launch_options['executablePath'] = chromium_path

        # 启动浏览器
        browser = await launch(**launch_options)
        
        page = await browser.newPage()
        
        # 设置浏览器特征
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        await page.setViewport({'width': 1920, 'height': 1080})
        
        # 注入反检测代码
        await page.evaluateOnNewDocument('''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        ''')

        # 存储API响应数据
        api_data = None
        done = asyncio.Event()

        # 监听网络请求
        async def intercept_response(response):
            nonlocal api_data
            if 'api/v4/search_v3?' in response.url:
                try:
                    data = await response.json()
                    if 'error' not in data:
                        api_data = data
                        done.set()
                        return api_data
                except Exception as e:
                    print(f"解析API响应时出错: {e}")

        page.on('response', lambda res: asyncio.ensure_future(intercept_response(res)))

        # 从环境变量获取cookie
        cookie_str = os.getenv('ZHIHU_COOKIE')
        if not cookie_str:
            raise Exception("未找到知乎cookie")

        cookies = []
        for cookie_part in cookie_str.split('; '):
            try:
                name, value = cookie_part.split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.zhihu.com',
                    'path': '/'
                })
            except ValueError as e:
                print(f"解析cookie时出错: {cookie_part}, 错误: {e}")

        # 设置cookies
        await page.setCookie(*cookies)
        
        # 访问搜索页面
        search_url = f'https://www.zhihu.com/search?type=content&q={query}'
        await page.goto(search_url, {
            'waitUntil': 'networkidle0',
            'timeout': 30000
        })
        
        # 等待API数据
        try:
            await asyncio.wait_for(done.wait(), timeout=10)
        except asyncio.TimeoutError:
            raise Exception("获取API数据超时")
        
        return api_data

    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass

@app.get("/")
async def root():
    return {"message": "知乎搜索API服务正常运行中"}

@app.get("/search/{query}")
async def search(query: str):
    try:
        result = await search_zhihu(query)
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="搜索失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 