#!/bin/env python3
#-*- coding: utf-8 -*-
import re
import sys
import json
import base64
import aiohttp
import asyncio

sys.path.append('.')
from common.net import Request, Response

async def fileb64e(req : Request, url):
    async with aiohttp.ClientSession() as sess:
        try:
            async with sess.get(url, headers=req.headers, timeout=30) as resp:
                return base64.b64encode(await resp.read()).decode()
        except:
            try:
                async with sess.get(url.replace('http:', 'https:'), headers=req.headers, timeout=30) as resp:
                    return base64.b64encode(await resp.read()).decode()
            except:
                return url

async def get_poi(req : Request, data : dict, poi : str):
    ret = data.copy()
    s = poi.split(':')
    poi = s[0]
    expn = None
    re_group_i = 0
    if len(s) > 1:
        expn = s[1]
    if len(s) > 2:
        re_group_i = int(s[2])
    for k in poi.split('.'):
        if len(k.strip()) != 0:
            ret = ret.get(k)
            if expn:
                if expn == 'b64d':
                    ret = base64.b64decode(ret).decode()
                elif expn == 'fileb64e':
                    ret = await fileb64e(req, ret)
                else:
                    m = re.search(expn, ret)
                    if m:
                        ret = m.group(re_group_i)
                    else:
                        ret = ''
    return ret

async def get_ret(req : Request, data : dict, m):
    ret = {}
    for k in m.keys():
        v = m.get(k)
        if isinstance(v, dict):
            ret[k] = await get_ret(req, data, v.get('map'))
        elif isinstance(v, list):
            ret[k] = []
            for p in v:
                v = await get_poi(req, data, p)
                if isinstance(v, list):
                    ret[k].extend(v)
                else:
                    ret[k].append(v)
        else:
            ret[k] = await get_poi(req, data, v)
    return ret

# type : one | more
# map: 字典，用于映射结果字段，其中key和value的详细解释如下：
## key: 结果字典的key
## value: 字典，用于匹配对应的值，其中包含type、map，解释如下:
### map: 根据值得类型不同而不同，各类型时的含义如下：
#### dict: 同上一层map，用于映射结果字段，递归
#### list: 字符串集合，用于匹配list的json节点定位字符串
#### 其他: 字符串，用于json节点定位
# item(type=more): 多个结果所在数组的json节点定位字符串
# add: 字典，key 为添加的字段位置，value为添加的值
# json节点定位字符串详解：
## 定位字符串:正则匹配字符:正则匹配组id(前者必须有，后两者可选，后两者没有时为所选全部)
async def match(cfg : dict, req : Request, resp : Response):
    data = json.loads(resp.raw)
    t = cfg.get('type')
    m = cfg.get('map')
    if t == 'one':
        r = await get_ret(req, data, m)
        for k in cfg.get('add').keys():
            rr = r
            ks = k.split('.')
            lk = ks[-1]
            for kk in ks[:-1]:
                if len(kk.strip()) != 0:
                    tmp = rr.get(kk)
                    if not tmp:
                        rr = tmp
                    else:
                        rr[kk] = {}
                        rr = rr.get(kk)
            rr[lk] = r.get(k)
        return [r]
    else:
        ret = []
        for i in await get_poi(req, data, cfg.get('item')):
            ret.append(await get_ret(req, i, m))
        for r in ret:
            for k in cfg.get('add').keys():
                rr = r
                ks = k.split('.')
                lk = ks[-1]
                for kk in ks[:-1]:
                    if len(kk.strip()) != 0:
                        tmp = rr.get(kk)
                        if not tmp:
                            rr = tmp
                        else:
                            rr[kk] = {}
                            rr = rr.get(kk)
                rr[lk] = cfg.get('add').get(k)
        return ret
        

