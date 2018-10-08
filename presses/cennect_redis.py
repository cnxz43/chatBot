#!/usr/bin/env python
# -*- coding:utf-8 -*-
import redis

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
    value = r.get(key).decode()
    # print ("#",r.get(key).decode(),value)   #获取
    # key不存在会返回 None
    return value

if __name__=="__main__":
    kv_dict = {'今天天气':'晴'}
    print(save_to_redis(kv_dict))
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    print(r.get('今天天气').decode())
    print(r.get('昨天天气').decode())