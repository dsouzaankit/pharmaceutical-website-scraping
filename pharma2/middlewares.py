import random
from scrapy import signals
from scrapy.conf import settings
from stem import Signal
from stem.control import Controller
#from time import sleep


def _set_new_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='tor_password')
        controller.signal(Signal.NEWNYM)


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua = random.choice(settings.get('USER_AGENT_LIST'))
        if ua:
            request.headers.setdefault('User-Agent', ua)


class RandomProxy(object):
    # overwrite process request
    def process_request(self, request, spider):
        # Set location of proxy
        p = random.choice(settings.get('PROXY_LIST'))
        if p:
            request.meta['proxy'] = p


class SleepRetryMiddleware(object):
    no_of_requests = 0
    proxy_index = 0

    # overwrite process request
    def process_request(self, request, spider):

        # print(request.url)
        if 'checkspammer' in request.url:
            # bypass captcha by supplying required form data in a POST request
            orig_url = request.url.split('fromurl=')[1]
            request = request.replace(url=orig_url)
            request.dont_filter = True
            print("Anti-bot redirection!!")
            self.proxy_index += 1
            if self.proxy_index % len(settings.get('PROXY_LIST')) == 0:
                self.proxy_index = 0
            return request

        if 'dr_fail' in request.url:
            # bypass IP blocked message by changing proxy
            orig_url = request.meta.get('redirect_urls', [request.url])[0]
            print("IP limit reached!! Changing IP")
            # _set_new_ip()
            request = request.replace(url=orig_url)
            request.dont_filter = True
            self.proxy_index += 1
            if self.proxy_index % len(settings.get('PROXY_LIST')) == 0:
                self.proxy_index = 0
                #     print("IPs exhausted!! Pause for some time")
                #     sleep(301)
        return request

        # print('Proxy# ' + str(self.proxy_index % len(settings.get('PROXY_LIST'))))
        # Set a proxy from list
        request.meta['proxy'] = settings.get('PROXY_LIST')[self.proxy_index % len(settings.get('PROXY_LIST'))]

        # send via privoxy
        # request.meta['proxy'] = 'http://127.0.0.1:8118'	

    # overwrite process response
    def process_response(self, request, response, spider):

        #	abc = spider.crawler.stats 
        self.no_of_requests += 1
        print("Response# " + str(self.no_of_requests))

        return response
