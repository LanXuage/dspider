#!/bin/env python3
import asyncio
import logging
import asyncpg
import logging

log = logging.getLogger(__name__)

async def export(cfg : dict, result : dict):
    print(cfg)
    print(result)
    try:
        conn : asyncpg.Pool = cfg.get('conn')
        unique_fields = cfg.get('unique_fields')
        table_name = cfg.get('table_name')
        pkey_name = cfg.get('pkey_name')
        async with conn.acquire() as c:
            await process(c, table_name, unique_fields, pkey_name, result)
    except Exception as e:
        log.error(e, exc_info=True)

async def get_ids(c, table_name, unique_fields, pkey_name, result):
    sql = 'SELECT "' + pkey_name + '" FROM "' + table_name + '" WHERE "'
    for k in unique_fields:
        v = result.get(k)
        sql += k + '" = '
        if isinstance(v, str):
            sql += '\'' + v + '\' and "'
        elif isinstance(v, int):
            sql += v + ' and "'
    sql = sql[:-6]
    if len(unique_fields) == 0:
        sql = sql[:-2]
    print(sql)
    return await c.fetch(sql)

async def process(c, table_name, unique_fields, pkey_name, result):
    async with c.transaction():
        r = await get_ids(c, table_name, unique_fields, pkey_name, result)
        if len(r) == 0:
            fks = []
            sql = 'INSERT INTO "' + table_name + '" ("'
            keys = []
            for k in result.keys():
                v = result.get(k)
                keys.append(k)
                if isinstance(v, dict) and v.get('type') == 'more':
                    continue
                sql += k + '", "'
            sql = sql[:-3] + ') VALUES ('
            for k in keys:
                v = result.get(k)
                if isinstance(v, str):
                    sql += '\'' + v + '\', '
                elif isinstance(v, int):
                    sql += v + ', '
                elif isinstance(v, dict):
                    ufs = v.get('unique_fields')
                    if not ufs:
                        ufs = []
                    pkn = v.get('pkey_name')
                    t = v.get('type')
                    tn = v.get('table_name')
                    if t == 'one':
                        v = await process(c, tn, ufs, pkn, v.get('result'))
                        sql += v + ', '
                    elif t == 'more':
                        fkns = []
                        mfkn = v.get('mfkey_name')
                        mtn = v.get('map_table_name')
                        for r in v.get('result'):
                            fkns.append(await process(c, tn, ufs, pkn, r))
                        fks.append({'fk_name': k, 'mfk_name': mfkn, 'results': fkns, 'map_table_name': mtn})
            sql = sql[:-2] + ')'
            print(sql)
            await c.execute(sql)
            r = await get_ids(c, table_name, unique_fields, pkey_name, result)
            for i in fks:
                sql = 'INSERT INTO "' + i.get('map_table_name') + '" ("' + i.get('fk_name') + '", "' + i.get('mfk_name') + '") VALUES ('
                if isinstance(r[0], str):
                    sql += '\'' + r[0] + '\', '
                else:
                    sql += r[0] + ', '
                for j in i.get('results'):
                    if isinstance(j, str):
                        n_sql = sql + '\'' + j + '\')'
                    else:
                        n_sql = sql + j + ')'
                    print(n_sql)
                    await c.execute(n_sql)
        return r[0]


