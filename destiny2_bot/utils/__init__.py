import aiohttp
import os
import requests

async def download_file(url: str, filename: str):
    figdir = os.path.dirname(filename)
    if not os.path.exists(figdir):
        os.makedirs(figdir)

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, verify_ssl=False)
        content = await response.read()

    with open(filename, 'wb') as f:
        f.write(content)
    return 1

async def write_file(data: str, filename: str):
    figdir = os.path.dirname(filename)
    if not os.path.exists(figdir):
        os.makedirs(figdir)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(data)
    return 1

async def paste(code):
    url1 = 'https://netcut.cn/api/note/update/'
    url2 = 'https://netcut.cn/4er7ucs8kfg0'
    data = {
        "note_id": (None, "624e25a60d56cd0a"),
        "note_content": (None, code)
    }
    r = requests.post(url1, files = data,verify=False)
    status = r.json().get('status')
    return url2 if status == 1 else None
