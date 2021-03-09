from bilibili_api import *

request_settings = {
    "use_https": True,
    "proxies": None
}


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
