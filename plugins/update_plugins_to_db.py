#!/bin/env python3
import os
import asyncio
import asyncpg

from datetime import datetime
from crc import Crc64, CrcCalculator


def remove_other(plugins):
    try:
        plugins.remove('__init__.py')
        plugins.remove('__pycache__')
    except:
        pass
    return plugins


async def update_to_db(plugins):
    pg_conn = await asyncpg.connect(user='postgres', password='7URL8rCIbJNNKq', database='dspider', host='127.0.0.1', port=65432)
    for p in plugins:
        async with pg_conn.transaction():
            rs = await pg_conn.fetch('SELECT 1 FROM ds_plugin WHERE id = $1', p.get('id'))
            if len(rs) == 0:
                await pg_conn.execute('INSERT INTO ds_plugin(id, plugin_name, plugin_type, plugin_plain, code_obj, update_time, create_time, code_obj_version) VALUES($1, $2, $3, $4, $5, $6, $7, $8)', p.get('id'), p.get('plugin_name'), p.get('plugin_type'), p.get('plugin_plain'), p.get('code_obj'), p.get('update_time'), p.get('create_time'), p.get('code_obj_version'))


async def update():
    exporters_dir = './plugins/exporters'
    generators_dir = './plugins/generators'
    matchers_dir = './plugins/matchers'
    plugins = []
    exporters = remove_other(os.listdir(exporters_dir))
    t = datetime.now().astimezone()
    c = CrcCalculator(Crc64.CRC64)
    for e in exporters:
        with open(exporters_dir + '/' + e, 'r') as f:
            data = f.read()
            plugins.append({
                'id': '{:0>16s}'.format(hex(c.calculate_checksum(data.encode()))[2:]),
                'plugin_name': e,
                'plugin_type': 2,
                'plugin_plain': data,
                'code_obj': b'',
                'update_time': t,
                'create_time': t,
                'code_obj_version': ''
            })
    generators = remove_other(os.listdir(generators_dir))
    for e in generators:
        with open(generators_dir + '/' + e, 'r') as f:
            data = f.read()
            plugins.append({
                'id': '{:0>16s}'.format(hex(c.calculate_checksum(data.encode()))[2:]),
                'plugin_name': e,
                'plugin_type': 0,
                'plugin_plain': data,
                'code_obj': b'',
                'update_time': t,
                'create_time': t,
                'code_obj_version': ''
            })
    matchers = remove_other(os.listdir(matchers_dir))
    for e in matchers:
        with open(matchers_dir + '/' + e, 'r') as f:
            data = f.read()
            plugins.append({
                'id': '{:0>16s}'.format(hex(c.calculate_checksum(data.encode()))[2:]),
                'plugin_name': e,
                'plugin_type': 1,
                'plugin_plain': data,
                'code_obj': b'',
                'update_time': t,
                'create_time': t,
                'code_obj_version': ''
            })
    await update_to_db(plugins)


if __name__ == '__main__':
    asyncio.run(update())
