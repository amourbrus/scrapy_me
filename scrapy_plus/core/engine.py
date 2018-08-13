#coding:utf-8

from datetime import datetime


from spider import Spider
from scheduler import Scheduler
from downloader import Downloader
from pipeline import Pipeline

from ..http.item import Item
from ..http.request import Request

from ..middleware.downloader_middleware import DownloaderMiddleware
from ..middleware.spider_middleware import SpiderMiddleware

from ..utils.log import logger

from ..conf.default_settings import *

class Engine(object):
    #def __init__(self, spiders={}, pipelines=[], spider_mids=[], downloader_mids=[]):
    def __init__(self):
        # 爬虫对象（自定义的Spider对象）
        #self.spiders = spiders
        self.spiders = self._auto_import_module(SPIDERS, spider=True)

        # 调度器对象
        self.scheduler = Scheduler()
        # 下载器对象
        self.downloader = Downloader()
        # 管道对象
        #self.pipelines = pipelines
        self.pipelines = self._auto_import_module(PIPELINES)

        # 爬虫中间件对象
        #self.spider_mids = spider_mids
        self.spider_mids = self._auto_import_module(SPIDER_MIDDLEWARES)
        # 下载中间件对象
        #self.downloader_mids = downloader_mids
        self.downloader_mids = self._auto_import_module(DOWNLOADER_MIDDLEWARES)


    def _auto_import_module(self, module_list, spider=False):
        """
            module_list：是不同模块对应的列表
            spider： 表示处理的模块列表是否是爬虫 -
                1. 如果是爬虫进行动态模块导入，那么就创建字典保存所有的对象{spider.naem : spider_obj}
                2. 如果不是爬虫，就创建列表保存 [pi1, p2, p3]
            return 返回值当前模块所有类的实例化对象（Spider返回字典，其他返回列表）
        """
        # 如果是爬虫，构建instance为字典；如果不是爬虫，构建instance为列表
        if spider:
            instance = {}
        else:
            instance = []

        # Python内置的处理模块导入的工具
        import importlib

        # 迭代当前模块列表中的所有字符串
        for module in module_list:
            # 获取模块名 字符串
            path_name = module[:module.rfind(".")]
            # 获取类名 字符串
            class_name = module[module.rfind(".")+1:]

            # 通过模块名字符串，获取该模块的绝对路径
            path = importlib.import_module(path_name)
            # 再通过该模块的绝对路径，获取该模块中指定的类对象
            cls = getattr(path, class_name)

            if spider:
                # 通过类对象，获取该类的实例化对象
                instance[cls.name] = cls()
            else:
                instance.append(cls())

        return instance


    def start(self):
        start = datetime.now()
        logger.info("Start time : {}".format(start))

        self._start_engine()

        end = datetime.now()
        logger.info("End time : {}".format(end))

        logger.info("Using time: {}".format( (end - start).total_seconds() ))


    def _start_engine(self):
        #1. 调用spider对象的start_requests()方法，获取第一批入口请求
        #start_request = self.spider.start_requests()
        #for spider in self.spiders:

        # spiders是一个字典，迭代后获取字典的key和value，对应爬虫名和爬虫对象
        for spider_name, spider in self.spiders.items():
            # 迭代start_reqeusts()方法，获取每一个请求对象
            for start_request in spider.start_requests():
                # 通过爬虫名，标记该请求的所属爬虫
                start_request.spider = spider.name
                for spider_mid in self.spider_mids:
                    # 1.1 请求通过爬虫中间件做预处理
                    start_request = spider_mid.process_request(start_request)
                #2. 将第一批通过爬虫中间件处理好的入口请求，交给调度器处理并保存
                self.scheduler.add_request(start_request)


        # 循环获取调度器中的请求，并处理
        while True:
            #3. 将调度器中处理好的请求取出
            request = self.scheduler.get_request()
            if request is None:
                break

            # 4.1 请求发送之前，通过下载中间件做预处理
            for downloader_mid in self.downloader_mids:
                request = downloader_mid.process_request(request)
            # 4.将请求交给下载器的send_request()发送请求，返回响应
            response = self.downloader.send_request(request)
            for downloader_mid in self.downloader_mids:
                # 4.2 下载器返回响应交给parse解析之前，经过下载中间件做预处理
                response = downloader_mid.process_response(response)

            # 获取请求对应的爬虫名
            spider_name = request.spider
            # 通过爬虫名，获取该爬虫名对应的爬虫对象
            spider = self.spiders[spider_name]
            # 再通过爬虫对象获取该请求对应的回调函数
            parse_func = getattr(spider, request.callback)
            # 再将这个请求对应的response响应，传给这个callback
            for results in parse_func(response):
            #for results in self.spider.parse(response):
                # 6. 判断解析结果：
                # 如果是请求对象，则交给调度器处理
                if isinstance(results, Request):
                    for spider_mid in self.spider_mids:
                        # 6.1 请求通过爬虫中间件做预处理
                        results = spider_mid.process_request(results)
                    # 将爬虫名继续传递下去，后续请求也可以通过爬虫名获取到爬虫对象
                    results.spider = spider_name
                    self.scheduler.add_request(results)
                # 如果是Item对象，交给管道的process_item()方法处理

                elif isinstance(results, Item):
                    # 6.2 item交给每一个爬虫中间件做预处理
                    for spider_mid in self.spider_mids:
                        # 6.1 请求通过爬虫中间件做预处理
                        results = spider_mid.process_item(results)
                    # 再将item交给每一个管道做处理
                    for pipeline in self.pipelines:
                        results = pipeline.process_item(results, spider)
                # 如果既不是请求也不是item，就抛出异常报错
                else:
                    raise Exception("Not Support data type : <{}>".format(type(results)))



