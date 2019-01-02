#!/usr/bin/env python
# -*- coding:utf-8 -*-
import redis
from presses import nlp_presses


def save_to_redis(kv_dict):
    try:
        r = redis.StrictRedis(host='localhost', port=6379,db=0)
        for key, value in kv_dict.items():
            print(key,value)
            # r.set('昨天天气','多云')
            r.set(key, value)   #添加
        return "储存成功！"
    except:
        return "储存失败！"


def get_from_redis(key):
    print("---get_from_redis---")
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    try:
        value = r.get(key).decode()
    except:
        value = r.get(key)
    # print ("#",r.get(key).decode(),value)   #获取
    # key不存在会返回 None
    return value

def publish_timed_task(now, time_span, value):
    print("---publish_timed_task---")
    print(now, time_span, value)
    try:
        if time_span >= 0:
            conn = redis.StrictRedis(host='localhost', port=6379, db=0)
            key = str(now)
            key_expire = str(now) + '_e'

            # 同时存入两条
            conn.set(key, value)  # 任务内容
            conn.set(key_expire, 'expire')  # 过期内容
            conn.expire(key_expire,time_span) #
            # conn.get(key)
            return "设定定时任务成功！"
        else:
            return "发布定时任务失败,定时任务发生在过去！"
    except:
        return "发布定时任务失败!"



if __name__=="__main__":
    kv_dict = {'今天天气':'晴'}
    print(save_to_redis(kv_dict))
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    print(r.get('今天天气').decode())
    print(r.get('昨天天气').decode())