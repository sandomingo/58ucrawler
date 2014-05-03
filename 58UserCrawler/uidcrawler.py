# encoding=utf-8
import urllib
import Queue
import re
import threading
import time
import dbutil



class UidCrawler(threading.Thread):
    """58同城技能交换搜索页面用户uid抓取类"""

    def __init__(self, seeds, interval=1000):
        threading.Thread.__init__(self)
        self.interval = interval / 1000.0  # fetch interval in second
        self.seeds = seeds
        self.fetching = Queue.Queue(maxsize=10)
        self.xpaths = tc_xpaths
        self.default_encoding = 'utf-8'
        self.fetched_num = 0

    def fetch(self, url, proxies=None):
        """抓取指定url的html页面"""
        resp = urllib.urlopen(url, proxies=proxies)
        # TODO(SanDomingo) try to guess encoding by reading meta info in its head
        encoding = self.default_encoding
        html = resp.read().decode(encoding)
        return html

    def extract(self, url, html):
        """根据xpath从DOM树中抽取出感兴趣的内容"""
        # extract person's url
        result = {}
        # extract city from url
        city = re.search(r'city_py=\w+', url).group(0)
        if len(city) > 8:
            city = city[8:]
        result['city'] = city
        # from lxml import etree
        import lxml.html.soupparser as soupparser
        dom = soupparser.fromstring(html)
        for name, xpath in self.xpaths.items():
            result[name] = []
            r = dom.xpath(xpath)
            for item in r:
                try:
                    uid = re.search(r'\d+', item.strip()).group(0)
                    result[name].append(uid)
                    self.fetched_num += 1
                except Exception, e:
                    # print 'Error occurs: =>', url, ' ==> ', item
                    pass # always item = '/user/'

        # extract next page url
        next_url = self.gen_next_url(url, html)
        if len(next_url) > 0:
            self.fetching.put(next_url)
        else:
            print "Finish fetching.", "Total:(uid) ", self.fetched_num
        return result

    def save2db(self, result):
        """将结果存储到指定位置
         TODO(SanDomingo) 存到sqlite或者其他位置"""
        dbutil.insert_uids(result['uids'], result['city'])
        # print "fetched", len(result['uids'])

    def show_result(self, result):
        """桩方法，简单的输出结果"""
        for name, values in result.items():
            print name
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str):
                        value = value.encode('utf-8')
                    print value
            else:
                if isinstance(values, str):
                    values = values.encode('utf-8')
                print values

    def crawl_one(self, url, proxies=None):
        """爬取一个页面，包括fetch，extract，save三个过程"""
        html = self.fetch(url, proxies=proxies)
        result = self.extract(url, html)
        self.save2db(result)

    def run(self):
        """启动爬虫"""
        while True:
            if self.fetching.empty(): # inject a seed is possible
                try:
                    seed = self.seeds.get_nowait()
                    self.fetching.put(seed)
                    print "uid crawler started. Init with seed: ", seed
                except Exception:
                    print "No seed available"
                    exit(0)

            fetching_url = self.fetching.get()
            self.crawl_one(fetching_url)
            print "===> Fetched uid num: ", self.fetched_num
            # crawl interval: default is one second
            time.sleep(self.interval)

    def gen_next_url(self, url, html):
        """从response中解析js，并结合现有的url拼出下一页的url"""
        next_url = ""
        try:
            pattern_str = r'/skills/search\?down=t&time=\d+'
            pattern_time = r'time=\d+'
            url_str = re.search(pattern_str, html).group(0)
            next_time = re.search(pattern_time, url_str).group(0)
            current_time = re.search(pattern_time, url).group(0)
            next_url = url.replace(current_time, next_time)
        except AttributeError: # should only occur while there in no next page
            print "No next url not found. ==> ", url
        return next_url


tc_xpaths = {'uids': "//dd[@class='title']//a/@href"}
