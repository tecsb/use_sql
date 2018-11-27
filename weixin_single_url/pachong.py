#!/usr/bin/python
# coding: utf-8
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.touch_actions import TouchActions #add 2019-09-30
from selenium.webdriver.common.keys import Keys

import re
import time
import datetime
# import pdfkit
import os
import sys
import pymongo
import urllib2
import ssl
import multiprocessing
#chrome调试设置

options = webdriver.ChromeOptions()
options.add_argument('user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
mobileEmulation = {'deviceName': 'iPhone 6'}
options.add_experimental_option('mobileEmulation', mobileEmulation)
##############################
client = pymongo.MongoClient('localhost', 27017)
db = client.weixin
conn = db.gzh
debug = False
# 这三行代码是防止在python2上面编码错误的，在python3上面不要要这样设置
reload(sys)
sys.setdefaultencoding('utf-8')

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393")
js2 = 'window.scrollTo(0, document.body.scrollHeight)'

class crawl_wechat:

    def __init__(self, url):

        self.url = url
        self.old_scroll_height = 0
        self.date_begin = '2018年11月1日'

    def getList(self):

        driver = webdriver.PhantomJS(desired_capabilities=dcap)

        driver.get(self.url)

        # for i in range(10):
        #     if(BeautifulSoup(driver.page_source,'html5lib').find('div',class_="more_wrapper \ no_more").get("style")) == 'display:none':
        #     driver.execute_script(js2)

        resp = BeautifulSoup(driver.page_source, 'html5lib')
        msg_list = []
        msg_title=[]
        msg_cover = resp.find_all("div", class_="weui_media_title")

        for href in msg_cover:
            if href.get("hrefs") is not None:
                msg_list.append(href.get("hrefs"))
            else:
                msg_cover_redirect = resp.find_all("a",class_="cover_appmsg_link_box redirect")
                for tmp in msg_cover_redirect:
                    msg_list.append(tmp.get("hrefs"))

        sub_msg = resp.find_all("h4", class_="weui_media_title")

        for sub_href in sub_msg:
            msg_list.append(sub_href.get("hrefs"))
            msg_title.append(sub_href.text)

        print(msg_list)
        print(msg_title)


    def get_list(self):
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.get(self.url)
        # resp = BeautifulSoup(driver.page_source, 'html5lib')
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="nickname"]')))
            # WebDriverWait(driver, 10)
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "js_msg_card")))
            gzh_name= driver.find_element_by_xpath('//*[@id="nickname"]').text
            print gzh_name
        except:
            print "parse gzh error--may not find gzh name"
            driver.quit()
            return
        path = os.path.join(os.getcwd(), 'DOC',gzh_name)
        # u"创建公众号目录"
        if os.path.exists(path):
            print "gzh_dir already exists"
            pass
        else:
            os.makedirs(path)
        print path
        # ls_title = driver.find_elements_by_class_name('weui_media_title')
        # if ls_title:
        #     for line in ls_title:
        #         print line.text,line.get_attribute('hrefs')

        # ls_title = driver.find_elements_by_class_name('weui_media_bd')
        # if ls_title:
        #     for line in ls_title:
        #         print line.find_element_by_partial_link_text()
        #         print line.find_element_by_class_name('weui_media_title').text
        #         print line.find_element_by_class_name('weui_media_title').get_attribute('hrefs')
        #         # print line.find_element_by_class_name('weui_media_desc').text,'\n'
        #         print line.find_element_by_class_name('weui_media_extra_info').text
        resp = BeautifulSoup(driver.page_source, 'html5lib')
        ls_title = resp.find_all(class_ = "weui_media_bd")
        try:
            for i in ls_title:
                try:
                    title = i.find('h4',class_ ='weui_media_title').text.strip()
                    print title
                    url_one = i.find('h4', class_='weui_media_title').get('hrefs')
                    print url_one
                    # save one content

                    desc = i.find('p', class_='weui_media_desc').text
                    date = i.find('p', class_='weui_media_extra_info').text
                    print date,desc
                except:
                    print 'unnormal content parse'
                    continue
                '''文章比较时间'''
                if(time.strptime(date.encode('utf-8').replace('原创',''), '%Y年%m月%d日')<time.strptime(self.date_begin, '%Y年%m月%d日')):
                    print "out of date"
                    break
                title = re.sub(r'[\\\/\:\*\?\"\<\>\|\ \…\n]', '', title)
                file1 = path + r'\\'+ date + title +'.html'
                print file1
                # mongodb-operate
                ls = re.findall(u"\d{4}年\d{1,}月\d{1,}日", date)
                if ls:
                    print ls[0]
                    # print datetime.datetime.strptime(ls[0], u'%Y年%m月%d日')
                    date_iso = datetime.datetime.strptime(ls[0], u'%Y年%m月%d日')
                else:
                    date_iso = datetime.datetime.utcnow()
                item = {'title':date+title,'gzh':gzh_name,'date':date_iso,'desc':desc,'content':''}
                if not conn.find({'title':item['title']}).count():
                    conn.insert(item)
                # mongodb-operate
                self.get_one_page_by_chrome(file1,url_one,date+title)
        # except:
        #         print "parse content error"
        finally:
            driver.quit()
            print "处理完毕"+gzh_name

    def get_one_page(self, file1,url1,index_title):#暂时不用
        if os.path.exists(file1):
            return
        else:
            driver = webdriver.PhantomJS(desired_capabilities=dcap)
            driver.get(url1)
            driver.implicitly_wait(5)
            try:
                f = open(file1,'w')
                f.write(driver.page_source)
                f.close()
                # mongodb-operate
                conn.update({'title':index_title},{'$set':{'content':file1}},upsert=True)
                # mongodb-operate
            except:
                print 'get_one_page error'
            finally:
                driver.close()

    def get_one_page_by_chrome(self, file1, url1, index_title):
        if os.path.exists(file1) and debug ==False:
            return
        else:
            driver = webdriver.Chrome(chrome_options=options)
            # driver = webdriver.PhantomJS(desired_capabilities=dcap)
            driver.get(url1)
            # try:
            len = driver.execute_script('return document.body.scrollHeight')
            # js = 'window.scrollTo(0, document.body.scrollHeight)'
            origin_len = len
            js = 'window.scrollBy(0,500)'  # 单个文章自动阅读，目的是为了加载图片
            while(len>0):
                driver.execute_script(js)
                len2 = driver.execute_script('return document.body.scrollHeight')
                print len2,len,origin_len
                len  = len -500
                len = len+len2-origin_len
                origin_len = len2
                time.sleep(1)

            resp = BeautifulSoup(driver.page_source, 'html5lib')
            page= driver.page_source
            al = resp.find_all('img')
            data_src = u''
            src = u''
            for x in al:
                if x.attrs.has_key('data-src'):
                    data_src =  x['data-src']
                if x.attrs.has_key('src'):
                    # src= x['src']
                    # if data_src.find('mmbiz.qpic.cn')> -1 and  data_src.strip():
                    #     print "replace",data_src,x['src']
                    #     page= page.replace(x['src'],data_src)
                    pass
                if x.attrs.has_key('crossorigin'):
                    page  = page.replace(u"crossorigin=\"anonymous\"", u"")
            # except:
            #     print "get len error"

            try:
                f = open(file1, 'w')

                f.write(page)
                # content = self.download(url1)
                # f.write(content)#下载网页
                f.close()
                # mongodb-operate
                conn.update({'title': index_title}, {'$set': {'content': file1}}, upsert=True)
                # mongodb-operate
            except:
                print 'get_one_page error'
            finally:
                driver.close()

    def download(self, url):
        if url is None:
            return None
        ua_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        context = ssl._create_unverified_context()
        request = urllib2.Request(url, headers=ua_headers)
        content = urllib2.urlopen(request,context=context).read()
        return content
    def process_img(self,str):
        pass
