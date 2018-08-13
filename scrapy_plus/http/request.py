#coding:utf-8


class Request(object):
    '''
        框架自定义的请求类，用户可以通过这个类构建请求对象 reqeust
    '''
    def __init__(self, url, method="GET", headers=None, params=None, data=None, proxy=None, callback="parse"):
        self.url = url # 请求的url地址
        self.method = method # 请求的方法
        self.headers = headers # 请求的请求报头
        self.params = params # 请求的查询字符串
        self.data = data # 请求的表单数据
        self.proxy = proxy # 请求的代理
        self.callback = callback # 该请求发送后响应的回调函数
