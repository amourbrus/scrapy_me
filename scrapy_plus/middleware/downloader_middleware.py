#coding:utf-8


class DownloaderMiddleware(object):
    def process_request(self, request):
        print("DownloaderMiddleware process_request :  <{}>".format(request.url))
        return request

    def process_response(self, response):
        print("DownloaderMiddleware process_response :  <{}>".format(response.url))
        return response
