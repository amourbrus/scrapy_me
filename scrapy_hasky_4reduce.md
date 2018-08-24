### 分布式
支持分布式
1. 主从分离
- 主端处理第一批请求的保存
- 从端处理请求发送，响应的解析，提交新的请求
2. 同一个数据库里存储请求队列、指纹集合，提取Item数据，由多个爬虫端去访问获取请求
保存数据库时的问题：出现存的是字符串不是python的对象，可以使用pickle模块解决该问题
*提供redis 队列的接口,建在 utils内，set接口也放在那，还有一个日志*
在配置文件中设置redis 信息
在调度器中判断角色，master,slave,none / 如果用户使用的是分布式，在redis数据库中存请求队列，取指纹;如果是本地的就使用本地python的
```python
# queue.py
#coding:utf-8

import time
import pickle

import redis
from six.moves import queue as BaseQueue

from ..conf.default_settings import *


# 利用redis实现一个Queue，使其接口同python的内置队列接口一致，可以实现无缝转换
class Queue(object):
    """
    A Queue like message built over redis
    """

    Empty = BaseQueue.Empty
    Full = BaseQueue.Full
    max_timeout = 0.3

    def __init__(self, maxsize=0, name=REDIS_QUEUE_NAME, host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT, db=REDIS_QUEUE_DB,
                lazy_limit=True, password=None):
        """
        Constructor for RedisQueue
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: redis queue is shared via instance, a lazy size limit is used
                    for better performance.
        """
        self.name = name
        self.redis = redis.StrictRedis(host=host, port=port, db=db, password=password)
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0

    def qsize(self):
        self.last_qsize = self.redis.llen(self.name)
        return self.last_qsize

    def empty(self):
        if self.qsize() == 0:
            return True
        else:
            return False

    def full(self):
        if self.maxsize and self.qsize() >= self.maxsize:
            return True
        else:
            return False

    def put_nowait(self, obj):
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        self.last_qsize = self.redis.rpush(self.name, pickle.dumps(obj))
        return True

    def put(self, obj, block=True, timeout=None):
        if not block:
            return self.put_nowait(obj)

        start_time = time.time()
        while True:
            try:
                return self.put_nowait(obj)
            except self.Full:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    def get_nowait(self):
        ret = self.redis.lpop(self.name)
        if ret is None:
            raise self.Empty
        return pickle.loads(ret)

    def get(self, block=True, timeout=None):
        if not block:
            return self.get_nowait()

        start_time = time.time()
        while True:
            try:
                return self.get_nowait()
            except self.Empty:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)
# set.py
#coding:utf-8

import redis

from ..conf.default_settings import *
from .log import logger

class NormalFilterSet(object):
    def __init__(self):
        self.filter_set = set()

    def add(self, fp):
        self.filter_set.add(fp)

    def is_filter(self, request, fp):
        if fp in self.filter_set:
            logger.info("Filter Request : <{}>".format(request.url))
            return False
        else:
            return True


class RedisFilterSet(object):
    def __init__(self):
        self.filter_set = redis.Redis(host=REDIS_SET_HOST, port=REDIS_SET_PORT, db=REDIS_SET_DB)
        self.name = REDIS_SET_NAME

    def add(self, fp):
        self.filter_set.sadd(self.name, fp)

    def is_filter(self, request, fp):
        if self.filter_set.sismember(self.name, fp):
            logger.info("Filter Request : <{}>".format(request.url))
            return False
        else:
            return True

# scheduler.py
# 如果是分布式的角色，那么使用redis数据库的队列
if role == "master" or role == "slave":
    from ..utils.queue import Queue
    from ..utils.set import RedisFilterSet as Set
# 如果是非分布式角色，那么使用python内置的队列
elif role == None:
    from six.moves.queue import Queue
    from ..utils.set import NormalFilterSet as Set
else:
    raise Exception("Not Support role ： {}".format(role))

```

###
爬虫高端技术：
分布式 ： 在不同的硬件环境和网络环境下，共享请求队列和指纹集合。
断点续爬 ： 保持请求队列和指纹集合，程序中断后再次执行，可以继续之前的记录执行
增量抓取 ： url不变，但是页面会变动的场景，定期抓取该页面，获取最新的数据。
1. 定时发送：
    Linux定任务工具：crontab、 while True: time.sleep(300)
2. 请求不能被去重，
3. 页面内容的重复检测：
    根据内容的特征值：url、标题、作者 如果都是相同的，那么就认为是重复的内容，不必保存。
案例：新浪滚动新闻
