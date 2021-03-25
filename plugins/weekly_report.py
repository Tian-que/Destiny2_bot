import os
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message
from destiny2_bot.utils import download_file
from bilibili_api import *

request_settings = {
    "use_https": True,
    "proxies": None
}

weekly_report = on_command("weekly_report", aliases={'周报', '老九', '试炼', }, priority=5)


@weekly_report.handle()
async def _(bot: Bot, event: Event, state: T_State):
    target = event.raw_message
    if target == '周报':
        figurl, figname = await get_weekly_report()
    elif target == '老九':
        figurl, figname = await get_9_report()
    elif target == '试炼':
        figurl, figname = await get_osiris_report()
    else:
        return 0
    figname = figname + '.jpg'
    fig_dir = os.path.join(os.getcwd(), 'data', 'weekly_report', figname)
    if not os.path.exists(fig_dir):
        if not await download_file(figurl, fig_dir):
            await weekly_report.send('失败了')
            return
    await weekly_report.send(Message(f"[CQ:image,file=file:///{fig_dir}]"))


async def get_weekly_report():
    articles_generator = user.get_articles_g(uid=514771)
    for articles in articles_generator:
        if '命运2周报' in articles['title']:
            cv = articles['id']
            fig_url = article.get_content(cid=cv).paragraphs[3].node_list[0].url
            return [fig_url, articles['title']]


async def get_9_report():
    articles_generator = user.get_articles_g(uid=514771)
    for articles in articles_generator:
        if '苏尔情报' in articles['title']:
            cv = articles['id']
            fig_url = article.get_content(cid=cv).paragraphs[3].node_list[0].url
            title = '苏尔情报 -' + articles['title'].split('-')[1]
            return [fig_url, title]


async def get_osiris_report():
    articles_generator = user.get_articles_g(uid=514771)
    for articles in articles_generator:
        if '试炼周报' in articles['title']:
            cv = articles['id']
            fig_url = article.get_content(cid=cv).paragraphs[7].node_list[0].url
            title = '试炼周报 -' + articles['title'].split('-')[1]
            return [fig_url, title]
