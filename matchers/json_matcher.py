#!/bin/env python3
#-*- coding: utf-8 -*-
import json

from common.net import Request, Response

def get_poi(data, poi):
    pass

def get_ret(data, m):
    pass

# type : one | more
# map: 字典，用于映射结果字段，其中key和value的详细解释如下：
## key: 结果字典的key
## value: 字典，用于匹配对应的值，其中包含type、map，解释如下:
### type: 表示结果字典值得类型，str、int、dict、list
### map: 根据值得类型不同而不同，各类型时的含义如下：
#### dict: 同上一层map，用于映射结果字段，递归
#### list: 字符串集合，用于匹配list的json节点定位字符串
#### 其他: 字符串，用于json节点定位
# item(type=more): 多个结果所在数组的json节点定位字符串
async def match(cfg : dict, req : Request, resp : Response):
    data = json.loads(resp.raw)
    t = cfg.get('type')
    m = cfg.get('map')
    if t == 'one':
        return [get_ret(data, m)]
    else:
        ret = []
        for i in get_poi(cfg.get('item')):
            ret.append(get_ret(i, m))
        return ret
        