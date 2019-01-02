# -*- coding:utf-8 -*-

import jieba
import jieba.posseg as pseg
import os
import xlrd
import time


from urllib import request, parse, error
import json
import string
import sys
import re
from presses import cennect_redis, spider, CreateBase

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_dir)


# # 添加自定义词
# jieba.add_word(word, freq=None, tag=None)
# # 添加自定义词典
jieba.load_userdict(project_dir + "/static/city_dict")
jieba.load_userdict(project_dir + "/static/bussiness_dict")
jieba.load_userdict(project_dir + "/static/fault_dict")
jieba.load_userdict(project_dir + "/static/uncut_dict")
jieba.load_userdict(project_dir + "/static/userdict.txt")
# 添加建议词
# jieba.suggest_freq(('今天','天气'), True)

# 加载数据
xls_file = xlrd.open_workbook(project_dir + '/static/test.xls')
xls_sheet = xls_file.sheet_by_name('standard_format')

jiake_file = xlrd.open_workbook(project_dir + '/static/test.xls')
jiake_sheet = xls_file.sheet_by_name('jiake')

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
city_list = ['沧州市', '石家庄市', '保定市', '唐山市', '秦皇岛市', '邯郸市', '衡水市', '张家口市', '雄安新区', '廊坊市', '承德市', '邢台市']
jiake_ecodes = ['错误代码','错误提示','账户已停机','UserToken失效',
                    '未知的异常','LOS亮红灯','部分直播黑屏','全部直播黑屏',
                    '黑白屏','点播视频播放不完整或回跳','用户账号不存在','用户绑定MAC与登录MAC不匹配',
                    '自动获取业务账号中','UserToken过期',
                    '未知的异常','订购失败','检测账号中','网管服务器数据下发超时','机顶盒恢复出厂的方法',
                    '查看机顶盒获得IP地址的方法']


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
    intent = analysis_intent(seq, seg_list)
    key_dict = {"city": [], "bus": [], "fau": [],"pos":[]}
    for pos in pos_list:
        if pos[1] == 'city':
            key_dict['city'].append(pos[0])
        elif pos[1] == 'bus':
            key_dict['bus'].append(pos[0])
        elif pos[1] == 'fault':
            key_dict['fau'].append(pos[0])
        key_dict['pos'].append(pos[1])
    print(intent)
    return intent, seg_list, key_dict, pos_list

def analysis_intent(seq, seg_list):
    print("---analysis_intent---")

    # key value存取redis
    kv_os_intent = ['PUT','GET']

    # 定时任务
    timed_task_intent = ['AT']

    # 舆情 1.更新舆情 2.获取网易排行 3.获取微博排行
    toprank_intent = ['更新排行榜', '网易新闻排行','网易新闻', '微博热搜排行','微博热搜排行榜','新浪热搜排行','天气预警','灾害预警']

    '''
    update_toprank_intent = ['更新排行榜']
    get_neteaserank_intent = ['网易新闻排行','网易新闻']
    get_sinarank_intent = ['微博热搜排行','微博热搜排行榜','新浪热搜排行']
    get_alarm_intent = ['天气预警','灾害预警']
    '''

    # 家客错误:
    jiake_intent = jiake_ecodes

    # 人员知识图谱
    knowledge_graph = ['FIND']

    intent = 'other_domain'
    # for k in jiake_intent:
    #     if k in seq:
    #         intent = 'knowladge_domin'
    if intent != 'other_domain':
        pass
    elif seq in toprank_intent:
        intent = 'toprank_domain'
    else:
        for w in seg_list:
            # print(w)

            # key value存取redis
            if w in kv_os_intent:
                intent = 'redis_domain'

            # 定时任务
            elif w in timed_task_intent:
                intent = 'timed_domain'

            # 家客知识库
            elif w in jiake_intent:
                intent = 'jiake_domin'
            # 知识图谱
            elif w in knowledge_graph:
                intent = 'kg_domain'
    print(intent)
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
                if word in city_list:
                    flag = 'city'
                elif word in jiake_ecodes:
                    flag = 'jiake'
                else:
                    flag = 'undefine'
                print(word, Syn)
        pos_list.append([word,flag])
    print(seg_list, pos_list)
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
    # seq_ = seq.replace("：",":")
    kv_dict = {}
    pattern = re.compile('"(.*?)"') #非贪婪
    print(pattern.findall(seq))
    print(pattern.search(seq))
    for kv_item in pattern.findall(seq):
        print(kv_item.split('：', 1))
        temp_item = kv_item.replace("：",":")
        temp_key = temp_item.split(':', 1)[0]
        kv_dict[temp_key] = kv_item[len(temp_key)+1:]#kv_item.split(':', 1)[1]
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


