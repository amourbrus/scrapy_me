#coding:utf-8

from lxml import etree
import re
import json

class Response(object):
    '''
        框架自定义的响应类，用户发送请求后，框架会通过这个类构建响应对象交给用户 response对象
    '''
    def __init__(self, url, status_code, headers, body, encoding):
        self.url = url  # 响应的url地址
        self.status_code = status_code  # 响应的状态码
        self.headers = headers  # 响应的报头
        self.body = body    # 响应体
        self.encoding = encoding


    def xpath(self, rule):
        html_obj = etree.HTML(self.body)
        return html_obj.xpath(rule)


    def re_findall(self, rule, string=None):
        """
            正则表达式默认处理响应字符串的解析，
            添加了一个新功能，如果传入第二个参数string，可以解析其他字符串进行解析
        """
        if string is None:
            return re.findall(rule, self.body)
        else:
            return re.findall(rule, string)

    @property
    def json(self):
        """
            可以将json文件的响应解析为对应的Python数据类型并返回
            如果不是json文件则抛出异常
        """
        try:
            return json.loads(self.body)
        except Exception as e:
            #logger.error(e)
            raise e


    #response.re_findall(r"\d+")
    #response.re_findall(r"\d+", "hello1234world")


        # pattern = re.compile(rule)
        # pattern.findall(self.body)

# import json
# html = requests.get().content
# python_obj = json.loads(html)

# python_obj = requests.get().json()

# from jsonpath import jsonpath
# jsonpath(pythob_obj, "$..key")


