import aiohttp
import os
from destiny2_bot.utils import download_file
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message

today_report = on_command("today_report", aliases={'日报', }, priority=5)

@today_report.handle()
async def _(bot: Bot, event: Event, state: T_State):
    ret = await get_today_report()
    await today_report.send(Message(ret))

async def get_today_report():
    url = 'http://www.tianque.top/d2api/today/'
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url)
        data = await response.json()
    figurl, figname = data['img_url'],f"{data['img_hash_md5']}-{data['img_name']}"
    fig_dir = os.path.join(os.getcwd(), 'data', 'today_report', figname)
    if not os.path.exists(fig_dir):
        if not await download_file(figurl, fig_dir):
            return '失败了'
    return f"[CQ:image,file=file:///{fig_dir}]"