def go_to_timedtask(seq, seg_list):
    print("---go_to_timedtask---")
    # seq: "AT 17:59 通知：请各位立刻去813开会"
    # result = {'value': '', 'time': '17:49'}
    '''
    将seq处理成标准格式，切分出value和time, 存入redis
    '''
    # split_seq = seq.strip()
    split_seq = seq.split(' ', 2)
    print("split_seq",split_seq)
    sent_time = split_seq[1]
    sent_time= sent_time.replace("：", ":")
    value = split_seq[2]
    now = time.time()
    now_local = time.localtime()
    publish_localtime = str(now_local.tm_year) + "-" + str(now_local.tm_mon) + "-" + str(now_local.tm_mday) + " " + sent_time
    #print(publish_localtime)

    # 转换成时间数组
    timeArray = time.strptime(publish_localtime, "%Y-%m-%d %H:%M")
    #print(now,"|", now_local.tm_year,"|" ,timeArray )

    # 转换成时间戳
    timestamp = time.mktime(timeArray)

    time_span = timestamp-now
    time_span = int(time_span)

    result = cennect_redis.publish_timed_task(now, time_span, value)
    print(value)

    return result

def go_to_spider(seq):
    print("---go_to_spider---")
    update_toprank_intent = ['更新排行榜']
    get_neteaserank_intent = ['网易新闻排行','网易新闻']
    get_sinarank_intent = ['微博热搜排行','微博热搜排行榜','新浪热搜排行']
    get_alarm_intent = ['天气预警','灾害预警']
    if seq in update_toprank_intent:
        result = spider.update_data()
    elif seq in get_neteaserank_intent:
        result = spider.read_netease_file()
    elif seq in get_sinarank_intent:
        result = spider.read_sina_file()
    elif seq in get_alarm_intent:
        result = spider.read_alarm(city_list)
    else:
        result = "获取排行榜失败！"
    return result

def go_to_knowladge(seq, seg_list):
    print("---go_to_knowladge---")

    error_list = jiake_sheet.col_values(0)
    solution_list = jiake_sheet.col_values(1)
    print(error_list)
    print(solution_list)
    result = []

    for w in seg_list:
        for i in range(len(error_list)):
            if error_list[i] == w:
                result.append(solution_list[i])
    if result == []:
        for i in range(len(error_list)):
            if error_list[i] == seq:
                result.append(solution_list[i])
    # print(result)
    if result == []:
        result = '家客知识库中没有答案！'
    else:
        result = result[0]
    return result


