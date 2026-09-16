import time
import random
from scrapy import signals


class AntiBotMiddleware:
    def __init__(self, settings):
        self.settings = settings
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def process_request(self, request, spider):
        # Add random delay to requests
        delay = random.uniform(1, 3)
        time.sleep(delay)
        
        # Add common headers to look more like a real browser
        request.headers['Accept-Language'] = 'en-US,en;q=0.9'
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Upgrade-Insecure-Requests'] = '1'
        
        # Add referer if not present
        if 'Referer' not in request.headers:
            request.headers['Referer'] = request.url
    
    def process_response(self, request, response, spider):
        # Check for CAPTCHA or bot detection
        if self.detect_bot_protection(response):
            spider.logger.warning(f'Bot protection detected on {request.url}')
            return request
        
        return response
    
    def detect_bot_protection(self, response):
        # Check for common bot detection indicators
        bot_indicators = [
            'captcha',
            'access denied',
            'blocked',
            'unusual traffic',
            'verify you are human',
            'cloudflare'
        ]
        
        response_text = response.text.lower()
        return any(indicator in response_text for indicator in bot_indicators)