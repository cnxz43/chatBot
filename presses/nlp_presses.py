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
from presses import cennect_redis

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_dir)

# 加载数据
xls_file = xlrd.open_workbook(project_dir + '/static/test.xls')
knowledge_file = xlrd.open_workbook(project_dir + '/static/test.xls')
knowledge_sheet = xls_file.sheet_by_name('knowledge')

# 生成uncut词典
question_list = knowledge_sheet.col_values(0)
print("question",question_list)
uncut_path = project_dir + "/static/uncut_dict"
with open(uncut_path, 'w') as uncutFile:
    for i in range(len(question_list)):
        if i != 0:
            uncutFile.write(question_list[i] + ' ' + '20000' + '\n')

# # 添加自定义词
# jieba.add_word(word, freq=None, tag=None)
# # 添加自定义词典
jieba.load_userdict(project_dir + "/static/uncut_dict")

# 添加建议词
# jieba.suggest_freq(('今天','天气'), True)



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


    # 家客错误:
    knowledge_intent = question_list[1:]


    intent = 'other_domain'

    if intent != 'other_domain':
        pass
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
            elif w in knowledge_intent:
                intent = 'knowledge_domin'

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

                if word in question_list[1:]:
                    flag = 'knowledge'
                else:
                    flag = 'undefine'
                print(word, Syn)
        pos_list.append([word,flag])
    print(seg_list, pos_list)
    return seg_list, pos_list



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

import pytz, datetime
tz = pytz.timezone('Asia/Shanghai')

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
    now_local = time.localtime(now)
    publish_localtime = str(now_local.tm_year) + "-" + str(now_local.tm_mon) + "-" + str(now_local.tm_mday) + " " + sent_time
    #print(publish_localtime)

    # 转换成时间数组
    timeArray = time.strptime(publish_localtime, "%Y-%m-%d %H:%M")
    # print(now,"|", now_local.tm_year, now_local.tm_min,"|" ,timeArray )
    # print(now_local.tm_hour, now_local.tm_min)

    # 转换成时间戳
    timestamp = time.mktime(timeArray)

    # print("mmm", datetime.datetime.now(tz))
    now_str = str(datetime.datetime.now(tz))
    # print(now_str[:19])
    nowArray = time.strptime(now_str[:19], "%Y-%m-%d %H:%M:%S")
    nowstamp = time.mktime(nowArray)
    # print(timestamp,"timestamp")
    time_span = timestamp-nowstamp
    time_span = int(time_span)

    result = cennect_redis.publish_timed_task(nowstamp, time_span, value)
    print(value)

    return result



def go_to_knowladge(seq, seg_list):
    print("---go_to_knowladge---")

    error_list = question_list[1:]
    solution_list = knowledge_sheet.col_values(1)[1:]
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
        result = '知识库中没有答案！'
    else:
        result = result[0]
    return result




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

    elif intent == 'knowledge_domin':
        code = 1
        result = go_to_knowladge(seq,seg_list)

    else:
        code = 0
        result = ''


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

