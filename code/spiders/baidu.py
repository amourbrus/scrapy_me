#coding:utf-8

from scrapy_plus.core.spider import Spider
from scrapy_plus.http.item import Item


class BaiduSpider(Spider):

    name = "baidu"

    start_url = "http://news.baidu.com"

    start_urls = [
        "http://www.baidu.com",
        "http://news.baidu.com/",
        "http://www.baidu.com/"
    ]

    def parse(self, response):
        data = {}
        data['title'] = response.xpath("//title/text()")[0]
        yield Item(data)
