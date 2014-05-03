#encoding=utf-8
import pagecrawler
import uidcrawler
import dbutil
import Queue
import sys
import time

def crawl_page(crawl_num = 1):
    """启动用户个人页面爬虫"""
    page_crawlers = []
    for i in range(crawl_num):
        page_crawler = pagecrawler.PageCrawler()
        page_crawler.start()
        page_crawlers.append(page_crawler)
        print "page crawler started, id: ", i
    for page_crawler in page_crawlers:
        page_crawler.join()


def gen_seeds(citys, genders):
    """生成种子页面url"""
    url_template = "http://jiaoyou.58.com/skills/search?down=t&time={}&type=1&class1=-1&class2=-1&sex={}&city_py={}"
    seeds = Queue.Queue()
    for city in citys:
        for gender in genders:
            gender = str(gender)
            seed = url_template.format(int(time.time() * 1000), gender, city)
            seeds.put(seed)
    print "Generate seeds number: ", seeds.qsize()

    return seeds


def get_citys():
    citys = []
    fobj = open('city.txt', 'r')
    for line in fobj:
        line = line.strip()
        if len(line) < 1 or line.startswith('#'):
            continue
        citys.append(line)
    return citys



def crawl_uid(crawl_num = 1):
    """启动搜索页面爬虫，抓取用户uid"""
    citys = get_citys()
    gender = [1, 2]  # 1: female, 2: male
    seeds = gen_seeds(citys, gender)
    uid_cralers = []
    for i in range(crawl_num):
        uid_crawler = uidcrawler.UidCrawler(seeds)
        uid_crawler.start()
        uid_cralers.append(uid_crawler)
    for uid_crawler in uid_cralers:
        uid_crawler.join()

def export_data(output_filename):
    """从sqlite数据库中导出数据"""
    dbutil.export(output_filename)


def print_help():
    print "Usage: python app.py setup | crawluid [thread_num]| crawlpage [thread_num] | export <outfile>"


if __name__ == '__main__':
    arg_num = len(sys.argv)
    if arg_num < 2:
        print_help()
        exit(0)
    fun_name = sys.argv[1]
    if fun_name == 'setup':
        dbutil.create_table()
    elif fun_name == 'crawluid':
        crawl_num = 1
        if arg_num == 3:
            crawl_num = int(sys.argv[2])
        crawl_uid(crawl_num)
    elif fun_name == 'crawlpage':
        crawl_num = 1
        if arg_num == 3:
            crawl_num = int(sys.argv[2])
        crawl_page(crawl_num)
    elif arg_num == 3 and fun_name == 'export':
        outfile = sys.argv[2]
        export_data(outfile)
    else:
        print_help()