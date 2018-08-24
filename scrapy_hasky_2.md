导包，
*代码的main --engine ---logger --- settings*
# 使用自定义框架进行发送请求
code
  - spiders
    - __init__.py
    - baidu.py

定义一个爬虫，在引擎发送，继承父类（自定义框架）改写方法\属性
```python
# baidu.py
from scrapy_hasky.core.spider import Spider

class BaiduSpider(Spider):
    name = 'baidu'
    start_url = 'http://www.baidu.com/'
    start_urls = [
    "http://www.baidu.com/",
    "http://news.baidu.com/",
    "http://www.baidu.com/"
    ]

```

修改源码（自定义框架）的engine.py
在main.py中传参
```python
from scrapy_plus.core.engine import
from spiders.baidu import BaiduSpider  # 导入BaiduSpider
def main():
    spider = BaiduSpider()  # 创建自定义的爬虫对象
    engin = Engine(spider)  # 传参
    engine.start()

if __name__ == '__main__':
    main()

```
engine.py
```python
class Engine(object):
    def __init__(self, spider):  # 传参
        # self.spider = Spider()
        self.spider = spider  # 修改
        self.scheduler = Scheduler()
        self.downloader = Downloader()
        self.piepline = Pipeline()
```
## 新增功能：使用多个url地址 --- baidu.py for example
改框架代码 遍历 start_urls, 引擎使用用户spider对象发送请求，再经过爬虫中间件预处理，最后第一批入口请求交给调度器处理并保存
```python
# core.spider.py
class Spider(object):

    # start_url = "http://www.baidu.com/"
    start_urls = []

    def start_requests(self):
        # return Request(self.start_url)  # 需改如下
        # way 1
        # request_list = []
        # for url in self.start_urls:
        #     request_list.append(Request(url))
        # return request_list
        # way 2 better
        for url in self.start_urls:
            yield Request(url)  

    def parse(self, response):
        data = {}
        data['url'] = response.url
        data['content'] = response.len(body)
        item = Item(data)
        return item

```
core.engine.py
```python
......
def _start_engine(self):
    # start_request = self.spider.start_requests()
    for start_request in self.spider.start_requests():
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
        # results = self.spider.parse(response)  # 修改代码如下
        for results in self.spider.parse(response):

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
在调度器中，导入日志
```python
# core.scheduler.py
# 修改如下代码
# def _filter_request(self, request):
#     if request.url in self.filter_set:
#         return False
#     else:
#         return True
from ..utils.log import logger
# 只要有请求，打印 log
def _filter_request(self, request):
    if request.url in self.filter_set:
        logger.info('Filter Request: <{}>'.format(request.url))

```

## 封装定制的返回结果，
- 在response.py 实现一个xpath, 用户拿到response 直接可以 response.xpath
- 正则的两种方式
- 正则方法新增一个功能，除了解析响应的文本，还可以传入其他字符串进行解析
- 封装json

```python
# response.py
class Response(object):
    def __init__(self,url,status_code,headers,body,encoding):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.encoding = encoding
    # add 如下代码
    def xpath(self, rule):
        html_obj = etree.HTML(self.body)
        return html_obj.xapth(rule)

    def re_findall(rule, rule, string=None):
        if string is None:
            return re.findall(rule, self.body)
        else:
            return re.findall(rule, string)

        import re
        re.findall(rule, self.body)

        # 方式二, 规则可以被多次调用，在这里都一样，因为只使用一次
        # pattern = re.compile(rule)
        # pattern.findall(self.body)
    @property   # 不需要传参
    def json(self):
        try:
            return json.loads(self.body)
        except Exception as e:
            raise e

    def bs4(self):
        pass

# core.spider.py
def parse(self, response):
    # text_list = response.xapth("//title/text()")  # 新增
    text = response.xpath('//title/text()')[0]
    data = {}
    data['title'] = text
    data['url'] = response.url
    data['content'] = response.len(body)
    item = Item(data)
    yield item
    # next_link = response.xpath('//a/@href')[0]
    # yield Request(next_link)

```

```python
requests.get().content()
requests.get().text()
requests.get().json()   # 如果数据是json,则返回pathon对象
等价于 --->
import json
python_obj = json.loads(response.body)
python_obj = requests.get().json()

html = requests.get().content
python_obj = json.loads(html)

# demo josnpath
import requests
requests.get('xxx')
import json
from josnpath import jsonpath
requests.get('')

```
### 新增功能：处理不同页面进行解析 --- 多级, 指定一个callback --- douban.py 举例
**douban.py**
code
  - spiders
    - __init__.py
    - baidu.py
    - douban.py
```python
from scrapy_hasky.core.spider import Spider
from scrapy_hasky.http.request import Request
from scrapy_hasky.http.item import Item

class DoubanSpider(Spider):

    name = "douban"

    start_urls = [
        "https://movie.douban.com/top250?start=0",
        "https://movie.douban.com/top250?start=25",
        "https://movie.douban.com/top250?start=50"
    ]
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        node_list = response.xpath("//div[@class='hd']")
        for node in node_list:
            data = {}
            data['title'] = node.xpath('./a/span[1]/text()')[0]
            data['url'] = node.xpath('./a/@href')[0]
            yield Item(data)
            # 在框架 request.py 新增__init__参数 callback='parse'  self.callback=callback
            yield Request(data['url'], callback='parse_page')

    def parse_page(self, response):   # 获取spider对象的response 方法 demo 见下面代码块  
        data = {}
        data['page_url'] = response_url
        yield Item(data)