# read fiddle-headers
def read_file(file):
    file_object = open(file)
    try:
        all_the_text = file_object.read()
        # list_of_all_the_lines = file_object.readlines()
    except:
        return None
    finally:
        file_object.close()
    # print all_the_text
    url=  re.findall('GET (.*?) HTTP/1.1',all_the_text)
    url_id= []
    url_unique =[]
    if url:
        for url_one in url:
            ls= re.findall('action=home&__biz=(.*?)==&scene',url_one)
            if ls:
                if ls[0] not in url_id:
                    url_id.append(ls[0])
                    url_unique.append(url_one)
            else:
                pass
    return url_unique
#___old____
#  def parse_gzh(file_):
#     wechat_url = read_file(file_)
#     if wechat_url:
#         for url in wechat_url:
#             print url
#             wechat = crawl_wechat(url)
#             wechat.get_list()

def parse_gzh_by_singleprocess(ls):
    if ls:
        for url in ls:
            print url
            wechat = crawl_wechat(url)
            wechat.get_list()

def parse_gzh(file_):
    wechat_url = read_file(file_)
    if wechat_url:
        a = int(len(wechat_url) / 3)
        b = int(len(wechat_url) / 1.5)
        import multiprocessing
        print a,b
        process1 = multiprocessing.Process(target=parse_gzh_by_singleprocess, args=(wechat_url[:a],))
        process1.start()
        process2 = multiprocessing.Process(target=parse_gzh_by_singleprocess, args=(wechat_url[a:b],))
        process2.start()
        process3 = multiprocessing.Process(target=parse_gzh_by_singleprocess, args=(wechat_url[b:],))
        process3.start()
if __name__ == '__main__' :
    parse_gzh('E:/4_Headers.txt')

    #
    # wechat_url = read_file('E:/6_Headers.txt')
    # if wechat_url:
    #     for url in wechat_url:
    #         print url
    #         wechat = crawl_wechat(url)
    #         wechat.get_list()
    #
    #


