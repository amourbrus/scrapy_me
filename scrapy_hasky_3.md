### 实现引擎内的动态模块导入
1. 在类，main中的类都是默认的，可以在setting中settings中写一些列表(字典) 引擎会去实例化
2. main函数中的初始化都不需要了--注释掉


import importlib    ----- 给相对路径，返回绝对路径
- 实例属性、实例方法 = getattr(对象，'属性名/方法名')  
- 类对象 = getattr(文件的绝对路径名，'文件中类名')

原来是写在main中的对象，手动传参等，  现在用户在setting写好列表，自动遍历传参，前部分做路径模块名，后部分做类名
动态模块导入获得类,避免用户大量创建对象，大量传参
```python
# demo
# spiders.py
# - baidu.py -- BaiduSpider
import settings
import importlib
path = importlib.import_module("spiders.baidu")
cls = getattr(path, BaiduSpider)
print(cls)
cls()
```

```python
# engine.py
from ..conf.default_settings import *

__init__ 中 ：
对象都自动化导入  self.pipelines = self._auto_import_module(PIPELINES)

def _auto_import_module(self, module_list, spider=False):
    if spider:
        instance ={}
    else:
        instance = []
    import importlib
    for module in module_list:
        path_name = module[:module.rfind(".")]
        class_name = module[module.rfind(".")+1:]

        path = importlib.import_module(path_name)
        cls = getattr(path, class_name)
        if spider:
            instance[cls.name] = cls()   # 字典旧添加键值对
        else:
            instance.append(cls())  # 列表旧追加
    return instance

```
### 使用hashlib 处理请求指纹  --- 调度器,利用sha1 对请求url,method 进行加密制作指纹
- 排序（列表，字典） 对请求进行去重
- sha1 对 unicode 加密
列表排序  -- sort 原数据会被修改 sorted
字典排序  -- 不同顺序去存储，会返回一定的结果虽然不是有序的

list1 = [[],[],[]]
sorted(list1)  默认按第一个值排序
sorted(list1, key=lambda x : x[1])  按第二个值排序
sorted(dict1.items(),key=lambda x : x[0])
sorted(dict1.items(),key=lambda x : x[0], reverse=True)

```python
# scheduler.py
def _filter_request(self, request, fp):
        #如果该请求的url在集合中，表示该请求不需要放入请求队列，返回False表示不同意
        #if request.url in self.filter_set:
        if fp in self.filter_set:
            logger.info("Filter Request : <{}>".format(request.url))
            return False
        else:
            # 如果请求的url地址不在集合中，那么同意让如请求队列，返回True
            return True

def _get_fingerprint(self, request):
    import w3lib.url
    from hashlib import sha1
    # 请求的url地址
    url = self._get_utf8_str(w3lib.url.canonicalize_url(request.url))
    # 请求的方法
    method = self._get_utf8_str(request.method.upper())
    # 请求的查询字符串，归整
    params = request.params if request.params else {}
    params = str(sorted(params.items(), key=lambda x : x[0]))

    data = request.formdata if request.formdata else []
    data = str(sorted(data.items(), key=lambda x : x[0]))

    sha1_data = sha1()
    sha1_data.update(url)
    sha1_data.update(method)
    sha1_data.update(params)
    sha1_data.update(formdata)

    fp = sha1_data.hexdigest()
    return fp

def _get_utf8_str(self,string):
    if six.PY2:
        if isinstance(string, unicode):
            return string.encode('utf-8')
    else:
        if isinstance(string, str):
            return string
```
### 异步方法 --- 多线程和协程
1. 在engine.py 中，start_engine 分为两个部分，一部分开始请求把请求添加到调度器里，没有涉及到网络IO；循环里有网络io，发送请求，异步执行，同步会有网络阻塞
map 批量处理  map(func,list) 同步,  pool.Pool() ,pool.map(func,list) 异步处理
2. 注意点有三
- 在发送请求的地方（网络io）采用异步的方式执行，通过for循环定异步数量。设置callback递归发送。
- 递归停止条件判断：当请求数等于响应数时停止
- while True 防止主线

递归2点   -- 有返回值，有停止条件 ，1000

```python
#coding:utf-8

import time
from datetime import datetime

# 导入线程池类
from multiprocessing.dummy import Pool

from .spider import Spider
from .scheduler import Scheduler
from .downloader import Downloader
from .pipeline import Pipeline

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

        # 创建一个线程池对象
        self.pool = Pool()

        self.total_response = 0

        self.is_running = True

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



# 递归有两个重要必须的特性：
# 1. 必须有返回值
# 2. 必须有停止条件

# Python递归强制退出机制：递归1000次左右，强制停止递归，防止计算机资源被消耗。
# def func()
#     func()


    def _callback(self, _):
        # 当is_running 为True，表示允许一致递归调用自身处理请求
        # 当处理的总请求数和响应数相同，is_running被设置为False，则递归停止
        if self.is_running:
            self.pool.apply_async(self._execute_request_response_item, callback=self._callback)

    def _start_engine(self):
        # 将start_request请求存入调度器
        self._execute_start_request()

        for _ in range(3):
            # 创建一个子线程执行这一部分代码
            self.pool.apply_async(self._execute_request_response_item, callback=self._callback)
        # 从调度器中取出请求，发送请求解析响应（涉及到网络IO)
        #self._execute_request_response_item()

        # 1. 让主线程阻塞在这里，等待所有的子线程任务完成，主线程可以继续执行
        while True:
            # 每次循环等待0.01秒，避免CPU疯狂空转
            time.sleep(0.01)
            # 2.当调度器里的添加的总请求数和引擎解析的总响应数相同时，表示所有请求处理完毕，主线程才可以继续执行
            if self.scheduler.total_request == self.total_response and self.scheduler.total_request != 0:
                # 当if条件满足时，停止callback的递归条用。
                self.is_running = False
                break

        #self.scheduler.queue.empty()
        self.pool.close()
        self.pool.join()

        logger.info("Main thread is over!")

#Linux ： 可以执行的多线程代码，可能在windows上执行结果不一样。

    def _execute_start_request(self):
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


    def _execute_request_response_item(self):
        # 循环获取调度器中的请求，并处理
        #while True:
        #3. 将调度器中处理好的请求取出
        request = self.scheduler.get_request()
        if request is None:
            return

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

        # 每次处理一个响应，总计数器自增1
        self.total_response += 1

```

**协程版**
```python
# coroutine.py
import gevent.monkey
from gevent.pool import Pool as BasePool
gevent.monkey.patch_all()


class Pool(BasePool):
    def apply_async(self, func, args=None, kwds=None, callback=None):
        return BasePool().apply_async(func=func, args=args, kwds=kwds, callback=callback)

    def close(self):
        pass


# engine.py

# 导入线程池类
if ASYNC_TYPE == "thread":
    from multiprocessing.dummy import Pool
elif ASYNC_TYPE == "coroutine":
    #from gevent.pool import Pool
    from ..async.coroutine import Pool
else:
    raise Exception("Not Support async type : {}".format(ASYNC_TYPE))


```
