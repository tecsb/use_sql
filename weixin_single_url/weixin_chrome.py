# -- coding: utf-8 --
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
mobileEmulation = {'deviceName': 'Apple iPhone 6'}
options = webdriver.ChromeOptions()
options.add_experimental_option('mobileEmulation', mobileEmulation)
import re
# import pdfkit
import os
import time
import sys
# 这三行代码是防止在python2上面编码错误的，在python3上面不要要这样设置
reload(sys)
sys.setdefaultencoding('utf-8')
import pymongo
client = pymongo.MongoClient('localhost', 27017)
db = client.dianping
conn = db.dianping
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393")


class crawl_dianping:

    def __init__(self, url):

        self.url = url
        self.old_scroll_height = 0

    def get_shop_list(self):
        driver = webdriver.Chrome(chrome_options=options)
        # driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.get(self.url)

        try:
            len = driver.execute_script('return document.body.scrollHeight')
            # js = 'window.scrollTo(0, document.body.scrollHeight)'
            js = 'window.scrollBy(0,1000)'#单个文章自动阅读，目的是为了加载图片
            print len
            for i in range(0,len/1000+1):
                driver.execute_script(js)
                time.sleep(2)
        except:
            print "get len error"
        f = open('e://1.html', 'w')
        f.write(driver.page_source)
        f.close()

            # tg1 = driver.find_element_by_xpath('/html/body/div[1]/div/ul/li[1]/a')
            # for i in range(10):
            #     # print tg1
            #     act.tap_and_hold(200,600).move(200,100).perform()#"模拟向下滑动屏幕"
            #     time.sleep(1)

            # tg2 = driver.find_element_by_xpath('/html/body/div[1]/div/ul/li[24]')
            # action.click_and_hold(tg1).move_by_offset(0,-1500).release().perform()



            # mongodb-operate

            # time.sleep(3)
            # resp2 = BeautifulSoup(driver.page_source, 'html5lib')
            # print len(resp2.find(class_='result-list').find_all(class_="item Fix"))
        driver.quit()
        # msg_list = []
        # msg_title=[]
        # msg_cover = resp.find_all("div", class_="weui_media_title")
        #
        # for href in msg_cover:
        #     if href.get("hrefs") is not None:
        #         msg_list.append(href.get("hrefs"))
        #     else:
        #         msg_cover_redirect = resp.find_all("a",class_="cover_appmsg_link_box redirect")
        #         for tmp in msg_cover_redirect:
        #             msg_list.append(tmp.get("hrefs"))
        #
        # sub_msg = resp.find_all("h4", class_="weui_media_title")
        #
        # for sub_href in sub_msg:
        #     msg_list.append(sub_href.get("hrefs"))
        #     msg_title.append(sub_href.text)
        #
        # print(msg_list)
        # print(msg_title)


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

if __name__ == '__main__':

    # key = sys.argv[1]
    # wechat_url = read_file('E:/3860_Headers.txt')
    # url = "https://m.dianping.com/shopping/mallshoplist/c2m1766320"
    # mall = '君太百货'
    url ="https://mp.weixin.qq.com/s?__biz=MjM5ODgwOTUwMg==&mid=2650087789&idx=2&sn=8cb932ce262555a406bff82ed10f3343&chksm=bec49b9c89b3128a192058cfbeca9c4c89c7181120d1826abfeae131d01102606093185d4dc4&scene=42&key=9d0d875582a7ed1e3fdfdddbaea2c823a38ceb0ccfb9c6ae67d039939cdf26fb7b0a65e8dbc5ad9e59b26655160b437cdae33e05ece6704c609da4bfdd837f7934bdd74c872e5dc67088b20b0a56436a&ascene=7&uin=ODQ1ODU5NjU%3D&devicetype=Windows+7&version=6204014f&pass_ticket=%2FLDaSg%2Fm8Q91w2nYztLnaZoHnZtunDNJY4RDPdFfr54%3D&winzoom=1"
    # if wechat_url:
    #     for url in wechat_url:
    #         print url
    #         wechat = crawl_dianping(url)
    #         wechat.get_list()
    dp = crawl_dianping(url)
    dp.get_shop_list()