```
**demo getattr 使用, 获取一个对象的指定属性或方法**
```python

class A(object):
    no = 10
    def parse_page(self, n):
        print(n)
spider = A()
getattr(spider, 'no')    
[out] 10
getattr(spider, 'parse_page')
[out] <bound method A.parse_page of <__main__.A object at 0x113129450>>
parse_page(123)
[out] 123

```
**修改引擎代码如下：**
```python
while True:

    request = self.scheduler.get_request()
    if request is None:
        break
    request = self.downloader_middleware.process_request(request)
    response = self.downloader.send_request()
    response = self.downloader_middleware.process_response()

    parse_func = getattr(self.spider, request.callback)  # 修改增加
    # for results in self.spider.parse(response):  
    for results in parse_func(response):
        if ininstance(results, Request):

            results = self.spider_mid.process_request(results)
            self.scheduler.add_request(results)
        elif isinstance(results, Item):
            # item
            results = self.spider_mid.process_item(results)
            self.pepeline.process_item(results)
        else:
            raise Exception('not support method')

```
```python
# main.py
from scrapy_hasky.core.engine import Engine
from spiders.baidu import BaiduSpider  # 导入BaiduSpider
from spider.douban import DoubanSpider
def main():
    # spider = BaiduSpider()  # 创建自定义的爬虫对象
    spider = DoubanSpider()
    engin = Engine(spider)  # 传参
    engine.start()

if __name__ == '__main__':
    main()

```

### 新增功能：同时跑多个爬虫 -- scrapy 没有
1. 在main.py 创建2个对象 baidu_spider, douban_spider ,传一个列表
2. 引擎遍历处理
3. 判断 spider 来自哪个类

```python
# 用户 main.py
def main():
    baidu_spider = BaiduSpider()  # 创建自定义的爬虫对象
    douban_spider = DoubanSpider()
    # spider_list = ["baidu":baidu_spider, "douban":douban_spider]  # 修改这种方式，在创建爬虫类时添加该name, 暂时还需要传这个字典
    spider_list = {BaiduSpider.name: BaiduSpider(),DoubanSpider.name: DoubanSpider()}
    engin = Engine(spider_list)  # 传参
    engine.start()

if __name__ == '__main__':
    main()
# engine.py
def _start_engine(self):
    for spider_name, spider in self.spider.item():  # change point
        for start_request in spider.start_requests():
            start_request.spider = spider.name
            start_request = self.spider_mid.process_request(start_request)
            self.scheduler.add_request(start_request)

            while True:

                request = self.scheduler.get_request()
                if request is None:
                    break
                request = self.downloader_middleware.process_request(request)
                response = self.downloader.send_request()
                response = self.downloader_middleware.process_response()
                spider = self.spiders[spider_name]  # 新增
                parse_func = getattr(spider, request.callback)
                # for results in self.spider.parse(response):  
                for results in parse_func(response):
                    if isinstance(results, Request):
                        results = self.spider_mid.process_request(results)
                        results.spider = spider_name   # 将爬虫名继续传递下去，后面都可以获得该对象
                        self.scheduler.add_request(results)
                    elif isinstance(results, Item):
                        # item
                        results = self.spider_mid.process_item(results)
                        self.pepeline.process_item(results)
                    else:
                        raise Exception('not support method')

# 框架parse代码：
# core.spider.py
def parse(self, response):
    raise Exception('Must overwrite this parse function')
    # text_list = response.xapth("//title/text()")  # 新增
    # text = response.xpath('//title/text()')[0]
    # data = {}
    # data['title'] = text
    # data['url'] = response.url
    # data['content'] = response.len(body)
    # item = Item(data)
    # yield item
# baidu.py
from scrapy_hasky.http.item import Item
class BaiduSpider(Spider):
    start_url = 'http://www.baidu.com/'
    start_urls = [
    "http://www.baidu.com/",
    "http://news.baidu.com/",
    "http://www.baidu.com/"
    ]
    def parse(self, response):
        data = {}
        data['title'] = response.xpath("//title/text()")[0]
        yield Item(data)
# 用户必须写 name ，写代码如下
# core.spider.py
class Spider(object):
    name = None  # 新增
    start_urls = []
    def __init__(self):  # 新增
        if self.name is None:
            raise Exception("Must have a spider name")

    def start_requests(self):

        for url in self.start_urls:
            yield Request(url)  

    def parse(self, response):
        raise Exception('Must overwrite this parse function')

```
### 自定义管道
code ->pipeline.py
```python
# pipeline.py  代码见github
# main.py
导入创造的管道类，创建对象，pipelines 列表

# engine.py
__init__ 参数增加 pipeline 参数
for results in parse_func(response):
    if isinstance(results, Request):
        results = self.spider_mid.process_request(results)
        results.spider = spider_name   # 将爬虫名继续传递下去，后面都可以获得该对象
        self.scheduler.add_request(results)
    elif isinstance(results, Item):
        results = self.spider_mid.process_item(results)
        for pipeline in self.pipeliens:  # 管道的机制是 第一次的输出是第二次的输入，
            results = pepeline.process_item(results, spider)  # 所以需要接收返回值
    else:
        raise Exception('not support method')

```

### 自定义中间件
1. 在code中创建四个中间件，在main中导入然后创建四个中各中间件对象 代码见github
2. 在引擎__init__增加参数，接收 spider_mids,downloader_mids,并初始化
3. 在main.py中传参给engine
4. 在引擎中 start_engin（） 迭代处理中间件
