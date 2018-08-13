#coding:utf-8

# try:
#     from queue import Queue
# except ImportError:
#     from Queue import Queue

import six
from six.moves.queue import Queue

from ..utils.log import logger

class Scheduler(object):
    def __init__(self):
        # 构建保存请求对象的 请求队列
        self.queue = Queue()
        self.filter_set = set()

    def add_request(self, request):
        # 获取请求指纹
        fp = self._get_fingerprint(request)
        # 先对请求进行去重，如果不重复则放入请求队列
        if self._filter_request(request, fp):
            # 如果请求通过了指纹判重，不仅要将请求添加到队列中，同时也要记录请求指纹
            self.queue.put(request)
            #self.filter_set.add(request.url)
            self.filter_set.add(fp)


    def get_request(self):
        # 从请求队列中取出一个请求：FIFO
        # self.queue.get() # 如果没有数据会导致程序阻塞
        try:
            return self.queue.get(False) # 如果没有数据会抛出异常
        except:
            return None


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

        # 请求的查询字符串
        params = request.params if request.params else {}
        params = self._get_utf8_str(str(sorted(params.items(), key=lambda x : x[0])))
        # 请求的表单数据
        data = request.data if request.data else {}
        data = self._get_utf8_str(str(sorted(data.items(), key=lambda x : x[0])))


        sha1_data = sha1()

        sha1_data.update(url)
        sha1_data.update(method)
        sha1_data.update(params)
        sha1_data.update(data)

        fp = sha1_data.hexdigest()
        #  返回生成的请求指纹
        return fp

    def _get_utf8_str(self, string):
        """
            如果字符串是Unicode，那么就返回utf-8编码
            如果字符串不是Unicode，返回原字符串
        """
        if six.PY2:
            if isinstance(string, unicode):
                return string.encode("utf-8")
            else:
                return string
        else:
            if isinstance(string, str):
                return string.encode("utf-8")
            else:
                return string







