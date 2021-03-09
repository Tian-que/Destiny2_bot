import sqlite3
import ujson
import requests, os
from bs4 import BeautifulSoup
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from nonebot import get_driver
from destiny2_bot.utils.JsonIO import *

driver = get_driver()
player_info = {}
BUNGIE_API_URL = 'https://www.bungie.net/Platform/'
BUNGIE_API_KEY = driver.config.bungie_api_key

@driver.on_startup
async def get_member():
    global player_info
    global cors

    # 载入玩家token
    fig_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'player_info.json')
    player_info = await readTo(fig_dir)

    # 连接sqllit本地数据库
    fig_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'zh.sqllit3')
    conn = sqlite3.connect(fig_dir)
    cors = conn.cursor()
    print('载入Destiny2模块成功')

s = 'SELECT json FROM DestinyInventoryItemDefinition WHERE json like "%""name"":""{}""%"'

async def Refresh_Token():
    global player_info
    url = BUNGIE_API_URL + 'app/oauth/token/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-API-KEY': '{}'.format(BUNGIE_API_KEY)}
    data = {
        "grant_type": (None, "refresh_token"),
        "refresh_token": (None, player_info["refresh_token"]),
        "client_id": (None, "35258"),
        "client_secret": (None, "xaRwwLZo5bJECNbAmv0wpCOiJx6Prmd1CwRhEJLtpP8")
    }
    async with aiohttp.ClientSession() as session:
        response = await session.post(url=url, data=data, headers=headers, verify_ssl=False)
        content = await response.json()
    player_info['access_token'] = content['access_token']
    player_info['refresh_token'] = content['refresh_token']

    fig_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'player_info.json')
    await writeTo(fig_dir, player_info)

    return content['access_token']

def Get_DMembershipId_By_Id():
    pass

def Get_CharacterIds_By_DMembershipId():
    pass

# 获取枪酱售卖内容
async def Get_Vendor_Sales():
    url = BUNGIE_API_URL + 'Destiny2/{}/Profile/{}/Character/{}/Vendors/{}/?Components=402'
    url = url.format('3', '4611686018510059315', '2305843009736844756', '672118013')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-API-KEY': '{}'.format(BUNGIE_API_KEY),
        'Authorization': "Bearer " + player_info['access_token']
    }
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url, headers=headers, verify_ssl=False)
            data = await response.json()
    except:
        await Refresh_Token()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-API-KEY': '{}'.format(BUNGIE_API_KEY),
            'Authorization': "Bearer " + player_info['access_token']
        }
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url, headers=headers, verify_ssl=False)
            data = await response.json()
    data = data['Response']['sales']['data']
    mod_list = [data[i]['itemHash'] for i in data if
                data[i]['costs'] != [] and data[i]['costs'][0]['itemHash'] == 4046539562]

    name = []
    for i in mod_list:
        try:
            s = 'SELECT json FROM DestinyInventoryItemDefinition WHERE id = {};'.format(i)
            cursor = cors.execute(s)
            a = cursor.fetchall()
            content = ujson.loads(a[0][0])
        except:
            id = int(i)
            if (id & (1 << (32 - 1))) != 0:
                id = id - (1 << 32)
            s = 'SELECT json FROM DestinyInventoryItemDefinition WHERE id = {};'.format(id)
            cursor = cors.execute(s)
            a = cursor.fetchall()
            content = ujson.loads(a[0][0])

        name.append([content['displayProperties']['icon'], content['displayProperties']['name']])

    return name

# 枪酱拼图
async def info_to_img(name):
    material_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'material')
    img = Image.open(material_dir + '\枪酱模组2.png')
    drawobj = ImageDraw.Draw(img)
    font = ImageFont.truetype(material_dir + '\msyhbd.ttc', 35)

    figName = name[0][0].replace('/', '_')
    img_url = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'mod', figName)

    if img_url[-3:] != 'png':
        im = Image.open(img_url).resize((79, 79))
        img.paste(im, (32, 436))
    else:
        im = Image.open(img_url).resize((79, 79))
        r, g, b, a = im.split()
        img.paste(im, (32, 436), mask=a)

    figName = name[1][0].replace('/', '_')
    img_url = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'mod', figName)
    if img_url[-3:] != 'png':
        im = Image.open(img_url).resize((79, 79))
        img.paste(im, (33, 530))
    else:
        im = Image.open(img_url).resize((79, 79))
        r, g, b, a = im.split()
        img.paste(im, (33, 530), mask=a)

    text = name[0][1]
    drawobj.text([145, 451], text, 'white', font=font)

    text = name[1][1]
    drawobj.text([145, 545], text, 'white', font=font)

    dirs = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'everyday_mod')
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    fig_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'everyday_mod',
                           name[0][1] + '_' + name[1][1] + '.png')
    img.save(fig_dir)

    return 0

