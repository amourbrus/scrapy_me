#coding:utf-8


from ..http.request import Request
from ..http.item import Item

class Spider(object):

    name = None

    #start_url = "http://www.baidu.com/"
    # 默认空列表，需要用户重写这个类属性
    start_urls = []


    def __init__(self):
        if self.name is None:
            raise Exception("Must have a spider name.")

    def start_requests(self):
        # reqeust_list = []
        # for url in self.start_urls:
        #     reqeust_list.append(Request(url))
        # return reqeust_list

        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        raise Exception("Must overwrite this parse func.")

        # from lxml import etree
        # html_obj = etree.HTML(response.body)
        # html_obj.xpath("")

        # text = response.xpath("//title/text()")[0]

        # data = {}
        # data['title'] = text
        # data['url'] = response.url
        # data['content'] = len(response.body)
        # item = Item(data)
        # yield item

        # next_link = response.xpath("//a/@href")[0]
        # yield Request(next_link)

        #return Request(data['url'])

