import os,ujson,aiofiles

async def readTo(p):
    if not os.path.exists(p):
        return 0
    async with aiofiles.open(p, 'r', encoding='utf-8') as f:
        content = await f.read()
    content = ujson.loads(content)
    return content


async def writeTo(p, info):
    async with aiofiles.open(p, 'w', encoding='utf-8') as f:
        await f.write(ujson.dumps(info))
    return 1