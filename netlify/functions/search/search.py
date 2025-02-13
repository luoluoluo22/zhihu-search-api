import json
import os
import asyncio
from pyppeteer import launch

async def search_zhihu(query='java'):
    browser = None
    try:
        browser = await launch(
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--disable-gpu',
                '--disable-dev-shm-usage'
            ],
            headless=True
        )
        
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        # 存储API响应数据
        api_data = None
        done = asyncio.Event()

        async def intercept_response(response):
            nonlocal api_data
            if 'api/v4/search_v3?' in response.url:
                try:
                    data = await response.json()
                    if 'error' not in data:
                        api_data = data
                        done.set()
                except Exception as e:
                    print(f"解析API响应时出错: {e}")

        page.on('response', lambda res: asyncio.ensure_future(intercept_response(res)))

        # 设置cookies
        cookies = []
        zhihu_cookies = os.environ.get('ZHIHU_COOKIES', '')
        for cookie_part in zhihu_cookies.split('; '):
            try:
                name, value = cookie_part.split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.zhihu.com',
                    'path': '/'
                })
            except ValueError:
                continue

        await page.setCookie(*cookies)
        
        # 访问搜索页面
        search_url = f'https://www.zhihu.com/search?type=content&q={query}'
        await page.goto(search_url, {
            'waitUntil': 'networkidle0',
            'timeout': 8000
        })
        
        try:
            await asyncio.wait_for(done.wait(), timeout=8)
        except asyncio.TimeoutError:
            return {"error": "获取数据超时"}
        
        return api_data or {"error": "未获取到数据"}

    except Exception as e:
        return {"error": str(e)}
        
    finally:
        if browser:
            await browser.close()

def handler(event, context):
    params = event.get('queryStringParameters', {})
    query = params.get('q', 'java')
    
    try:
        result = asyncio.run(search_zhihu(query))
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result, ensure_ascii=False)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        } 