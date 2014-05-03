#encoding=utf-8
import Queue
import threading
import time
import urllib
import dbutil


class PageCrawler(threading.Thread):
    """58同城用户个人页面抓取类"""

    def __init__(self):
        threading.Thread.__init__(self)
        self.fetching = Queue.Queue(maxsize=1000)
        self.xpaths = tc_xpaths
        self.default_encoding = 'utf-8'
        self.base_url = 'http://jiaoyou.58.com/user/'
        self.fetched_num = 0

    def fetch(self, uid, proxies=None):
        """抓取指定uid的html页面"""
        url = self.base_url + str(uid)
        resp = urllib.urlopen(url, proxies=proxies)
        # TODO(SanDomingo) try to guess encoding by reading meta info in its head
        encoding = self.default_encoding
        html = resp.read().decode(encoding)
        return html

    def extract(self, uid, html):
        """根据xpath从DOM树中抽取出感兴趣的内容"""
        result = {'uid': uid}
        # from lxml import etree
        import lxml.html.soupparser as soupparser

        dom = soupparser.fromstring(html)
        for name, xpath in self.xpaths.items():
            result[name] = []
            r = dom.xpath(xpath)
            for item in r:
                result[name].append(item.text.strip())
            result[name] = ','.join(result[name])
        self.fetched_num += 1
        return result

    def save2db(self, result):
        """将结果存储到指定位置
        TODO(SanDomingo) 存到sqlite或者其他位置"""
        # prepossess the result
        # extract age (number only)
        # e.g: 年龄：27岁 => 27
        if len(result['age']) > 5:
            result['age'] = result['age'][3:-1]
        else:
            result['age'] = -1  # error format
        # extract gender
        # e.g: 性别：女 => 女
        if len(result['sex']) > 1:
            result['sex'] = result['sex'][-1]
        # extract location
        # e.g: 地区：朝阳常营 => 朝阳常营
        if len(result['location']) > 3:
            result['location'] = result['location'][3:]
        dbutil.update_page_data(result)
        print 'uid: ', result['uid'], 'fetched.'

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

    def crawl_one(self, uid, proxies=None):
        """爬取一个用户的页面，包括fetch，extract，save三个过程"""
        html = self.fetch(uid, proxies=proxies)
        result = self.extract(uid, html)
        self.save2db(result)

    def run(self):
        """启动爬虫"""
        while True:
            fetching_uids = dbutil.get_fetching_uids()
            if len(fetching_uids) == 0: # finish crawling
                return
            for uid in fetching_uids:
                self.crawl_one(uid[0])
                if self.fetched_num % 100 == 0: # simple log
                    print "===> Fetched page num: ", self.fetched_num
                # crawl interval: one second
                time.sleep(1)



tc_xpaths = {'nickname': "//b[@id='nickid']",
             'sex': "(//ul[@class='m_zl']/li/span)[1]",
             'age': "(//ul[@class='m_zl']/li/span)[2]",
             'location': "(//ul[@class='m_zl']/li/span)[4]",
             'skill': "//p[@class='zy_jn_y']/a",
             'want': "//p[@class='zy_jn_n']/a",
             }