if __name__ == '__main__':
    payload = b'{"msg": "success", "error_code": 0, "data": {"total": 81, "accounts": [{"mid": 650293, "mp_name": "\\u5317\\u4eac\\u65b0\\u95fb", "wxid": "brtvbjxw", "desc": "\\u805a\\u7126\\u5317\\u4eac\\u7684\\u65b0\\u95fb\\uff0c\\u7740\\u529b\\u62a5\\u9053\\u70ed\\u70b9\\u6c11\\u751f\\uff1b\\u5173\\u5fc3\\u5317\\u4eac\\u7684\\u4e8b\\u513f\\uff0c\\u65f6\\u5e38\\u53d1\\u5e03\\u5b9e\\u7528\\u4fe1\\u606f\\uff1b\\u4e13\\u6ce8\\u5317\\u4eac\\u7684\\u751f\\u6d3b\\uff0c\\u4e0d\\u65ad\\u53d1\\u653e\\u5927\\u5c0f\\u798f\\u5229\\u3002\\u65e0\\u8bba\\u662f\\u5426\\u8eab\\u5728\\u5317\\u4eac\\uff0c\\u60a8\\u9700\\u8981\\u6765\\u81ea\\u5317\\u4eac\\u7684\\u65b0\\u95fb\\uff01", "tag": [], "avatar": "http://mmbiz.qpic.cn/mmbiz_png/LCChw9N6UicdRoeibDg82mPebcm46nq9ian3CpoDHLsqLKajT6uNyC7UyuibwzQZpjNA377IqInO1bthpGsnzAuCJA/0?wx_fmt=png", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 622106, "avg_top_read": 14153, "avg_top_praise": 61, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 34, "dajiala_index": 175.44, "ghid": "", "area": "", "register": "2014-07-12", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_406cd9af657e", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 200, "original_count": 0, "webtask_count": 1, "lastest_publish": "2022-08-26 14:43", "high_title": "", "high_desc": "", "total_monitoring": 2, "register_time": "2014-07-12", "create_time": "2019-12-13 10:44:21", "biz": "MzA3OTg1NTAzNw=="}, {"mid": 102054, "mp_name": "\\u5317\\u4eac\\u536b\\u89c6\\u517b\\u751f\\u5802", "wxid": "btv_yangshengtang", "desc": "\\u5317\\u4eac\\u536b\\u89c6\\u300a\\u517b\\u751f\\u5802\\u300b\\uff0c\\u4f20\\u9012\\u5065\\u5eb7\\u517b\\u751f\\u77e5\\u8bc6~", "tag": [], "avatar": "http://mmbiz.qpic.cn/mmbiz_png/iac0vE8Nzz4DibzR2GjVIUbvibV8Z7e0Iq7rce7b2e3hpj8I2P6vNFHCzCeXtCAV19ZEQVT0Cxib4IMquNWs2Z1icqA/0?wx_fmt=png", "account_type": 100, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 3724829, "avg_top_read": 70443, "avg_top_praise": 519, "area_id": "", "age": [], "original_index": 2299.0, "week_articles": 8, "dajiala_index": 139.59, "ghid": "", "area": "", "register": "2014-10-09", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_af6012b4b6ea", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 5099, "original_count": 0, "webtask_count": 1, "lastest_publish": "2022-08-25 17:08", "high_title": "", "high_desc": "", "total_monitoring": 4, "register_time": "2014-10-09", "create_time": "2019-08-04 12:01:03", "biz": "MzAwOTA3NDYyNg=="}, {"mid": 50782, "mp_name": "\\u6696\\u6696\\u7684\\u5473\\u9053\\u5b98\\u5fae", "wxid": "btvjiadeweidao", "desc": "\\u6bcf\\u5929\\u6559\\u60a8\\u4e00\\u9053\\u5927\\u53a8\\u5bb6\\u5e38\\u83dc\\uff01\\u613f\\u4f60\\u5728\\u8f7b\\u677e\\u6109\\u5feb\\u7684\\u6c1b\\u56f4\\u4e2d\\u5b66\\u4e60\\u70f9\\u996a\\u6280\\u5de7\\u3001\\u751f\\u6d3b\\u7a8d\\u95e8\\u3001\\u517b\\u751f\\u77e5\\u8bc6\\u3002\\u8282\\u76ee\\u64ad\\u51fa\\u65f6\\u95f4\\u5468\\u4e00\\u5230\\u5468\\u516d17:10\\uff0c\\u516c\\u4f17\\u53f716:00\\u62a2\\u5148\\u77e5\\u6653\\u8282\\u76ee\\u5185\\u5bb9+\\u9884\\u544a\\uff0c\\u53c2\\u4e0e\\u4e92\\u52a8\\u66f4\\u6709\\u514d\\u8d39\\u8bd5\\u5403\\u54e6~", "tag": [], "avatar": "http://mmbiz.qpic.cn/mmbiz_png/QDTa3lHem03f0KrP3I3HKNzHh4POdhZgcFWbRCy3z4H9WiadjrGdibQicOywGP1KibGNCW7jj3Ac38MFzxIiatXeu8g/0?wx_fmt=png", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 3624038, "avg_top_read": 88025, "avg_top_praise": 266, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 10, "dajiala_index": 459.23, "ghid": "", "area": "", "register": "2015-11-04", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_7b9210bbc578", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 468, "original_count": 0, "webtask_count": 1, "lastest_publish": "2022-08-25 16:01", "high_title": "", "high_desc": "", "total_monitoring": 28, "register_time": "2015-11-04", "create_time": "2019-06-26 14:40:02", "biz": "MzA4MTUzODI0Ng=="}, {"mid": 45483, "mp_name": "\\u82f1\\u8bedPK\\u53f0", "wxid": "goingforgold774", "desc": "\\u3010\\u5317\\u4eac\\u5916\\u8bed\\u5e7f\\u64ad\\u738b\\u724c\\u6559\\u5b66\\u680f\\u76ee\\u3011\\u4e00\\u6863\\u4ee5\\u57f9\\u517b\\u5b9e\\u7528\\u82f1\\u8bed\\u6280\\u80fd\\uff08\\u6d41\\u5229\\u542c\\u8bf4\\uff09\\u4e3a\\u7279\\u8272\\u7684\\u8f7b\\u5a31\\u4e50\\u5f0f\\u5e7f\\u64ad\\u82f1\\u8bed\\u6559\\u5b66\\u8282\\u76ee\\u3002\\u8363\\u83b7\\u201c\\u65b0\\u6d6a\\u58f0\\u52a8\\u4e2d\\u56fd\\u2014\\u6700\\u53d7\\u6b22\\u8fce\\u5916\\u8bed\\u7c7b\\u8282\\u76ee\\u201d\\u3002\\u516c\\u76ca\\u6559\\u5b66\\u7b2c\\u5341\\u5e74\\uff0c\\u5e26\\u9886\\u5b66\\u4e60\\u8005\\u653b\\u514b\\u82f1\\u8bed\\uff0c\\u8fde\\u63a5\\u4e16\\u754c\\uff0c\\u542f\\u53d1\\u5fc3\\u667a\\uff0c\\u63d0\\u5347\\u4eba\\u751f\\u3002", "tag": [], "avatar": "http://mmbiz.qpic.cn/mmbiz_png/FhZAMVUpfUh83BqUx7bL86OxJCxI6ERE6ia5Zbniaebvs8JIzWaBoCoDnnnxtO9h2uPm9cgKPVT8JN5ONWvf6QnA/0?wx_fmt=png", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 77205, "avg_top_read": 1131, "avg_top_praise": 19, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 3, "dajiala_index": 2.05, "ghid": "", "area": "", "register": "2014-02-26", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_302cd8838455", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 310, "original_count": 0, "webtask_count": 0, "lastest_publish": "2022-08-05 18:05", "high_title": "", "high_desc": "", "total_monitoring": 0, "register_time": "2014-02-26", "create_time": "2019-12-12 23:36:27", "biz": "MzA3OTQwMTAwNw=="}, {"mid": 90519, "mp_name": "\\u5317\\u4eac\\u4ea4\\u901a\\u5e7f\\u64ad", "wxid": "jtgbfm1039", "desc": "\\u5317\\u4eac\\u4ea4\\u901a\\u5e7f\\u64ad\\uff0c\\u8ba9\\u4f60\\u7684\\u51fa\\u884c\\u66f4\\u8f7b\\u677e\\uff01", "tag": [], "avatar": "http://mmbiz.qpic.cn/sz_mmbiz_png/wSf4PzRytP1ia17xoyfoakqKUUVuED5YXvaIlibMn5jBEiczOosB5eiaKgAgXOxQVC8MJaU7H8L3IvSYffaGYjqOIQ/0?wx_fmt=png", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 665992, "avg_top_read": 17703, "avg_top_praise": 31, "area_id": "", "age": [], "original_index": 85.0, "week_articles": 22, "dajiala_index": 160.27, "ghid": "", "area": "", "register": "2013-09-17", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_f7ff268f3d09", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 473, "original_count": 0, "webtask_count": 1, "lastest_publish": "2022-08-26 10:25", "high_title": "", "high_desc": "", "total_monitoring": 17, "register_time": "2013-09-17", "create_time": "2019-08-30 11:17:03", "biz": "MzA5NDAxMDIzOA=="}, {"mid": 50327, "mp_name": "V\\u4f20\\u5a92", "wxid": "rbcyjzx01", "desc": "\\u5317\\u4eac\\u4eba\\u6c11\\u5e7f\\u64ad\\u7535\\u53f0-\\u5e7f\\u64ad\\u53d1\\u5c55\\u7814\\u7a76\\u4e2d\\u5fc3\\u7684\\u5b98\\u65b9\\u53f7\\uff1a\\u4e00\\u4e2a\\u4e0d\\u5173\\u6ce8\\u4f20\\u5a92\\u5708\\u7684\\u7814\\u7a76\\u5458\\u4e0d\\u662f\\u597d\\u5e7f\\u64ad\\u4eba~ \\u5408\\u4f5c\\u8bf7\\u8054\\u7cfb\\uff1a 010-65157248/010-65158364", "tag": [], "avatar": "https://dajiala.oss-cn-hangzhou.aliyuncs.com/mp_avatar/aa29dbded01f33b7bc0babdf7f5a7da4.jpg", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 68396, "avg_top_read": 886, "avg_top_praise": 19, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 0, "dajiala_index": 0.62, "ghid": "", "area": "", "register": "2014-07-01", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_bf4ec3152728", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 59, "original_count": 0, "webtask_count": 0, "lastest_publish": "2022-08-01 16:47", "high_title": "", "high_desc": "", "total_monitoring": 0, "register_time": "2014-07-01", "create_time": "2019-12-12 23:38:17", "biz": "MzA4OTg3ODAwOA=="}, {"mid": 78639, "mp_name": "\\u5403\\u559d\\u73a9\\u4e50\\u5927\\u641c\\u7d22", "wxid": "chwl876", "desc": "\\u5317\\u4eac\\u7535\\u53f0FM876\\u300a\\u5403\\u559d\\u73a9\\u4e50\\u5927\\u641c\\u7d22\\u300b\\u8282\\u76ee\\u5b98\\u65b9\\u5fae\\u4fe1\\u516c\\u4f17\\u53f7\\u3002\\u6211\\u4eec\\u7684\\u76ee\\u6807\\u662f\\u8ba9\\u6bcf\\u4e00\\u4f4d\\u542c\\u4f17\\u90fd\\u80fd\\u5403\\u5f97\\u5c3d\\u5174\\uff0c\\u73a9\\u7684\\u7cbe\\u5f69\\u3002", "tag": [], "avatar": "https://dajiala.oss-cn-hangzhou.aliyuncs.com/mp_avatar/2afd1ec0f9df7e2fd3962f7942efe497.jpg", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 273843, "avg_top_read": 7973, "avg_top_praise": 4, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 6, "dajiala_index": 2.72, "ghid": "", "area": "", "register": "2014-04-25", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_0153e9caf72c", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 288, "original_count": 0, "webtask_count": 0, "lastest_publish": "2022-07-27 17:00", "high_title": "", "high_desc": "", "total_monitoring": 0, "register_time": "2014-04-25", "create_time": "2019-12-13 00:32:54", "biz": "MzA3ODYwMjczMA=="}, {"mid": 50247, "mp_name": "\\u95ee\\u5317\\u4eac", "wxid": "xinwenrexian65159063", "desc": "\\u6765\\u81ea\\u5317\\u4eac\\u65b0\\u95fb\\u5e7f\\u64ad\\u7684\\u72ec\\u5bb6\\u8c03\\u67e5\\u62a5\\u9053\\u3002", "tag": [], "avatar": "http://mmbiz.qpic.cn/sz_mmbiz_png/HicWG2hzvehOKPlKg0Kib2ZyHiayxjgOscvfxq2aRz9r6ozX5jgdeQJNehVic6J7MgnfvLNOeNwMLREa08roPEbGXQ/0?wx_fmt=png", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 261634, "avg_top_read": 5774, "avg_top_praise": 32, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 14, "dajiala_index": 27.79, "ghid": "", "area": "", "register": "2014-12-02", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_3016d338ca59", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 411, "original_count": 0, "webtask_count": 1, "lastest_publish": "2022-08-25 18:00", "high_title": "", "high_desc": "", "total_monitoring": 7, "register_time": "2014-12-02", "create_time": "2019-08-05 10:43:02", "biz": "MzA5MjEyMDA5MQ=="}, {"mid": 554736, "mp_name": "\\u7231\\u8f661039", "wxid": "ACFM1039", "desc": "\\u5317\\u4eac\\u4ea4\\u901a\\u5e7f\\u64adFM103.9\\u6c7d\\u8f66\\u680f\\u76ee\\u552f\\u4e00\\u5b98\\u65b9\\u4e92\\u52a8\\u5e73\\u53f0\\u3002", "tag": [], "avatar": "http://mmbiz.qpic.cn/mmbiz_png/8PuWmwMZmmhfQgBam7OZXYJMf9S7ic1KiafXyks2cJpiaVVXh9hibFiazPWmiaB88D4qlU3RaFSaEusS3kpgSch4bG0Q/0?wx_fmt=png", "account_type": 200, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 358466, "avg_top_read": 9245, "avg_top_praise": 20, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 21, "dajiala_index": 38.95, "ghid": "", "area": "", "register": "2016-07-06", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_bd967b061b4d", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 232, "original_count": 0, "webtask_count": 1, "lastest_publish": "2022-08-26 12:38", "high_title": "", "high_desc": "", "total_monitoring": 13, "register_time": "2016-07-06", "create_time": "2019-12-13 09:18:56", "biz": "MzIyNTQ3Nzg3Nw=="}, {"mid": 469025, "mp_name": "BRTV\\u4eac\\u57ce\\u7f8e\\u98df\\u5730\\u56fe", "wxid": "meishiditu-btv", "desc": "\\u751f\\u6d3b\\u670d\\u52a1", "tag": [], "avatar": "http://mmbiz.qpic.cn/mmbiz_png/GrxdWe8zv8S8xNYtEBhxGvtgr2NrL5SF5ednv6IWEBU3MRrfXDtoC4S1xLniae2352A2UMT1zcvQSMv5svoDWhg/0?wx_fmt=png", "account_type": 100, "zhuti": "\\u5317\\u4eac\\u5e7f\\u64ad\\u7535\\u89c6\\u53f0", "fans": 178693, "avg_top_read": 4215, "avg_top_praise": 17, "area_id": "", "age": [], "original_index": 0.0, "week_articles": 6, "dajiala_index": 4.6, "ghid": "", "area": "", "register": "2014-10-13", "industry": "", "same_owner": 0, "have_owner": false, "is_avatar": true, "is_favorite": 0, "favorite_num": 0, "qrcode": "https://open.weixin.qq.com/qr/code?username=gh_fc7245709bfa", "owner_id": 1504790, "mini_count": 0, "mp_fetch_sum": 129, "original_count": 0, "webtask_count": 1, "lastest_publish": "2022-08-24 20:00", "high_title": "", "high_desc": "", "total_monitoring": 1, "register_time": "2014-10-13", "create_time": "2019-12-13 08:09:31", "biz": "MjM5MDg0NDA5NQ=="}]}}\n'
    resp = Response('', None, payload)
    cfg = {
        'type': 'more',
        'map': {
            'username': 'qrcode:username=(gh_.*?)([^a-z0-9]|$):1',
            'nickname': 'mp_name',
            'aliasname': 'wxid',
            'register_body': 'zhuti',
            'signature': 'desc',
            #'head_img': 'avatar:fileb64e',
            'head_img': 'avatar',
            'doc_id': 'biz:b64d'
        },
        'item': 'data.accounts',
        'add': {
            'type': 'wechat_oaccount',
            'appid': ''
        }
    }
    print(json.dumps(cfg))
    req = Request('', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47'})
    print(asyncio.run(match(cfg, req, resp)))
    
