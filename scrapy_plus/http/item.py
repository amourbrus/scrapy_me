#coding:utf-8


class Item(object):
    '''
        框架自定义的item数据类，用户可以通过这个类构建Item对象 item
    '''
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        """
            提供对外访问的接口，但是不允许修改
        """
        return self._data


