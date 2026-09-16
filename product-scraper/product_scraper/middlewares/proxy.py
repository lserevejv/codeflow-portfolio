import random
from scrapy import signals
from scrapy.exceptions import NotConfigured


class ProxyMiddleware:
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        if not self.proxy_list:
            raise NotConfigured('No proxies configured')
    
    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.get('PROXY_LIST', [])
        return cls(proxy_list)
    
    def process_request(self, request, spider):
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = proxy
            spider.logger.debug(f'Using proxy: {proxy}')
    
    def process_exception(self, request, exception, spider):
        if 'proxy' in request.meta:
            spider.logger.warning(f'Proxy failed: {request.meta["proxy"]}')
            if self.proxy_list:
                new_proxy = random.choice(self.proxy_list)
                request.meta['proxy'] = new_proxy
                return request