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
