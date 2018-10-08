# -*- coding:utf-8 -*-

import jieba
import jieba.posseg as pseg
import os
import xlrd


from urllib import request, parse, error
import json
import string
import sys
import re
from presses import cennect_redis

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_dir)


# # 添加自定义词
# jieba.add_word(word, freq=None, tag=None)
# # 添加自定义词典
jieba.load_userdict(project_dir + "/static/city_dict")
jieba.load_userdict(project_dir + "/static/bussiness_dict")
jieba.load_userdict(project_dir + "/static/fault_dict")
jieba.load_userdict(project_dir + "/static/uncut_dict")
# 添加建议词
# jieba.suggest_freq(('今天','天气'), True)

# 加载数据
xls_file = xlrd.open_workbook(project_dir + '/static/test.xls')
xls_sheet = xls_file.sheet_by_name('standard_format')

# 加载同义词
file_dir = project_dir + "/static/Synonyms_dict.txt"
Syn_list = []
with open(file_dir,encoding='utf-8') as f1:
    for line in f1.readlines():
        Syn_words = line.strip().split()
        Syn_list.append(Syn_words)

        # 将同义词加入分词词典
        for word in Syn_words:
            jieba.add_word(word)

get_name_api_word_list = ["起名", "网名", "想个名字", "起个名字"]


from collections import Counter
# def  general_dict(filename = '../data/test.xls', sheetname = 'standard_format'):
#     '''
#     （1）读文件
#     xls_file = xlrd.open_workbook("file.name")
#     （2）打开工作bu
#     xls_sheet = xls_file.sheets()[num-1] num为第几个工作bu
#     （3）读取行/列数据（整行/整列）
#     row_value = xls_sheet.row_values(num-1) num为第几行
#     col_value = xls_sheet.col_values(num-1) col为第几列
#     （4）读取某行某列元素
#     用行索取：value = xls_sheet.row_values(row_num)[col_num].value
#     用列索取：value = xls_sheet.col_values(col_num)[row_num].value
#     用单元格获取：value = xls_sheet.cell(row_num,col_num).value
#     '''
#     xls_file = xlrd.open_workbook(filename)
#     xls_sheet = xls_file.sheet_by_name(sheetname)
#
#     # k列 所属市
#     city_list = xls_sheet.col_values(10)[1:]
#     citys = Counter(city_list)
#     # print("city list",city_list)
#     with open('../data/city_dict','w') as f1:
#         for city in citys:
#             print(city + " city")
#             f1.write(city + " city\n")
#     # v列 业务分
#     business_list = xls_sheet.col_values(21)[1:]
#     print("business list", business_list)
#     business_words = Counter(business_list)
#     with open('../data/bussiness_dict','w') as f2:
#         for b in business_words:
#             if b != 'null':
#                 f2.write(b + " bus\n")
#     # w列 故障原因类型
#     fault_list = xls_sheet.col_values(22)[1:]
#     # print("fault list", fault_list)
#     fault_words = Counter(fault_list)
#     with open('../data/fault_dict','w') as f3:
#         for fau in fault_words:
#             if fau != '':
#                 f3.write(fau + " fault\n")

