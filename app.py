import asyncio
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pyppeteer import launch
from dotenv import load_dotenv
import sys
import platform
import signal
import atexit

# 加载环境变量
load_dotenv()

app = FastAPI()

# 存储全局的浏览器实例和事件循环
browser_instances = set()
loop = None

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def cleanup_browser(browser):
    """安全地清理浏览器实例"""
    if browser:
        try:
            browser_instances.discard(browser)
            if not browser.process.returncode:
                await browser.close()
        except Exception as e:
            print(f"关闭浏览器时出错: {e}")

async def cleanup_all_browsers():
    """清理所有浏览器实例"""
    tasks = [cleanup_browser(browser) for browser in browser_instances.copy()]
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

@app.on_event("startup")
async def startup_event():
    """服务启动时的初始化"""
    global loop
    loop = asyncio.get_running_loop()
    
@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时的清理"""
    await cleanup_all_browsers()

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
        
        # 优先检查项目目录中的Chrome
        project_chrome_path = os.path.join(os.getcwd(), ".local-chromium/chrome-linux/chrome")
        print(f"\n检查项目目录中的Chrome: {project_chrome_path}")
        
        if os.path.exists(project_chrome_path):
            print("找到项目目录中的Chrome")
            chromium_path = project_chrome_path
            try:
                os.chmod(project_chrome_path, 0o755)
                print("已设置执行权限")
            except Exception as e:
                print(f"设置权限失败: {e}")
        else:
            print("项目目录中未找到Chrome")
            
            # 检查环境变量指定的路径
            if os.path.exists(chromium_path):
                print(f"使用环境变量指定的Chrome: {chromium_path}")
                try:
                    os.chmod(chromium_path, 0o755)
                    print("已设置执行权限")
                except Exception as e:
                    print(f"设置权限失败: {e}")
            else:
                raise Exception(f"未找到可用的Chrome可执行文件，已检查路径: {project_chrome_path}, {chromium_path}")

        print(f"\n最终使用的Chromium路径: {chromium_path}")
        launch_options['executablePath'] = chromium_path

        # 启动浏览器
        browser = await launch(**launch_options)
        browser_instances.add(browser)
        
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
            await cleanup_browser(browser)

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