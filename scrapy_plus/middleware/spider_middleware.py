#coding:utf-8


class SpiderMiddleware(object):
    def process_request(self, request):
        print("SpiderMiddleware process_request :  <{}>".format(request.url))
        return request

    def process_item(self, item):
        print("SpiderMiddleware process_item :  <{}>".format(type(item.data)))
        return item
