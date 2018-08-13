#coding:utf-8


from scrapy_plus.core.engine import Engine

#from spiders.baidu import BaiduSpider
# from spiders.douban import DoubanSpider

# from pipelines import BaiduPipeline1, BaiduPipeline2, DoubanPipeline1, DoubanPipeline2

# from middlewares import SpiderMiddleware1, SpiderMiddleware2, DownloaderMiddleware1, DownloaderMiddleware2

def main():
    # 通过自定义的BaiduSpider类构建了爬虫对象
    # baidu_spider = BaiduSpider()
    # douban_spider = DoubanSpider()
    #spiders = {"baidu" : baidu_spider, "douban" : douban_spider}
    #spiders = {baidu_spider.name : baidu_spider, douban_spider.name : douban_spider}
    # spiders = {BaiduSpider.name : BaiduSpider(), DoubanSpider.name : DoubanSpider()}

    # 通过自定义的Pipeline类构建了多个管道对象
    # pipelines = [
    #     BaiduPipeline1(),
    #     BaiduPipeline2(),
    #     DoubanPipeline1(),
    #     DoubanPipeline2()
    # ]

    # 通过自定义的middlewares构建了多个爬虫中间件
    # spider_middlewares = [
    #     SpiderMiddleware1(),
    #     SpiderMiddleware2()
    # ]

    # 通过自定义的middlewares构建了多个下载中间件
    # downloader_middlewares = [
    #     DownloaderMiddleware1(),
    #     DownloaderMiddleware2()
    # ]

    # ，把对象传给Engine，再创建框架提供的引擎对象
    # engine = Engine(
    #     spiders=spiders,
    #     pipelines=pipelines,
    #     spider_mids = spider_middlewares,
    #     downloader_mids = downloader_middlewares
    # )

    engine = Engine()
    # 执行start()方法，启动框架执行程序
    engine.start()


    # import settings
    # import importlib

    # spiders = settings.SPIDERS
    # print(spiders)

    # for spider in spiders:
    #     path_name = spider[:spider.rfind(".")]
    #     class_name = spider[spider.rfind(".")+1:]

    #     path = importlib.import_module(path_name)
    #     cls = getattr(path, class_name)
    #     print(cls)
    #     print(cls())


    # import importlib

    # path = importlib.import_module("spiders.baidu")

    # # 实例属性/实例方法 = getattr(对象，"属性名/方法名")

    # # 类对象 = getattr(文件的绝对路径名, "文件中类名")

    # print(getattr(path, "BaiduSpider"))

    # print(BaiduSpider)




if __name__ == "__main__":
    main()