async def search_id(name):
    cursor = cors.execute(s.format(name))
    a = cursor.fetchall()
    id = []
    for aa in a:
        d = ujson.loads(aa[0])
        id.append(d['hash'])
    # print(f'id = {id}')
    return id

async def get_perks(name):
    ids= await search_id(name)
    if not len(ids):
        return None

    for id in ids:
        try:
            ret_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'weapon_perk', '{}.png').format(id)
            # print(ret_dir)
            if os.path.exists(ret_dir):
                return ret_dir
            url = 'https://www.light.gg/db/zh-cht/items/{}/'.format(id)
            # print(url)

            async with aiohttp.ClientSession() as session:
                response = await session.get(url, verify_ssl=False)
                content = await response.read()

            # response = requests.get(url, verify_ssl=False)
            # content = response.content

            soup = BeautifulSoup(content, 'lxml', from_encoding='utf-8')
            item_header = soup.find_all('div', class_='item-header')[0]
            special_perks = soup.find_all('div', id='special-perks', class_='clearfix')[0]
            stat_container = soup.find_all('div', id='stat-container', class_='clearfix')[0]
            socket_container = soup.find_all('div', id='socket-container')[0]
            clearfix_perks = socket_container.find_all('div', class_='clearfix perks')[0]
            break
        except:
            continue

