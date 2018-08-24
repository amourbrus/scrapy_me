目录结构：

- scrapy_plus
    - core
        - engine.py
        - spider.py
        - scheduler.py
        - downloader.py
        - pipeline.py

    - http
        - reqeust.py
        - response.py
        - item.py

    - middleware
        - spider_middleware
        - downloader_middleware


三大数据对象的属性
```python
# request.py
class Request(object):
    def __init__(self, url, method='GET', headers=None, params=None, data=None):
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params
        self.data = data

# response.py
class Response(object):
    def __init__(self,url,status_code,headers,body):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.encoding = encoding

# item.py
class Item(object):
    def __init__(self, data):
        self._data = data        

    @property
    def data(self):
        return self._data   # 提供对外访问的接口，但是不允许修改

```
*数据允许访问，但不允许修改, @property，方法变为属性*
*注释的不同三个引号的可以在导入时候显示提示信息*
demo：
import a
help(a.fun_xxx)


# 程序入口  --- spider urls
5个组件
scheduler.py
- 2，3兼容
- 使用队列  --- 队列是线程安全的，get(False) 可以使它取不到数据时不阻塞,加一个异常捕获
downloader.py
- response.url  .headers  
- response.encoding demo
```python
response = requests.get("xxxxxxxxxx")
response.encoding  # ‘ISO-8859-1’,可以使用下面两种方法

html = response.content
response.encoding = 'utf-8'
response.text   # 此时会按指定的utf-8编码

# 使用chardet  判断字符串编码 返回字典
import chardet
chardet.detect(html)
[out] {'confidence':0.99, 'encoding':'utf-8', 'language':''}
chardet.detect(html)['encoding']
[out]'utf-8'

```
```python
# spider.py
class Spider(object):
    start_url = "http://www.baidu.com/"

# Scheduler.py
# 调度器封装两个对外接口，一个内部接口
# try:
#     from queue import Queue
# except ImportError:
#     from Queue import Queue
from six.moves.queue import Queue
class scheduler(object):
    def __init__(self):
      # 构建保存请求对象的请求队列
        self.queue = Queue()
        self.filter_set = set()

    def add_request(self):
      # 先对请求进行去重，如果不重复则放入请求队列
        if self._filter_request(request):
            # 如果请求通过了指纹判重，将请求添加到队列中，同时也记录请求指纹---这里的指纹比较简单，只是请求的url,后期改进sha1
            self.queue.put(request)
            self.filter_set.add(request.url)

    def get_request(self):
      # FIFO
        try:
            return self.queue.get()
        except Exception as e:
            return None

    def _filter_request(self, request):
        if request.url in self.filter_set:
            return False
        else:
            return True
# downloader.py
# 发送请求，返回响应
import requests

class Downloader(object):
    def __init__(self, request):
        if request.method.upper() ==  'GET':
            response = request.get(
                url = request.url,
                headers = request.headers,
                params = request.params,
                proxies = request.proxy                
            )
        elif request.method.upper() ==  'POST':
            response = request.post(
                url = request.url,
                headers = request.headers,
                params = request.params,
                proxies = request.proxy,
                data = request.data                 
            )
        else:
            raise Exception('not support this method--{}'.format(request.method))

        return Response(
            url = response.url,
            status_code = response.status_code,
            headers = response.headers,
            body = response.body,
            encoding = chardet.detect(response.content)['encoding']
        )
```
*返回 spider.py*
```python
# spider.py
from ..http.request import Request
from ..http.item import Item

class Spider(object):

    start_url = "http://www.baidu.com/"

    def start_requests(self):
        return Request(self.start_url)

    def parse(self, response):
        data = {}
        data['url'] = response.url
        data['content'] = response.len(body)
        item = Item(data)
        return item
        # Item(response.body)

# pipeline.py
class Pipeline(object):
    def process_item(self, item):
        print(item.data)

```
*主要模块，引擎*
调用其他模块的方法，需要有其他类的类属性，都导入
```python
# engine.py
from spider import Spider
from scheduler import Scheduler
from downloader import Downloader
from pipeline import Pipeline

class Engine(object):
    def __init__(self):
        self.spider = Spider()
        self.scheduler = Scheduler()
        self.downloader = Downloader()
        self.piepline = Pipeline()

    def start(self):   # 封装一个外部接口
        self._start_engine()  

    def _start_engine(self):
        start_request = self.spider.start_requests()
        self.scheduler.add_request(start_request)
        while True:

            request = self.scheduler.get_request()
            if request is None:
                break
            response = self.downloader.send_request()
            results = self.spider.parse(response)

            if ininstance(results, Request):
                self.scheduler.add_request(results)
            elif isinstance(results, Item):
                self.pepeline.process_item(results)
            else:
                raise Exception('not support method')

```
# 安装代码  ---- 利用setup.py
- 代码见github scrapy_me
- 设置requirements.py
- pip freeze  \ list  > xxx.txt
- 版本文件 ---  VERSION.txt
```python
# 执行代码
from scrapy_plus.core.engine import

def main():
    engin = Engine()
    engine.start()

if __name__ == '__main__':
    main()

```