def  search_xls_file(key_dict, filename = '/static/test.xls', sheetname = 'standard_format'):
    print("---search_xls_file---")
    # xls_file = xlrd.open_workbook(project_dir + filename)
    # xls_sheet = xls_file.sheet_by_name(sheetname)
    # key_dict{"city":[],"bus":[],"fau":[]} city:第10列  bus:第21列 fau:第22列
    print(key_dict)
    city_index = []
    if key_dict['bus'] ==[] and key_dict['fau'] == []:
        return ''
    elif key_dict['city'] == [] and (key_dict['bus'] !=[] or key_dict['fau'] != []):
        if 'ns' in key_dict['pos']:
            result = "没有该城市的数据"
            return result
        else:
            key_dict['city'] = ['沧州市','石家庄市','保定市','唐山市','秦皇岛市','邯郸市','衡水市','张家口市','雄安新区','廊坊市','承德市','邢台市']

    city_list = xls_sheet.col_values(10)
    for i in range(len(city_list)):
        if city_list[i] in key_dict["city"]:
            city_index.append(i)

    if key_dict['bus'] != []:
        bus_list = xls_sheet.col_values(21)
        for j in city_index:
            if bus_list[j] not in key_dict['bus']:
                city_index.pop()
    if key_dict['fau'] != []:
        fau_list = xls_sheet.col_values(22)
        for k in city_index:
            if fau_list[k] not in key_dict['fau']:
                city_index.pop()


    value_col = [0,1,4,9,10,11,15,16,21,23,24]
    value_col = [0,9,10,11,23,31]


    result = []
    for row in city_index:
        row_dict = {}
        row_value = xls_sheet.row_values(row)
        row_val = ''
        for ind in value_col:
            row_dict[xls_sheet.row_values(0)[ind]] = row_value[ind].strip()
            # row_val += " "+row_value[ind].strip()
        # print(row_val)
        result.append(row_dict)
    try:
        re = result[1]
        '''
        "条目ID": "WK_NETOPTIMIZE-15369168961959509",
        "问题点名称（弱覆盖名称）": "孟村县新县镇王帽圈村",
        "所属地市": "沧州市",
        "所属区县": "孟村回族自治县",
        "故障现象详细描述": "主被叫困难，上网慢",
        "解决延后原因": "
        '''
        re_sent = "问题的条目ID:{id}," \
                  "问题点名称（弱覆盖名称）:{name}," \
                  "所属地市:{city}," \
                  "所属区县:{dec}," \
                  "故障现象详细描述:{desc}," \
                  "解决延后原因:{reason}".format(id=re["条目ID"],
                                           name=re["问题点名称（弱覆盖名称）"],
                                           city=re["所属地市"],
                                           dec = re["所属区县"],
                                           desc = re["故障现象详细描述"],
                                           reason = re["解决延后原因"])
    except:
        re = 'not found!'
        re_sent = ''
    return re_sent



def get_intent(seq):
    print("---get_intent---")
    seg_list, pos_list = cut_seq(seq)
    # print(pos_list)
    intent = analysis_intent(seg_list)
    key_dict = {"city": [], "bus": [], "fau": [],"pos":[]}
    for pos in pos_list:
        if pos[1] == 'city':
            key_dict['city'].append(pos[0])
        elif pos[1] == 'bus':
            key_dict['bus'].append(pos[0])
        elif pos[1] == 'fault':
            key_dict['fau'].append(pos[0])
        key_dict['pos'].append(pos[1])
    return intent, seg_list, key_dict

def analysis_intent(seg_list):
    print("---analysis_intent---")
    # # intent: IT技术， 天气， 时间， 闲聊
    # houduan = ['分布式服务', '服务端组件', '分布式数据访问', '基础组件', '基础控件', '页面引擎', '横切关注']
    # fenbushi_server = ['远程调用', '协议集成', '集群监控', '动态部署', '服务治理']
    # fuwuduanzujian = ['分布式文件系统', '分布式缓存系统', '分布式计算']
    # IT_words = houduan + fenbushi_server + fuwuduanzujian
    # weather_words = ['天气','温度']
    # time_words = ['时间', '点钟']
    kv_os_intent = ['PUT','GET']

    intent = 'other_domain'
    for w in seg_list:
        print(w)
        if w in kv_os_intent:
            intent = 'redis_domain'
        # elif w in time_words:
        #     intent = 'time_domain'
    print(intent)
    return intent

def combos_intent(seq):
    # intent: IT技术， 天气， 时间， 闲聊
    combos = ['4G飞享套餐', '全球通无限尊享套餐', '任我用全国不限量套餐']


    intent = 'other_domain'
    for w in seq:
        print(w)
        if w in IT_words:
            intent = 'IT_domain'
        elif w in time_words:
            intent = 'time_domain'
    # print(intent)
    return intent

