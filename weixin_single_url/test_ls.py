#!/usr/bin/python
# coding: utf-8
import re,datetime
if __name__ == '__main__':
    ls = range(3)
    print ls
    a= int(len(ls)/3)
    b= int(len(ls)/1.5)
    print ls[:a],ls[a:b],ls[b:]
    tmp1 = u"ZARA H&M MUJI 2018-07-24"
    ls = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", tmp1)
    print ls

    if ls:
        print ls[0]
        # print datetime.datetime.strptime(ls[0], u'%Y年%m月%d日')
        date_iso = datetime.datetime.strptime(ls[0], u'%Y-%m-%d')
    else:
        date_iso = datetime.datetime.utcnow()
    print type(date_iso.strftime(u'%Y-%m-%d'))