# -*- coding: utf-8 -*-
"""
@Author : py时长两年半
@Time : 2023/4/13 9:37
@Software : pycharm
@File : 线程池+协程.py
@software : pycharm
@CSDN : https://blog.csdn.net/ikun_py
"""
import ssl

import aiohttp
import asyncio
import random
import time
from redis_db import RedisDB
from scrapy import Selector
import headers_pool

ORIGIN_CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES'
)

class SSLFactory:
    def __init__(self):
        self.ciphers = ORIGIN_CIPHERS.split(':')

    def __call__(self) -> ssl.SSLContext:
        random.shuffle(self.ciphers)
        ciphers = ':'.join(self.ciphers)
        ciphers = ciphers + ':!aNULL:!eNULL:!MD5'
        context = ssl.create_default_context()
        context.set_ciphers(ciphers)
        return context

class Spider:

    sem = asyncio.Semaphore(10)

    start_url = [
        "https://www.wayfair.com/costway-cswy4209.html",
        "https://www.wayfair.com/costway-cswy4785.html",
        "https://www.wayfair.com/storage-organization/pdp/costway-w002621268.html",
        "https://www.wayfair.com/costway-cswy3767.html",
        "https://www.wayfair.com/costway-cswy4276.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4209.html",
        "https://www.wayfair.com/costway-cswy4785.html",
        "https://www.wayfair.com/storage-organization/pdp/costway-w002621268.html",
        "https://www.wayfair.com/costway-cswy3767.html",
        "https://www.wayfair.com/costway-cswy4276.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html", "https://www.wayfair.com/costway-cswy4209.html",
        "https://www.wayfair.com/costway-cswy4785.html",
        "https://www.wayfair.com/storage-organization/pdp/costway-w002621268.html",
        "https://www.wayfair.com/costway-cswy3767.html",
        "https://www.wayfair.com/costway-cswy4276.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4209.html",
        "https://www.wayfair.com/costway-cswy4785.html",
        "https://www.wayfair.com/storage-organization/pdp/costway-w002621268.html",
        "https://www.wayfair.com/costway-cswy3767.html",
        "https://www.wayfair.com/costway-cswy4276.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4209.html",
        "https://www.wayfair.com/costway-cswy4785.html",
        "https://www.wayfair.com/storage-organization/pdp/costway-w002621268.html",
        "https://www.wayfair.com/costway-cswy3767.html",
        "https://www.wayfair.com/costway-cswy4276.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4209.html",
        "https://www.wayfair.com/costway-cswy4785.html",
        "https://www.wayfair.com/storage-organization/pdp/costway-w002621268.html",
        "https://www.wayfair.com/costway-cswy3767.html",
        "https://www.wayfair.com/costway-cswy4276.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",
        "https://www.wayfair.com/costway-cswy4533.html",
        "https://www.wayfair.com/costway-cswy3615.html",

    ]
    queue = asyncio.Queue()

    async def strat_requests(self):
        async with aiohttp.ClientSession() as Session:
            [self.queue.put_nowait(url) for url in self.start_url]

            workers = [asyncio.create_task(self.engine(Session)) for _ in range(8)]

            await self.queue.join()

            [w.cancel() for w in workers]


    async def engine(self,Session):
        while 1:
            url = await self.queue.get()
            await self.fetch(Session, url)
            self.queue.task_done()

    async def fetch(self,Session,url):
        async with self.sem:
            proxy = RedisDB.from_settings().get_proxy()
            print(proxy)
            try:
                async with Session.get(
                    url=url,
                    headers=headers_pool.HEADERS_EDGE,
                    timeout=aiohttp.ClientTimeout(20),
                    proxy=proxy,
                    ssl=SSLFactory()(),
                )as res:
                    if res.status == 200:
                        resp = await res.text()
                        # print(time.time())
                        self.parse(resp)

            except Exception as e:
                print(e)

    def parse(self, response):
        item = {}
        res_html = Selector(text=response)
        # 自定义解析
        item['Star'] = res_html.xpath(
            '//div[@data-enzyme-id="PdpLayout-infoBlock"]//span[@class="ProductRatingNumberWithCount-rating"]/text()').extract()
        item['ReviewsCount'] = res_html.xpath(
            '//div[@data-enzyme-id="PdpLayout-infoBlock"]//span[@class="ProductRatingNumberWithCount-count ProductRatingNumberWithCount-count--link"]/text()').extract()
        item['PriceNow'] = res_html.xpath('//meta[@property="product:price:amount"]/@content').extract()
        item['OriginalPrice'] = res_html.xpath('.').re_first('"listPrice":([0-9,.]+),"')
        item['UpdateTime'] = time.strftime('%Y-%m-%d %H:%M:%S')

        print(item)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    s = Spider()
    loop.run_until_complete(s.strat_requests())




