# -*- coding:utf-8 -*-

import jieba
import os
import xlrd
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_dir)
# # 添加自定义词
# jieba.add_word(word, freq=None, tag=None)
# # 添加自定义词典
jieba.load_userdict(project_dir + "/static/city_dict")
jieba.load_userdict(project_dir + "/static/bussiness_dict")
jieba.load_userdict(project_dir + "/static/fault_dict")
# 添加建议词
# jieba.suggest_freq(('今天','天气'), True)




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
    xls_file = xlrd.open_workbook(project_dir + filename)
    xls_sheet = xls_file.sheet_by_name(sheetname)
    # key_dict{"city":[],"bus":[],"fau":[]} city:第10列  bus:第21列 fau:第22列
    city_index = []
    if key_dict['city'] == []:
        # key_dict['city'] = ['沧州市','石家庄市','保定市','唐山市','秦皇岛市','邯郸市','衡水市','张家口市','雄安新区','廊坊市','承德市','邢台市']
        result = "city not include"
        return result
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

    return result



def get_intent(seq):
    seg_list, pos_list = cut_seq(seq)
    # print(pos_list)
    intent = analysis_intent(seg_list)
    key_dict = {"city": [], "bus": [], "fau": []}
    for pos in pos_list:
        if pos[1] == 'city':
            key_dict['city'].append(pos[0])
        elif pos[1] == 'bus':
            key_dict['bus'].append(pos[0])
        elif pos[1] == 'fault':
            key_dict['fau'].append(pos[0])
    return intent, key_dict

def analysis_intent(seq):
    # intent: IT技术， 天气， 时间， 闲聊
    houduan = ['分布式服务', '服务端组件', '分布式数据访问', '基础组件', '基础控件', '页面引擎', '横切关注']
    fenbushi_server = ['远程调用', '协议集成', '集群监控', '动态部署', '服务治理']
    fuwuduanzujian = ['分布式文件系统', '分布式缓存系统', '分布式计算']
    IT_words = houduan + fenbushi_server + fuwuduanzujian
    weather_words = ['天气','温度']
    time_words = ['时间', '点钟']

    intent = 'other_domain'
    for w in seq:
        print(w)
        if w in IT_words:
            intent = 'IT_domain'
        elif w in time_words:
            intent = 'time_domain'
    # print(intent)
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
    seg_list = []
    words = jieba.cut(seq)  # 默认是精确模式
    for word in words:
        seg_list.append(word)

    import jieba.posseg as pseg
    words = pseg.cut(seq)
    pos_list = []
    for word, flag in words:
        pos_list.append([word,flag])
    return seg_list, pos_list

def re_to_api(seq):
    intent, key_dict = get_intent(seq)
    result = search_xls_file(key_dict)
    return result

if __name__=="__main__":
    seq = input("输入句子：")
    # 沧州市的网络覆盖类LTE数据问题有哪些


    # # print(cut_seq(seq))
    # seg_list, pos_list = cut_seq(seq)
    # print(pos_list)
    # analysis_intent(seg_list)

    # print(get_intent(seq))
    intent, key_dict = get_intent(seq)

    search_xls_file(key_dict)