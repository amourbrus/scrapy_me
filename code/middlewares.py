#coding:utf-8


class SpiderMiddleware1(object):
    def process_request(self, request):
        print("SpiderMiddleware1 process_request :  <{}>".format(request.url))
        return request

    def process_item(self, item):
        print("SpiderMiddleware1 process_item :  <{}>".format(type(item.data)))
        return item


class SpiderMiddleware2(object):
    def process_request(self, request):
        print("SpiderMiddleware2 process_request :  <{}>".format(request.url))
        return request

    def process_item(self, item):
        print("SpiderMiddleware2 process_item :  <{}>".format(type(item.data)))
        return item




class DownloaderMiddleware1(object):
    def process_request(self, request):
        print("DownloaderMiddleware1 process_request :  <{}>".format(request.url))
        return request

    def process_response(self, response):
        print("DownloaderMiddleware1 process_response :  <{}>".format(response.url))
        return response


class DownloaderMiddleware2(object):
    def process_request(self, request):
        print("DownloaderMiddleware2 process_request :  <{}>".format(request.url))
        return request

    def process_response(self, response):
        print("DownloaderMiddleware2 process_response :  <{}>".format(response.url))
        return response
