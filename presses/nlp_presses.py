# -*- coding:utf-8 -*-

import jieba


# # 添加自定义词
# jieba.add_word(word, freq=None, tag=None)
# # 添加自定义词典
# jieba.load_userdict(user_dicat)
# 添加建议词
jieba.suggest_freq(('今天','天气'), True)


import xlrd
def  read_xls_file(filename = '../data/test.xls', sheetname = 'standard_format'):
    '''
    （1）读文件
    xls_file = xlrd.open_workbook("file.name")
    （2）打开工作bu
    xls_sheet = xls_file.sheets()[num-1] num为第几个工作bu
    （3）读取行/列数据（整行/整列）
    row_value = xls_sheet.row_values(num-1) num为第几行
    col_value = xls_sheet.col_values(num-1) col为第几列
    （4）读取某行某列元素
    用行索取：value = xls_sheet.row_values(row_num)[col_num].value
    用列索取：value = xls_sheet.col_values(col_num)[row_num].value
    用单元格获取：value = xls_sheet.cell(row_num,col_num).value
    '''
    xls_file = xlrd.open_workbook(filename)
    xls_sheet = xls_file.sheet_by_name(sheetname)

    # k列 所属市
    city_list = xls_sheet.col_values(10)
    print("city list",city_list)
    # v列 业务分类
    business_list = xls_sheet.col_values(21)
    print("business list", business_list)
    # w列 故障原因类型
    fault_list = xls_sheet.col_values(22)
    print("fault list", fault_list)

def get_intent(seq):
    seg_list, _ = cut_seq(seq)
    intent = analysis_intent(seg_list)
    return intent

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


if __name__=="__main__":
    # seq = input("输入句子：")

    # # print(cut_seq(seq))
    # seg_list, pos_list = cut_seq(seq)
    # print(pos_list)
    # analysis_intent(seg_list)

    # print(get_intent(seq))


    read_xls_file()