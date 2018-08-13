#coding:utf-8


# 默认的配置
# DEFAULT_LOG_LEVEL = logging.INFO    # 默认等级
# DEFAULT_LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'   # 默认日志格式
# DEFUALT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
DEFAULT_LOG_FILENAME = 'baidu.log'    # 默认日志文件名称

SPIDERS = [
    "spiders.baidu.BaiduSpider",
    #"spiders.douban.DoubanSpider"
]



PIPELINES = [
    "pipelines.BaiduPipeline1",
    #"pipelines.BaiduPipeline2",
    "pipelines.DoubanPipeline1",
    #"pipelines.DoubanPipeline2",
]


# SPIDER_MIDDLEWARES = [
#     "middlewares.SpiderMiddleware1",
#     "middlewares.SpiderMiddleware2",
# ]

# DOWNLOADER_MIDDLEWARES = [
#     "middlewares.DownloaderMiddleware1",
#     "middlewares.DownloaderMiddleware2",
# ]