from py2neo import Node, NodeMatcher, RelationshipMatcher, walk
def go_to_neo4j(pos_list):
    print("---go_to_neo4j---")

    # print(seq,seg_list,key_dict)
    '''
    知识图谱包含类型：
    apartment：name
    room：name
    people：id name ph addr email
    电话号码 phx
    邮箱 emailx
    地址 addrx
    科室 roomx
    员工 peoplex
    部门 apartmentx
    信息 informationx
    查询图谱 kgx

    matcher = RelationshipMatcher(graph) 
    result = matcher.match({node1},'know')
 
    '''
    people_name = ''
    room_name = ''
    # apmt_name = ''
    result_from = ''
    result_type = ['phx','emailx','addrx','informationx','roomx','peoplex','apartmentx']
    for pair in pos_list:
        if pair[1] == 'name':
            people_name = pair[0]
        elif pair[1] == 'room':
            room_name = pair[0]
        # elif pair[1] == 'apartment':
        #     apmt_name = pair[0]
        elif pair[1] in result_type:
            result_from = pair[1]
    print("people_name",people_name)
    print("room_name",room_name)
    print("result_from",result_from)
    result = []
    try:
        pp_graph = CreateBase.connect_graph()
        matcher = NodeMatcher(pp_graph)
        people_node = matcher.match('people', name= people_name)

        room_node = matcher.match('room', name= room_name)
        # print('node:',list(people_node),'\n',list(room_node))
        # apartment_node = matcher.match('apartment', name= apmt_name)
        if result_from in ['phx','emailx','addrx','informationx']:
            print('### people info ###')
            for node in people_node:
                if result_from == 'phx':
                    result.append(node['name']+'：'+node['ph'])
                elif result_from == 'emailx':
                    result.append(node['name']+'：'+node['email'])
                elif result_from == 'addrx':
                    result.append(node['name']+'：'+node['addr'])
                elif result_from == 'informationx':
                    result.append(node['name']+'：'+node['ph']+' '+node['email']+' '+node['addr'])
                print(result)
        elif result_from == 'peoplex':
            print('### people name ###')
            # 通过科室返回人名
            # for rel in pp_graph.match(start_node=room_node, r_type="have"):
            #     print(rel.end_node["name"])
            for node in room_node:
                matcher = RelationshipMatcher(pp_graph)
                match_res = matcher.match({node}, 'have')
                for x in match_res:
                    y = walk(x)
                    next(y)
                    next(y)
                    end_node = next(y)['name']
                    # print(end_node)
                    if end_node != room_name:
                        result.append(end_node)

                    # print(next(y)['name'])
        elif result_from == 'roomx':
            print('### room name ###')
            # 通过人名返回科室
            print('aaa')
            for node in people_node:
                matcher = RelationshipMatcher(pp_graph)
                match_res = matcher.match({node}, 'belong')
                for x in match_res:
                    y = walk(x)
                    # y.__next__()
                    next(y)
                    next(y)
                    end_node = (next(y)['name'])
                    result.append(end_node)
        result_ = ''
        for sent in result:
            result_ += sent + ' '


    except:
        result_ = '查询知识图谱失败'
    print("kg",result_)
    return result_



# views.py调用函数
def re_to_api(nature_seq):
    print("---re_to_api---")
    seq = nature_seq.strip()
    print("seq",seq)
    code = 0

    # 判断意图及分词
    intent, seg_list, key_dict, pos_list = get_intent(seq)
    print("intent, key_dict",intent, key_dict)

    if intent == "redis_domain":
        code = 1
        result = go_to_redis(seq, seg_list)
    elif intent == "timed_domain":
        code = 1
        #result = {'value':'','time':'2018-10-24 17:49:50'}
        result = go_to_timedtask(seq, seg_list)
    elif intent == 'toprank_domain':
        code = 1
        result = go_to_spider(seq)
    elif intent == 'jiake_domin':
        code = 1
        result = go_to_knowladge(seq,seg_list)
    elif intent == "kg_domain":
        code = 1
        result = go_to_neo4j(pos_list)
    else:
        result = search_xls_file(key_dict)
        if result == '':
            result = search_nickname(seq)
    if result != '':
        code = 1
    else:
        code = 0

    result_dict = {'code':code, 'content':str(result), 'sentence':nature_seq}
    return result_dict



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


    while seq != "q!":
        # connect_api(seq)
        print("%%%",re_to_api(seq))
        seq = input("输入句子：")

    # print(Syn_list)