# ----------------------item_header部分---------------------------
    icon = item_header.find_all('img')

    # 角标图/url data\destiny2\image\sign
    # icon_up_name = icon[0]['class'][0]
    # icon_up_src = icon[0]['src']

    sign_icon = {
        'figname': icon[0]['src'].split('/')[-1],
        'figurl': icon[0]['src'],
        'figdir': os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image','signs')
    }

    # 武器图/url data\destiny2\image\sign
    # icon_down_name = icon[1]['alt']
    # icon_down_src = icon[1]['src']

    weapon_icon = {
        'figname': '.'.join([icon[1]['alt'], icon[1]['src'].split('.')[-1]]),
        'figurl': icon[1]['src'],
        'figdir': os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'weapons')
    }

    # 武器类型
    weapon_type = item_header.find_all('span', class_='weapon-type')[0].contents[0].strip('\r\n ')

    # 背景叙述
    flavor_text = [i.contents for i in item_header.find_all('h4')][0][0]

    async def make_p1():
        await download_img2(**sign_icon)
        await download_img2(**weapon_icon)

        img = Image.new('RGB', (760, 150), (26, 26, 32))
        drawobj = ImageDraw.Draw(img)
        # font = ImageFont.truetype('msyhbd.ttc', 35)

        im = Image.open(weapon_icon['figdir'] + '\\' + weapon_icon['figname']).resize((96, 96))
        img.paste(im, (20, 20))

        im = Image.open(sign_icon['figdir'] + '\\' + sign_icon['figname']).resize((96, 96))
        l, a = im.split()
        img.paste(im, (20, 20), mask=a)

        fontdir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'material', 'msyhbd.ttc')
        font = ImageFont.truetype(fontdir, 30)
        drawobj.text([130, 15], weapon_icon['figname'].split('.')[0], 'white', font=font)

        font2 = ImageFont.truetype(fontdir, 20)
        drawobj.text([130, 56], weapon_type, 'white', font=font2)

        font3 = ImageFont.truetype(fontdir, 19)
        drawobj.text([130, 90], flavor_text, 'grey', font=font3)

        # img.show()
        return img

    # ----------------------特殊perk-------------------------------------
    txt = special_perks.find_all('img')
    txt2 = special_perks.find_all('div')
    s_perks_1 = {
        "figname": txt[0]['alt'] + '.' + txt[0]['src'].split('.')[-1],
        "figurl": txt[0]['src'],
        'figdir': os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'perks'),
        "txt": txt2[1].contents[0]
    }
    s_perks_2 = {
        "figname": txt[1]['alt'] + '.' + txt[0]['src'].split('.')[-1],
        "figurl": txt[1]['src'],
        'figdir': os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'perks'),
        "txt": txt2[3].contents[0]
    }


    async def make_p2():
        await download_img2(**s_perks_1)
        await download_img2(**s_perks_2)

        img = Image.new('RGB', (760, 150), (26, 26, 32))
        drawobj = ImageDraw.Draw(img)

        im = Image.open(s_perks_1['figdir'] + '\\' + s_perks_1['figname']).resize((52, 52))
        *_, a = im.split()
        img.paste(im, (37, 12), mask=a)

        font = ImageFont.truetype('msyhbd.ttc', 20)
        drawobj.text([120, 12], s_perks_1['figname'].split('.')[0], 'white', font=font)

        font2 = ImageFont.truetype('msyhbd.ttc', 15)
        drawobj.text([120, 40], s_perks_1['txt'], 'white', font=font2)

        im = Image.open(s_perks_2['figdir'] + '\\' + s_perks_2['figname']).resize((52, 52))
        *_, a = im.split()
        img.paste(im, (37, 84), mask=a)

        font = ImageFont.truetype('msyhbd.ttc', 20)
        drawobj.text([120, 84], s_perks_2['figname'].split('.')[0], 'white', font=font)

        font2 = ImageFont.truetype('msyhbd.ttc', 15)
        drawobj.text([120, 112], s_perks_2['txt'], 'white', font=font2)

        # img.show()
        return img


    # -------------------------------------------------------------------
    all_stats = stat_container.find_all('tr')
    stats = {}
    for i in all_stats:
        if len(i) == 7:
            stats[i.contents[1].contents[0].strip('\r\n ')] = i.contents[5].contents[0]
        elif len(i) == 5:
            stats[i.contents[1].contents[0].strip('\r\n ')] = i.contents[3].contents[0]

    async def progressBar(drawObject, x, y, progress):
        drawObject.rectangle((x, y, x + 170, y + 20), fill=(51, 51, 51))
        drawObject.rectangle((x, y, x + 1.7 * int(progress), y + 20), fill=(102, 102, 102))

    async def make_p3():
        img = Image.new('RGB', (760, 250), (26, 26, 32))
        drawobj = ImageDraw.Draw(img)

        font = ImageFont.truetype('msyhbd.ttc', 20)
        drawobj.text([18, 10], '武器参数', (170, 170, 170), font=font)
        drawobj.text([385, 10], '隐藏参数', (170, 170, 170), font=font)

        i = 0
        font = ImageFont.truetype('msyh.ttc', 16)
        for txt, value in stats.items():
            if i <= 4:
                drawobj.text([152 - 16 * len(txt), 53 + 28 * i], txt, (170, 170, 170), font=font)
                await progressBar(drawobj, 162, 53 + 28 * i, value)
                drawobj.text([340, 53 + 28 * i], value, (170, 170, 170), font=font)
                # print(txt,velue, 56 + 28*i)
            elif i <= 6:
                drawobj.text([152 - 16 * len(txt), 53 + 28 * i], txt, (170, 170, 170), font=font)
                drawobj.text([162, 53 + 28 * i], value, (170, 170, 170), font=font)
            elif i <= 10:
                drawobj.text([515 - 16 * len(txt), -143 + 28 * i], txt, (170, 170, 170), font=font)
                await progressBar(drawobj, 525, -143 + 28 * i, value)
                drawobj.text([703, -143 + 28 * i], value, (170, 170, 170), font=font)
            else:
                # drawobj.text([409, -143 + 28 * i], txt, (170, 170, 170), font=font)
                await progressBar(drawobj, 525, -143 + 28 * i, value)
                drawobj.text([703, -143 + 28 * i], value, (170, 170, 170), font=font)

            i += 1

        # img.show()
        return img

    # -------------------------------------------------------------------
    uls = clearfix_perks.find_all('ul', class_='list-unstyled sockets')

    C_ROLL = []
    R_ROLL = []
    for ul in uls:
        try:
            c = ul.li['class']
        except:
            continue
        if ul.li['class'] != ['random', 'clearfix']:
            ul_perks = []
            lis = ul.find_all('li')
            for li in lis:
                data = {
                    'figname': li.div['data-id'] + '.' + li.img['src'].split('.')[-1],
                    'figurl': li.img['src'],
                    'cls': None
                }
                # id = li.div['data-id']
                # src = li.img['src']
                ul_perks.append(data)
                pass
            C_ROLL.append(ul_perks)
        else:
            ul_perks = []
            lis = ul.li.ul.find_all('li')
            for li in lis:
                cls = li['class']
                li = li.find_all('div', class_=['item', 'show-hover'])[0]
                id = li['data-id'] + '.' + li.img['src'].split('.')[-1]
                src = li.img['src']

                data = {
                    'figname': id,
                    'figurl': src,
                    'cls': cls[-1] if len(cls) else None
                }
                ul_perks.append(data)
            R_ROLL.append(ul_perks)

    async def make_p4():
        high = max([len(i) for i in C_ROLL])
        img = Image.new('RGB', (760, 175 + 85*(high-1)), (26, 26, 32))
        # img = Image.open('D:\PYTHON\complex-bot\data\destiny2\image\material\p4_base.png')
        drawobj = ImageDraw.Draw(img)

        font = ImageFont.truetype('msyhbd.ttc', 16)
        drawobj.text([22, 9], 'Perks', (170, 170, 170), font=font)
        drawobj.text([22, 40], '官ROLL', (170, 170, 170), font=font)
        roll_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'perks')

        j = 0
        for rolls in C_ROLL:
            k = 0
            for roll in rolls:
                await download_img2(**roll, figdir=roll_dir)
                im = Image.open(roll_dir + '\\' + roll['figname']).resize((72, 72))
                bright_enhancer = ImageEnhance.Brightness(im)
                im = bright_enhancer.enhance(0.7).convert('LA')
                *_, a = im.split()
                img.paste(im, (26 + j * 85, 91 + k * 85), mask=a)
                k += 1
            j += 1
            pass

        # img.show()
        return img

    async def make_p5():
        if R_ROLL == []:
            img = Image.new('RGB', (760, 1), (26, 26, 32))
            return img
        high = max([len([j for j in i if j['cls'] != 'retired']) for i in R_ROLL])
        img = Image.new('RGB', (760, 120 + 60*(high-1)), (26, 26, 32))
        # img = Image.open('D:\PYTHON\complex-bot\data\destiny2\image\material\p5_base.png')
        drawobj = ImageDraw.Draw(img)

        font = ImageFont.truetype('msyhbd.ttc', 25)
        drawobj.text([30, 15], 'ROLLS', (170, 170, 170), font=font)
        roll_dir = os.path.join(os.getcwd(), 'destiny2_bot', 'data', 'destiny2', 'image', 'perks')

        j = 0
        x = 34
        x_j = 85
        y = 60
        y_j = 60
        pref = {
            'pref': '\\p-icon.png',
            'prefpvp': '\\pvp-icon.png',
            'prefpve': '\\pve-icon.png'
        }
        for rolls in R_ROLL:
            k = 0
            for roll in rolls:
                if roll['cls'] == 'retired':
                    continue
                await download_img2(**roll, figdir=roll_dir)
                im = Image.open(roll_dir + '\\' + roll['figname']).resize((60, 60))
                if roll['cls'] == None:
                    bright_enhancer = ImageEnhance.Brightness(im)
                    im = bright_enhancer.enhance(0.7).convert('LA')
                *_, a = im.split()
                img.paste(im, (x + j * x_j, y + k * y_j), mask=a)

                if roll['cls'] in pref.keys():
                    im = Image.open(roll_dir + pref[roll['cls']]).resize((18, 18))
                    r, g, b, a = im.split()
                    img.paste(im, (x + 52 + j * x_j, y - 1 + k * y_j), mask=a)
                k += 1
                # break
            j += 1
            # break
            pass

        # img.show()
        return img

    async def download_img2(figurl, figdir, figname, **kwargs):
        if not os.path.exists(figdir):
            os.makedirs(figdir)

        fig_dir = figdir + '/' + figname
        if not os.path.exists(fig_dir):
            async with aiohttp.ClientSession() as session:
                response = await session.get(figurl, verify_ssl=False)
                content = await response.read()
            # response = requests.get(figurl)
            # content = response.content
            with open(fig_dir, 'wb') as f:
                f.write(content)
        return 1

    async def merge_img(img):
        h = sum([i.size[1] for i in img])
        data = Image.new('RGB', (760, h), (26, 26, 32))
        h1 = 0
        for im in img:
            data.paste(im, (0, h1))
            h1 += im.size[1]
        # data.show()
        data.save(ret_dir)
        return ret_dir

    im1 = await make_p1()
    im2 = await make_p2()
    im3 = await make_p3()
    im4 = await make_p4()
    im5 = await make_p5()
    img = [im1,im2,im3,im4,im5]
    return await merge_img(img)
