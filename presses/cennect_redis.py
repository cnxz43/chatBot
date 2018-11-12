#!/usr/bin/env python
# -*- coding:utf-8 -*-
import redis
from presses import spider, nlp_presses


def save_to_redis(kv_dict):
    try:
        r = redis.StrictRedis(host='localhost', port=6379,db=0)
        for key, value in kv_dict.items():
            print(key,value)
            r.set('昨天天气','多云')
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
    try:
        if time_span >= 0:
            conn = redis.StrictRedis()
            key = str(now)
            key_expire = str(now) + '_e'
            conn.set(key, value)
            conn.set(key_expire, 'expire')
            conn.expire(key_expire,time_span)
            # conn.get(key)
            return "设定定时任务成功！"
        else:
            return "发布定时任务失败,定时任务发生在过去！"
    except:
        return "发布定时任务失败!"

def publish_alarm():
    message = spider.read_alarm(nlp_presses.city_list)
    # message = str(alarm_list)
    pool = redis.ConnectionPool(host='192.168.100.30',
                                port=6379, db=0,
                                password='123456')
    conn = redis.StrictRedis(connection_pool=pool)
    # conn = redis.StrictRedis()
    conn.publish('weather-alarm',message)
    return ('发布天气预警！')

if __name__=="__main__":
    kv_dict = {'今天天气':'晴'}
    print(save_to_redis(kv_dict))
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    print(r.get('今天天气').decode())
    print(r.get('昨天天气').decode())