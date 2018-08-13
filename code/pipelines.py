#coding:utf-8


class BaiduPipeline1(object):
    def process_item(self, item, spider):
        #if isinstance(spider, BaiduSpider)
        if spider.name == "baidu":
            print("BaiduPipeline1: process_item : {}".format(item.data))

        return item

class BaiduPipeline2(object):
    def process_item(self, item, spider):
        if spider.name == "baidu":
            print("BaiduPipeline2: process_item : {}".format(item.data))
        return item


class DoubanPipeline1(object):
    def process_item(self, item, spider):
        if spider.name == "douban":
            print("DoubanPipeline1: process_item : {}".format(item.data))
        return item

class DoubanPipeline2(object):
    def process_item(self, item, spider):
        if spider.name == "douban":
            print("DoubanPipeline2: process_item : {}".format(item.data))
        return item

