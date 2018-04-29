#!/usr/bin/env python
# encoding: utf-8

# from bs4 import BeautifulSoup
import json
from urllib import request
import settings
from psycopg2.extensions import AsIs
import psycopg2


"""
@author: Fabrice Zhang 
@file: rank
@time: 2018/4/16 下午8:20
"""


def run():
    # DB Connection
    conn = psycopg2.connect(
        database=settings.database,
        user=settings.user,
        password=settings.password,
        host=settings.host,
        port=settings.port)

    url = "https://www.panda.tv/live_lists?" \
          "status=2&token=97b0ad869a3fa010c97f1da5c066536e&" \
          "pageno=1" \
          "&pagenum=120&order=top&_=1523889862949"

    header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
        'cookie': 'webp=1; __guid=96554777.2603765222669492700.1523802427129.9802; '
                  'pdft=20180415222707fc74e8f465d496cb0982e7c33afa8a5f003a0503676e18c1; '
                  'smidV9=20180415222707fc74e8f465d496cb0982e7c33afa8a5f003a0503676e18c1; '
                  'I=r%3D84823014%26t%3D97b0ad869a3fa010c97f1da5c066536e; '
                  'R=r%3D84823014%26u%3DCnaqnGi84823014%26n%3D%25R7%2586%258N%25R7%258P%25NO%'
                  '25R6%2590%259R%25R7%25NP%2591%25R5%258S%25O7%26le%3D%26m%3D%26im%3DnUE0pPH'
                  'mDFHlEvHlEzx3YaOxnJ0hM3ZyZxLjZwH3ZQDjZmtjLzD3MQV5ATR4ZQR3AGZlLmN3MGZ5Lv5dp'
                  'Tp%3D%26p%3D%26i%3D; M=t%3D1523880252%26v%3D1.0%26mt%3D%26s%3D29d324c600b4'
                  'a60b8ac375218007b987%26ps%3Df3df733bf2291e86c297bf0eebe14462; pdftv1=e1b86'
                  '|162ce5755b8|2306|dddb9405|d; Hm_lvt_204071a8b1d0b2a04c782c44b88eb996=1523'
                  '802427,1523880253; GED_PLAYLIST_ACTIVITY=W3sidSI6ImJWWE0iLCJ0c2wiOjE1MjM4O'
                  'DI4MDcsIm52IjoxLCJ1cHQiOjE1MjM4ODI3NjAsImx0IjoxNTIzODgyODA3fV0.; monitor_c'
                  'ount=22; Hm_lpvt_204071a8b1d0b2a04c782c44b88eb996=1523889864',
        'Referer': 'https://www.panda.tv/all?pdt=1.18.pheader-n.1.79ldqpffdse',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ja;q=0.4'
    }

    rq = request.Request(url, headers=header)
    html = request.urlopen(rq)
    # bs = BeautifulSoup(html.read(), "html.parser")
    # print(bs)
    res = html.read()
    res_json = json.loads(res)

    for item in res_json['data']['items']:
        data = build_room_record(item)
        insert_into_db(conn, settings.host_record, data)


def build_room_record(item):
    data = {
        'room_id': item['id'],
        'person_num': item['person_num'],
        'classification': item['classification']['ename'],
        'user_id': item['userinfo']['rid']
    }

    return data


def insert_into_db(conn, table_name, data):
    insert_sql = 'insert into %s %%s values %%s' % table_name

    keys = '('
    for key in data.keys():
        keys = keys + key + ','
    keys = keys[:len(keys)-1] + ')'
    # print(insert_sql % (keys, tuple(data.values())))
    try:
        with conn.cursor() as cur:
            cur.execute(insert_sql % (keys, tuple(data.values())))
            conn.commit()
    except Exception as err:
        print(err)


if __name__ == "__main__":
    run()
