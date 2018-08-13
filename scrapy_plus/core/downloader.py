#coding:utf-8

import requests
import chardet

from ..http.response import Response

class Downloader(object):
    """
        框架按设计的下载器组件，通过requests模块发送请求，构建并返回对应的Response对象
    """
    def send_request(self, request):

        if request.method.upper() == "GET":
            response = requests.get(
                url = request.url,
                headers = request.headers,
                params = request.params,
                proxies = request.proxy
            )

        elif request.method.upper() == "POST":
            response = requests.post(
                url = request.url,
                headers = request.headers,
                params = request.params,
                data = request.data,
                proxies = request.proxy
            )
        else:
            # 如果不支持请求的方法，直接抛出异常，否则正常返回响应
            raise Exception("[ERROR]: Not Support method : <{}>".format(request.method))

        return Response(
            url = response.url,
            status_code = response.status_code,
            headers = response.headers,
            body = response.content,
            encoding = chardet.detect(response.content)['encoding']
        )
