#!user/bin/env python3
# coding=utf-8


import time
import json
import urllib.request
import requests
import urllib.parse
import threading
from queue import Queue
from lxml import etree


class crawl_thread_class(threading.Thread):         #定义爬虫线程类
    def __init__(self,crawl_thread_name,page_Queue,data_Queue):     #爬虫线程的初始化函数
        threading.Thread.__init__(self)             #必须先初始化Thread函数，否则会报错RuntimeError: thread.__init__() not called
        super(crawl_thread_class, self).__init__()
        self.crawl_thread_name = crawl_thread_name
        self.page_Queue = page_Queue
        self.data_Queue = data_Queue
        self.headers = {"User-Agent":"Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/"
                                   "534.50(KHTML,likeGecko)Version/5.1Safari/534.50"}

    def run(self):               #启动爬虫线程的run函数
        print("启动"+self.crawl_thread_name)
        while CRAWL_SWITCH:
            try:
                page = self.page_Queue.get(False)
                url = "http://www.qiushibaike.com/8hr/page/"+str(page)+"/"
                html = requests.get(url,headers=self.headers).text
                #print("这里"+html)
                time.sleep(1)
                self.data_Queue.put(html)
            except:
                pass
        print("结束"+self.crawl_thread_name)


class parse_thread_class(threading.Thread):           #定义解析线程类，继承自threading.Thread类
    def __init__(self,parse_thread_name,data_Queue,f,lock):
        threading.Thread.__init__(self)
        super(parse_thread_class).__init__()
        self.parse_thread_name = parse_thread_name
        self.data_Queue = data_Queue
        self.f = f
        self.lock = lock

    def run(self):               #启动解析线程的run函数
        print("启动"+self.parse_thread_name)
        while PARSE_SWITCH:
            try:
                html = self.data_Queue.get(False)
                #print("还是这里"+html)
                self.parse_data(html)
                time.sleep(10)
            except:
                pass
        print("结束"+self.parse_thread_name)

    def parse_data(self,html):
        print(self.parse_thread_name+"正在处理页面数据")
        html=etree.HTML(html)
        site_list = html.xpath('//div[@class="content-block clearfix"]/div[1]/div')
        #print("site_list的长度为"+str(len(site_list)))
        for site in site_list:
            #print(site)
            item = {}
            item["name"] = site.xpath('.//img[1]/@alt')[0]
            item["url"] = site.xpath('.//img[1]/@src')[0]
            item["content"] = site.xpath('.//div[@class="content"]/span')[0].text
            item["zan"] = site.xpath('.//span[@class="stats-vote"]/i')[0].text
            item["comments"] = site.xpath('.//span[@class="stats-comments"]/a/i')[0].text
            #print(item["name"])
            #print(item["url"])
            #print(item["content"])
            #print(item["zan"])
            #print(item["comments"])
            with self.lock:
                string_a = json.dumps(item,ensure_ascii=False)
                #print("要写入的信息是"+string_a)
                self.f.write(string_a+"\n")


def main():
    global CRAWL_SWITCH
    CRAWL_SWITCH = True
    global PARSE_SWITCH
    PARSE_SWITCH = True

    f = open(r"F:\Python_file\sipder-180610\files\multi_thread.json","w")
    lock = threading.Lock()
    data_Queue = Queue()
    page_Queue = Queue(20)
    for page in range(1,21):
        page_Queue.put(page)

    #设置并生成页面爬取多线程
    crawl_thread_save_list = []
    crawl_thread_name_list = ["页面爬取线程1","页面爬取线程2","页面爬取线程3"]
    for crawl_thread_name in crawl_thread_name_list:
        crawl_thread = crawl_thread_class(crawl_thread_name,page_Queue,data_Queue)
        crawl_thread.start()
        crawl_thread_save_list.append(crawl_thread)

    #设置并生成页面提取多线程
    parse_thread_save_list = []
    parse_thread_name_list = ["页面处理线程1","页面处理线程2","页面处理线程3"]
    for parse_thread_name in parse_thread_name_list:
        parse_thread = parse_thread_class(parse_thread_name,data_Queue,f,lock)
        parse_thread.start()
        parse_thread_save_list.append(parse_thread)

    #设置结束页面爬取线程
    while not page_Queue.empty():
        pass
    print("page_Queue 队列现在为空！")
    CRAWL_SWITCH = False
    for crawl_thread in crawl_thread_save_list:
        crawl_thread.join()
        print("1")

    #设置结束页面处理线程：
    while not data_Queue.empty():
        pass
    print("data_Queue 队列现在为空！")
    PARSE_SWITCH = False
    for parse_thread in parse_thread_save_list:
        parse_thread.join()
        print("2")

    #带锁关闭文件写入并输出友好结束语
    with lock:
        f.close()
    print("谢谢使用！")

if __name__ == "__main__":
    main()