# 2个中间件
```python
# spider_middleware.property
class SpiderMiddleware(object):
    def process_request(self,request):
        print('SpiderMiddleware process_request:<{}>'.format(request.url))
        return request
    def process_item(self,item):
        print('SpiderMiddleware process_item: <{}>'.format(type(request.data)))
        return item

# downloader_middleware.py
class DownloaderMiddleware(object):
    def process_request(self,request):
        print('DownloaderMiddleware process_request:<{}>'.format(request.url))
        return request
    def process_response(self,item):
        print('DownloaderMiddleware process_response: <{}>'.format(response.url))
        return response
```

*engin中导入这两个类*

```python
# engine.py
from ..middleware.downloader_middleware import DownloaderMiddleware
from ..middleware.spider_middleware import SpiderMiddleware

# __init__中添加
self.spider_mid = SpiderMiddleware()
self.downloader_middleware = DownloaderMiddleware()
......
def _start_engine(self):
    start_request = self.spider.start_requests()
    # 请求通过中间件做预处理
    start_request = self.spider_mid.process_request(start_request)
    self.scheduler.add_request(start_request)
    while True:

        request = self.scheduler.get_request()
        if request is None:
            break
        # 请求发送之前
        request = self.downloader_middleware.process_request(request)
        response = self.downloader.send_request()
        # 下载返回数据前中间件
        response = self.downloader_middleware.process_response()
        results = self.spider.parse(response)

        if ininstance(results, Request):
            # 请求通过中间件做预处理
            results = self.spider_mid.process_request(results)
            self.scheduler.add_request(results)
        elif isinstance(results, Item):
            # item
            results = self.spider_mid.process_item(results)
            self.pepeline.process_item(results)
        else:
            raise Exception('not support method')
```

# 日志
模块代码 可以复用
- utils
  - log.py
- 单例模式
- 时间 total_seconds 计算两个时间, 5 level
代码见github
```python
# engine.py
......
def start(self):   # 封装一个外部接口
    start = datetime.now()
    logger.info('Start time : {}'.format(start))

    self._start_engine()
    end = datetime.now()
    logger.info('Ending time: {}'.format(end))
    logger.info('Using time: {}'.format((end - start).total_seconds()))

```

# 默认设置  --- settings文件
- 为了方便用户配置，这是必须的
- 变量覆盖的原理--原来变量赋值在这种作用
```python
# utils.log.py 拿出这些变量，然后 from ..conf.default_settings import *
import logging

# 默认的配置
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d]%(levelname)s:%(mesage)s'
DEFAULT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_FILENAME = 'log.log'  # 默认日志文件名称
# 读取的是用户目录下的settings文件，如果文件中有重名的变量，则覆盖之前的，所以这句代码要在最后
from settings import *  
# 用户目录下添加settings.py
# DEFAULT_LOG_FILENAME = 'baidu.log'
# DEFAULT_LOG_FILENAME = 'baidu.log'

```
