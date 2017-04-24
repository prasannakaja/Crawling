import base64
import random

from utils import *

class MultipleProxyMiddleware(object):

    def process_request(self, request, spider):

        self.proxy_list = getProxies()
        self.proxy = random.choice(self.proxy_list)

        request.meta['proxy'] = "http://%s" %self.proxy.split('@')[-1]
        if "@" in self.proxy:
            proxy_user_pass = self.proxy.split('@')[0]
            encoded_user_pass = base64.encodestring(proxy_user_pass)
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass


class FailResponseMiddleware(object):
    
    def process_response(self, request, response, spider):
        if response.status!=200:
            proxySuspended(request.meta['proxy']) 
            return request
 
        return response
