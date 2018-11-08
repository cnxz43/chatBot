# -*- coding: utf-8 -*-
import os
import requests
import re
from lxml import etree
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(project_dir)
save_path = project_dir + "/static/top_news/"





def StringListSave(filename, slist):
    print("---StringListSave---")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    path = save_path +filename+".txt"
    with open(path, "w+") as fp:
        for s in slist:
            # print("s",s)
            # fp.write("%s\t\t%s\n" % (s[0], s[1]))
            fp.write("%s\n" % s[0])

def Page_Info(myPage):
    print("---Page_Info---")
    '''Regex'''
    mypage_Info = re.findall(r'<div class="titleBar" id=".*?"><h2>(.*?)</h2><div class="more"><a href="(.*?)">.*?</a></div></div>', myPage, re.S)
    return mypage_Info

def New_Page_Info(new_page):
    print("---New_Page_Info---")
    '''Regex(slowly) or Xpath(fast)'''
    dom = etree.HTML(new_page)
    #print(new_page)
    new_items = dom.xpath('//tr/td/a/text()')
    new_urls = dom.xpath('//tr/td/a/@href')
    assert(len(new_items) == len(new_urls))
    return zip(new_items, new_urls)

def netease_Spider():
    print("---netease_Spider---")
    i = 0
    url = "http://news.163.com/rank/"
    # print ("downloading ", url)
    myPage = requests.get(url).content.decode("gbk")
    # myPage = urllib2.urlopen(url).read().decode("gbk")
    myPageResults = Page_Info(myPage)
    filename = str(i)+"_"+u"新闻排行榜"
    StringListSave(filename, myPageResults)
    i += 1
    for item, url in myPageResults:
        # print ("downloading ", url)
        new_page = requests.get(url).content.decode("gbk")
        # new_page = urllib2.urlopen(url).read().decode("gbk")
        newPageResults = New_Page_Info(new_page)
        filename = str(i)+"_"+item
        StringListSave(filename, newPageResults)
        i += 1

def sina_Spider():
    print("---sina_Spider---")
    i = 0
    url = "https://s.weibo.com/top/summary?Refer=top_hot"
    # print ("downloading ", url)
    myPage = requests.get(url).content #.decode("gbk")
    # myPage = urllib2.urlopen(url).read().decode("gbk")
    myPageResults = New_Page_Info(myPage)
    filename = str(i)+"_"+u"热搜排行榜"
    StringListSave(filename, myPageResults)



def read_netease_file():
    print("---read_netease_file---")
    '''
    读取data目录下所有数据
    :return:
    '''
    file = save_path + "1_全站.txt"  #文件夹目录
    top_list = []
    with open(file) as f:
        for line in f.readlines():
            # print(line.strip())
            top_list.append(line.strip())
    return top_list[:5]

def read_sina_file():
    print("---read_sina_file---")
    file = save_path + "0_热搜排行榜.txt"
    top_list = []
    with open(file) as f:
        for line in f.readlines():
            # print(line.strip())
            top_list.append(line.strip())
    return top_list[:5]

def update_data():
    print("---update_data---")
    result = ''
    try:
        netease_Spider()
        result += "更新网易新闻排行成功!"
    except:
        result += "更新网易新闻排行失败!"

    try:
        sina_Spider()
        result += "\t更新新浪热搜排行成功!"
    except:
        result += "\t更新新浪热搜排行失败!"
    return result


if __name__ == '__main__':
    print ("start")
    # 更新排行
    # update_data()

    # 读取排行
    read_netease_file()
    read_sina_file()
    print ("end")

