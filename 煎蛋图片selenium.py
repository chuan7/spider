
#!user/bin/env python3
# coding=utf-8
# 多线程爬虫示例-爬取网页图片
import time
import urllib.request
from lxml import etree
from selenium import webdriver
phantomjs = r"D:\phantomJS\phantomjs-2.1.1-windows\bin\phantomjs.exe"
driver = webdriver.PhantomJS(phantomjs)
driver.implicitly_wait(9)
n = 1
for i in range(1,2):
    try:
        driver.get("http://jandan.net/ooxx/page-"+str(i)+"#comments")
        print("正在加载第"+str(i)+"页")
        html = driver.page_source
        dom = etree.HTML(html)
        # 返回所有匹配成功后的集合,此处返回的是图片链接的集合
        link_list = dom.xpath('///div/p/img/@src')
        print(link_list)
        for url in link_list:
            path ="F:\\Python_file\\sipder-180610\\files\\images\\" + str(n)+".jpg"
            urllib.request.urlretrieve(url,path) #根据url下载到路径
            n = n+1
            time.sleep(1)
    except:
        pass
