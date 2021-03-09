from nonebot import on_command, permission, on_endswith
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message
from .weekly_report import *
from .data_source import *
from destiny2_bot.utils import download_file

BOT_ID = str(driver.config.bot_id)


weekly_report = on_command("weekly_report", aliases={'周报', '老九', '试炼', }, priority=5)
Vendor_Sales = on_command("Vendor_Sales", aliases={'枪酱', }, priority=5)
Get_access_token = on_command("Get_access_token", aliases={'凭证', }, priority=5, permission=permission.SUPERUSER)
get_perk = on_endswith("perk",priority=5)

@get_perk.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.raw_message.split('perk')[0]
    if not len(msg):
        return
    try:
        fig_dir = await get_perks(msg)
        if fig_dir == None:
            return
        else:
            await get_perk.send(Message('[CQ:image,file=file:///' + fig_dir + ']'))
    except:
        await get_perk.send('出错了')




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
    fig_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'weekly_report', figname)
    if not os.path.exists(fig_dir):
        if not await download_file(figurl, fig_dir):
            await weekly_report.send('失败了')
            return
    await weekly_report.send(Message(f"[CQ:image,file=file:///{fig_dir}]"))

@Vendor_Sales.handle()
async def _(bot: Bot, event: Event, state: T_State):
    names = await Get_Vendor_Sales()

    fig_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'everyday_mod',
                           names[0][1] + '_' + names[1][1] + '.png')

    if not os.path.exists(fig_dir):
        for name in names:
            figName = name[0].replace('/', '_')
            mod_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'mod', figName)
            fig_url = 'https://www.bungie.net/' + name[0]
            if not os.path.exists(mod_dir):
                if not await download_file(url=fig_url,filename=mod_dir):
                    await Vendor_Sales.send('失败了')
                    return
        await info_to_img(names)

    # name:: [icon,name]
    await Vendor_Sales.send(Message('[CQ:image,file=file:///' + fig_dir + ']'))

    async def download_img(names):
        for name in names:
            fig_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'mod', figName)
            if not os.path.exists(fig_dir):
                async with aiohttp.ClientSession() as session:
                    response = await session.get('https://www.bungie.net/' + name[0], verify_ssl=False)
                    content = await response.read()

                with open(fig_dir, 'wb') as f:
                    f.write(content)
        return 1

@Get_access_token.handle()
async def Get_access_token(bot: Bot, event: Event, state: T_State):
    ret = await Refresh_Token()
    await Get_access_token.send(ret)
    pass