#coding:utf-8

import gevent.monkey
from gevent.pool import Pool as BasePool
gevent.monkey.patch_all()


class Pool(BasePool):
    def apply_async(self, func, args=None, kwds=None, callback=None):
        return BasePool().apply_async(func=func, args=args, kwds=kwds, callback=callback)

    def close(self):
        pass