def cut_seq(seq):
    '''
    分词返回句子分词后list
    :param seq:
    :return:
    '''
    print("---cut_seq---")
    seg_list = []
    words = jieba.cut(seq)  # 默认是精确模式
    for word in words:
        for Syn in Syn_list:
            if word in Syn:
                word = Syn[0]
                # print(word, Syn)
        seg_list.append(word)


    words = pseg.cut(seq)
    pos_list = []
    for word, flag in words:
        for Syn in Syn_list:
            if word in Syn:
                word = Syn[0]
                flag = 'city'
                print(word, Syn)
        pos_list.append([word,flag])
    return seg_list, pos_list

def search_nickname(seq):
    print("---search_nickname---")
    name = ''
    for word in get_name_api_word_list:
        if word in seq:
            try:
                content = request.urlopen("https://www.apiopen.top/femaleNameApi?page=0")
                data = json.loads(content.read())
                name = data['data'][0]['femalename']
                return name
            except:
                name = ''
    return name


def save_redis(seq):
    print("---save_to_redis---")
    # '存储 "算法：SVM"，还有 "姓名：许志娟" 结束''
    # print(seq)
    seq_ = seq.replace(":","：")
    kv_dict = {}
    pattern = re.compile('"(.*?)"') #非贪婪
    print(pattern.findall(seq_))
    print(pattern.search(seq_))
    for kv_item in pattern.findall(seq_):
        # print(kv_item.split('：', 1))
        kv_dict[kv_item.split('：', 1)[0]] = kv_item.split('：', 1)[1]
    print(kv_dict)
    result = cennect_redis.save_to_redis(kv_dict)
    return result

def search_redis(seq):
    print("---search_redis---")
    res = ''
    # pattern = re.compile('"(.*?)"')
    # for key in pattern.findall(seq):
    seq_list = seq.split()[1:]
    print(seq_list)
    for key in seq_list:
        print(key)
        result = cennect_redis.get_from_redis(key)
        if result == None:
            res += " " + (key + ":查询的关键词不存在！")
        else:
            res += " " + (key + ":" + result)
    return res.strip()



def go_to_redis(seq, seg_list):
    print("---go_to_redis---")
    # kv_os_intent = ['帮我储存', '帮我查询']
    result = ''
    if seq.split()[0] == 'GET':
        result = search_redis(seq)
    else:
        for w in seg_list:
            if w == 'PUT':
                result = save_redis(seq)
            # elif w == 'GET':
            #     result = search_redis(seq)
    return result

# views.py调用函数
def re_to_api(seq):
    print("---re_to_api---")
    print("seq",seq)
    intent, seg_list, key_dict = get_intent(seq)
    print("intent, key_dict",intent, key_dict)
    if intent == "redis_domain":
        result = go_to_redis(seq, seg_list)
    else:
        result = search_xls_file(key_dict)
        if result == '':
            result = search_nickname(seq)
    # print("$$$", result)
    return result



# url 调用方法
def connect_api(seq):
    print("---connect_api---")
    import pprint

    print ('start connect...')
    try:
        ip_address = sys.argv[1]
    except:
        ip_address = "localhost"
    api = "http://{localhost}:8000/answer?q=".format(localhost = ip_address)
    # 沧州市的网络覆盖类LTE数据问题有哪些


    encode_seq = parse.quote(seq, safe=string.printable)
    url = api + encode_seq
    print("api+seq", url)
    # print("url:", url)


    try:
        content = request.urlopen(url)
        data = json.loads(content.read())
        print("-------url result:---------")
        # pprint.pprint(data)
        if data['code'] == 1:
            # for line in data['content']:
            #     print(line)
            print(data['content'])
    except error.HTTPError as e:
        print(e)

if __name__=="__main__":

    seq = input("输入句子：")
    # 沧州市的网络覆盖类LTE数据问题有哪些
    # magic储存"今天天气：晴"还有"昨天天气：多云"   magic查询"今天天气"



    # # print(get_intent(seq))
    # intent, key_dict = get_intent(seq)
    #
    # search_xls_file(key_dict)

    # print("%%%",re_to_api(seq))
    while seq != "q!":
        connect_api(seq)
        seq = input("输入句子：")

    # print(Syn_list)

