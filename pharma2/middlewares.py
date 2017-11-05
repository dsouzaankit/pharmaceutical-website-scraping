import scrapy
from scrapy import signals
from scrapy.conf import settings
import random
from time import sleep

class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua  = random.choice(settings.get('USER_AGENT_LIST'))
        if ua:
            request.headers.setdefault('User-Agent', ua)

class CustomMiddleware(object):

    no_of_requests = 0
    proxy_index = 0

    # overwrite process request
    def process_request(self, request, spider):

        #print(request.url)
        if 'checkspammer' in request.url:
            #bypass captcha by supplying required form data in a POST request
            orig_url = request.url.split('fromurl=')[1]
            request = request.replace(url = orig_url)
            print("Anti-bot redirection!!")
            request = scrapy.FormRequest(
                orig_url,
                formdata = {'scode': '657515',
                          'code': '657515',
                          'validated': 'Yes',
                          'fromurl': orig_url},
                meta = {'item': request.meta['item']},
                dont_filter = True)

        if 'dr_fail' in request.url:
            #bypass IP blocked message by changing proxy
            orig_url = request.meta.get('redirect_urls', [request.url])[0]
            print("IP limit reached!! Changing IP")
            request = request.replace(url = orig_url)
            request.dont_filter = True
            self.proxy_index += 1
            if self.proxy_index % len(settings.get('PROXY_LIST')) == 0:
                print("IPs exhausted!! Pause for some time")
                sleep(301)
            return request

        print('Proxy# ' + str(self.proxy_index % len(settings.get('PROXY_LIST'))))
        # Set a proxy from list
        request.meta['proxy'] = settings.get('PROXY_LIST')[self.proxy_index % len(settings.get('PROXY_LIST'))]

    # overwrite process response
    def process_response(self, request, response, spider):

        self.no_of_requests += 1
        print("Response# " + str(self.no_of_requests))

        return response
        
