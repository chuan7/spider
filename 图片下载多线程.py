
#!user/bin/env python3
# coding=utf-8
# 多线程爬虫示例-爬取网页图片
import time
from queue import Queue
from lxml import etree
import urllib.request
import threading
from selenium import webdriver


phantomjs = r"D:\phantomJS\phantomjs-2.1.1-windows\bin\phantomjs.exe"
driver = webdriver.PhantomJS(phantomjs)
driver.implicitly_wait(5)

n = 0
class ThreadCrawl(threading.Thread):
    #负责下载页面，提取html
    def __init__(self, threadName, pageQueue, dataQueue,lock):
        threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(ThreadCrawl, self).__init__()
        self.threadName = threadName
        self.pageQueue = pageQueue
        self.dataQueue = dataQueue
        self.lock = lock

    def run(self):
        print(self.threadName + ' begin--------')
        while not CRAWL_EXIT:
            try:
                # 队列为空 产生异常
                with self.lock:
                    page = self.pageQueue.get(block=False)
                    url = "http://jandan.net/ooxx/page-"+str(page)+"#comments"
                    print("正在访问" + url)
                    driver.get(url)
                    html = driver.page_source
                # print("网页源码"+html)
                    self.dataQueue.put(html)
            except:
                break

class ThreadParse(threading.Thread):
    # 负责解析页面  提取图片地址
    def __init__(self, threadName, dataQueue, linkQueue,lock):
        threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(ThreadParse, self).__init__()
        self.threadName = threadName
        self.dataQueue = dataQueue
        self.linkQueue = linkQueue
        self.lock = lock

    def run(self):
        print(self.threadName + ' begin--------')
        while not PARSE_EXIT:
            try:
                html = self.dataQueue.get(block=False)
                self.parsePage(html)
            except:
                pass

    def parsePage(self,html):
        # 解析html文档为html dom模型
        dom = etree.HTML(html)
        #print(dom)
        # 返回所有匹配成功后的集合,此处返回的是图片链接的集合
        with self.lock:
            link_list = dom.xpath('///div/p/img/@src')
        #print(link_list)

        # 提取出页面链接
            for link in link_list:
            #print(link)
                self.linkQueue.put(link)


class ThreadImage(threading.Thread):
    # 负责提取出图片并下载保存
    def __init__(self, threadName, linkQueue, numQueue):
        threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(ThreadImage, self).__init__()
        self.threadName = threadName
        self.linkQueue = linkQueue
        self.numQueue = numQueue

    def run(self):
        print(self.threadName+' begin--------')
        while not IMAGE_EXIT:
            try:
                    link= self.linkQueue.get(block=False)
                    self.loadImage(link)
            except:
                pass

    def loadImage(self, link):
        #print(link)
        try:
            m = self.numQueue.get()
            path = "F:\\Python_file\\sipder-180610\\files\\image\\" + str(m) + ".jpg"
            urllib.request.urlretrieve(link, path)  # 根据link下载到路径
            print('-----loading image-----'+path)
        except:
            pass

CRAWL_EXIT = False
PARSE_EXIT = False
IMAGE_EXIT = False

def main():

    lock = threading.Lock()

    numQueue = Queue()
    for num in range(1, 2000):
        numQueue.put(num,block=True)

    pageQueue = Queue()
    # 放入1 到 20 先进先出
    for i in range(50, 61):
        pageQueue.put(i)

    # 采集结果（每页的html源码）的数据队列
    dataQueue = Queue()
    # 采集到的图片地址
    linkQueue = Queue()

    # 记录线程的列表
    threadCrawl = []
    crawList = ['采集线程1号','采集线程2号','采集线程3号','采集线程4号','采集线程5号']
    for threadName in crawList:
        Cthread = ThreadCrawl(threadName, pageQueue, dataQueue,lock)
        Cthread.start()
        #time.sleep(6)
        threadCrawl.append(Cthread)

    threadParse = []
    parseList = ['解析线程1号','解析线程2号','解析线程3号','解析线程4号','解析线程5号']
    for threadName in parseList:
        Pthread = ThreadParse(threadName, dataQueue, linkQueue,lock)
        Pthread.start()
        #time.sleep(6)
        threadParse.append(Pthread)

    threadImage = []
    imageList = ['下载线程1号', '下载线程2号', '下载线程3号', '下载线程4号','下载线程5号', '下载线程6号' ]
    for threadName in imageList:
        Ithraad = ThreadImage(threadName, linkQueue, numQueue)
        Ithraad.start()
        threadImage.append(Ithraad)


    # 等待pageQueue队列为空，也就是等待之前的操作执行完毕
    while not pageQueue.empty():
        pass
    # 如果pageQueue为空，采集线程退出循环
    global CRAWL_EXIT
    CRAWL_EXIT = True
    print ("pageQueue为空")
    for thread in threadCrawl:
        thread.join()
        print("1")

    while not dataQueue.empty():
        pass
    global PARSE_EXIT
    PARSE_EXIT = True
    print("dataQueue为空")
    for thread in threadParse:
        thread.join()
        print ("2")

    while not linkQueue.empty():
        pass
    global IMAGE_EXIT
    IMAGE_EXIT = True
    print("linkQueue为空")
    for thread in threadImage:
        thread.join()
        print ("3")

    print("谢谢使用！")


if __name__ == '__main__':
    main()


#注意，在定义爬取类及解析类时，因涉及到中间变量，且中间变量为list或者字符串，为多线程不安全性，需要用到线程锁，以免数据出错
#通过定义不同的类线程时在使用线程锁时需要对引用自类外部的线程锁进行说明，定义类的init函数时增加lock对象，并实例化self.lokc=lock,在类内部使用时使用with self.lock:
#同样在实例化类的对象时也应该说明对象的锁