async def test():
    results = [{'username': 'gh_406cd9af657e', 'nickname': '北京新闻', 'aliasname': 'brtvbjxw', 'register_body': '北京广播电视台', 'signature': '聚焦北京的新闻，着力报道热点民生；关心北京的事儿，时常发布实用信息；专注北京的生活，不断发放大小福利。无论是否身在北京，您需要来自北京的新闻！', 'head_img': 'http://mmbiz.qpic.cn/mmbiz_png/LCChw9N6UicdRoeibDg82mPebcm46nq9ian3CpoDHLsqLKajT6uNyC7UyuibwzQZpjNA377IqInO1bthpGsnzAuCJA/0?wx_fmt=png', 'doc_id': '3079855037', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_af6012b4b6ea', 'nickname': '北京卫视养生堂', 'aliasname': 'btv_yangshengtang', 'register_body': '北京广播电视台', 'signature': '北京卫视《养生堂》，传递健康养生知识~', 'head_img': 'http://mmbiz.qpic.cn/mmbiz_png/iac0vE8Nzz4DibzR2GjVIUbvibV8Z7e0Iq7rce7b2e3hpj8I2P6vNFHCzCeXtCAV19ZEQVT0Cxib4IMquNWs2Z1icqA/0?wx_fmt=png', 'doc_id': '3009074626', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_7b9210bbc578', 'nickname': '暖暖的味道官微', 'aliasname': 'btvjiadeweidao', 'register_body': '北京广播电视台', 'signature': '每天教您一道大厨家常菜！愿你在轻松愉快的氛围中学习烹饪技巧、生活窍门、养生知识。节目播出时间周一到周六17:10，公众号16:00抢先知晓节目内容+预告，参与互动更有免费试吃哦~', 'head_img': 'http://mmbiz.qpic.cn/mmbiz_png/QDTa3lHem03f0KrP3I3HKNzHh4POdhZgcFWbRCy3z4H9WiadjrGdibQicOywGP1KibGNCW7jj3Ac38MFzxIiatXeu8g/0?wx_fmt=png', 'doc_id': '3081538246', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_302cd8838455', 'nickname': '英语PK台', 'aliasname': 'goingforgold774', 'register_body': '北京广播电视台', 'signature': '【北京外语广播王牌教学栏目】一档以培养实用英语技能（流利听说）为特色的轻娱乐式广播英语教学节目。荣获“新浪声动中国—最受欢迎外语类节目”。公益教学第十年，带领学习者攻克英语，连接世界，启发心智，提升人生。', 'head_img': 'http://mmbiz.qpic.cn/mmbiz_png/FhZAMVUpfUh83BqUx7bL86OxJCxI6ERE6ia5Zbniaebvs8JIzWaBoCoDnnnxtO9h2uPm9cgKPVT8JN5ONWvf6QnA/0?wx_fmt=png', 'doc_id': '3079401007', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_f7ff268f3d09', 'nickname': '北京交通广播', 'aliasname': 'jtgbfm1039', 'register_body': '北京广播电视台', 'signature': '北京交通广播，让你的出行更轻松！', 'head_img': 'http://mmbiz.qpic.cn/sz_mmbiz_png/wSf4PzRytP1ia17xoyfoakqKUUVuED5YXvaIlibMn5jBEiczOosB5eiaKgAgXOxQVC8MJaU7H8L3IvSYffaGYjqOIQ/0?wx_fmt=png', 'doc_id': '3094010238', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_bf4ec3152728', 'nickname': 'V传媒', 'aliasname': 'rbcyjzx01', 'register_body': '北京广播电视台', 'signature': '北京人民广播电台-广播发展研究中心的官方号：一个不关注传媒圈的研究员不是好广播人~ 合作请联系： 010-65157248/010-65158364', 'head_img': 'https://dajiala.oss-cn-hangzhou.aliyuncs.com/mp_avatar/aa29dbded01f33b7bc0babdf7f5a7da4.jpg', 'doc_id': '3089878008', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_0153e9caf72c', 'nickname': '吃喝玩乐大搜索', 'aliasname': 'chwl876', 'register_body': '北京广播电视台', 'signature': '北京电台FM876《吃喝玩乐大搜索》节目官方微信公众号。我们的目标是让每一位听众都能吃得尽兴，玩的精彩。', 'head_img': 'https://dajiala.oss-cn-hangzhou.aliyuncs.com/mp_avatar/2afd1ec0f9df7e2fd3962f7942efe497.jpg', 'doc_id': '3078602730', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_3016d338ca59', 'nickname': '问北京', 'aliasname': 'xinwenrexian65159063', 'register_body': '北京广播电视台', 'signature': '来自北京新闻广播的独家调查报道。', 'head_img': 'http://mmbiz.qpic.cn/sz_mmbiz_png/HicWG2hzvehOKPlKg0Kib2ZyHiayxjgOscvfxq2aRz9r6ozX5jgdeQJNehVic6J7MgnfvLNOeNwMLREa08roPEbGXQ/0?wx_fmt=png', 'doc_id': '3092120091', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_bd967b061b4d', 'nickname': '爱车1039', 'aliasname': 'ACFM1039', 'register_body': '北京广播电视台', 'signature': '北京交通广播FM103.9汽车栏目唯一官方互动平台。', 'head_img': 'http://mmbiz.qpic.cn/mmbiz_png/8PuWmwMZmmhfQgBam7OZXYJMf9S7ic1KiafXyks2cJpiaVVXh9hibFiazPWmiaB88D4qlU3RaFSaEusS3kpgSch4bG0Q/0?wx_fmt=png', 'doc_id': '3225477877', 'type': 'wechat_oaccount', 'appid': ''}, {'username': 'gh_fc7245709bfa', 'nickname': 'BRTV京城美食地图', 'aliasname': 'meishiditu-btv', 'register_body': '北京广播电视台', 'signature': '生活服务', 'head_img': 'http://mmbiz.qpic.cn/mmbiz_png/GrxdWe8zv8S8xNYtEBhxGvtgr2NrL5SF5ednv6IWEBU3MRrfXDtoC4S1xLniae2352A2UMT1zcvQSMv5svoDWhg/0?wx_fmt=png', 'doc_id': '2390844095', 'type': 'wechat_oaccount', 'appid': ''}]
    conn = await asyncpg.create_pool('postgres://postgres:7URL8rCIbJNNKq@localhost:65432/dstest')
    cfg = {
        'conn': conn,
        'unique_fields': ['username'],
        'table_name': 'vrp_oasa_data',
        'pkey_name': 'id'
    }
    for result in results:
        print(await export(cfg, result))

if __name__ == '__main__':
    asyncio.run(test())