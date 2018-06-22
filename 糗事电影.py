#!/user/bin/env python3
# coding=utf-8

import urllib.request
import re
import json


class Spider:
    def __init__(self):
        self.url = "http://www.qiushibaike.com/8hr/page"
        self.headers = {"User-Agent":"Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/"
                                   "534.50(KHTML,likeGecko)Version/5.1Safari/534.50"}
        self.switch = True
        self.page = 1
        self.info_list = []

    def qiushi_spider(self):
        url = self.url+str(self.page)+"/"
        request = urllib.request.Request(url,headers=self.headers)
        response = urllib.request.urlopen(request)
        html = response.read()
        #print(html)        #输出网页内容
        self.select_info(html)

    def select_info(self,html):
        html = html.decode("utf-8")
        pattern = re.compile('<div\sclass="article block untagged mb15 typs_.*?>([\d\D]*?)<div\sclass="single-clear"></div>', re.S)        #注意单个笑话匹配是正则表达式的确定，必须完全匹配单个笑话的作者，内容，点赞，评论，仅且匹配一次
        site_list = pattern.findall(html)
        print(len(site_list))
        self.select_site_info(site_list)

    def select_site_info(self,site_list):
        for site in site_list:
            #print(site)         #输出匹配出来的单个段子的内容，包括作者，内容，点赞数，评论数
            item = {}
            pattern_name=re.compile('<h2>(.*?)</h2>', re.S)         #使用正则表达式注意匹配的精确性，不可多或者少匹配某项内容
            pattern_url=re.compile('<div\sclass="author clearfix">[\d\D]*?<img src="//(.*?)"\salt=.*?>', re.S)
            pattern_context=re.compile('<div\sclass="content">\s<span>(.*?)</span>', re.S)
            pattern_haoxiao =re.compile('<span\sclass="stats-vote"><i\sclass="number">(.*?)</i>', re.S)
            pattern_comment=re.compile('<span\sclass="stats-comments">[\d\D]*?<i\sclass="number">(.*?)</i>', re.S)
            item["user_name"] = pattern_name.findall(site)[0]
            item["head_image_url"] = pattern_url.findall(site)[0].encode('utf-8')
            item["content"] = pattern_context.findall(site)[0].replace("<br>","")
            item["haoxiao"] = pattern_haoxiao.findall(site)[0]
            item["comment"] = pattern_comment.findall(site)[0]
            self.info_list.append(item)

    def save_json(self,info_list):
        print(type(info_list))
        info_json_string = json.dumps(info_list,cls=MyEncoder,ensure_ascii=False)    #cls=MyEncoder指定使用自定义的编码类进行编码
        f = open(r"F:\Python_file\sipder-180610\files\new1.json","w")
        f.write(info_json_string)
        f.write("\n")
        f.close()

    def start_work(self):
        while self.switch:
            self.qiushi_spider()
            self.save_json(self.info_list)
            choice = input("爬取下一页数据请按Enter，结束请输入quit：")
            if choice == "quit":
                self.switch = False
            else:
                self.page += 1
        print("谢谢使用！")

class MyEncoder(json.JSONEncoder):     #设置自定义的Json.dumps()类的编码类，继承自json.JSONEncode类
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8');     #将bytes转化为字符串，否则编码过程中会报错TypeError: Object of type 'bytes' is not JSON serializable，其他type类型报错是类似此操作
        return json.JSONEncoder.default(self, obj)

if __name__ == "__main__":
    myspider = Spider()
    myspider.start_work()
