import base64
import random

from utils import *

class MultipleProxyMiddleware(object):
    def __init__(self):
        self.proxy_list = getProxies()
        self.proxy = random.choice(self.proxy_list)
        print self.proxy

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://%s" %self.proxy.split('@')[-1]
        if "@" in self.proxy:
            proxy_user_pass = self.proxy.split('@')[0]
            encoded_user_pass = base64.encodestring(proxy_user_pass)
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
