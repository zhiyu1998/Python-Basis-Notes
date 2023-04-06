#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/11/21/0021 下午 23:59
# @Author  : zhiyu1998

import json
import os.path
import re
import time
import random
import logging

import pandas as pd
import requests

from bs4 import BeautifulSoup

# 头请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36',
    'Reference': 'https://www.letpub.com/journalapp/',
}
# 排除名单
exclude_list = ['arXiv']


def logger_config(log_path, logging_name):
    """
    配置log
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    """
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger


logger = logger_config(log_path='log.txt', logging_name='日志')


def extra_title_journal() -> pd.DataFrame:
    """
    提取论文标题和会议/期刊
    :return:
    """
    res: pd.DataFrame = pd.DataFrame(columns=['title', 'journal'])
    with open("ref.bib") as f:
        temp = []
        for line in f:
            if 'title' in line:
                temp.append(re.findall(r'({.*?})', line)[0].replace('{', '').replace('}', ''))
            if 'journal' in line or 'booktitle' in line:
                temp.append(re.findall(r'({.*?})', line)[0].replace('{', '').replace('}', ''))
            if line == '\n':
                # 校准
                if len(temp) > 2:
                    temp.pop(2)
                # 补全
                if len(temp) < 2:
                    temp.append(' ')
                res.loc[len(res)] = temp
                temp.clear()
    return res


def save_excel(res: pd.DataFrame) -> None:
    """
    保存为excel
    :param res:
    :return:
    """
    if os.path.exists('./ref.xlsx'):
        os.remove('./ref.xlsx')
    res.to_excel('ref.xlsx', index=False)


def get_msg_from_letpub(journal_name: str) -> list:
    """
    从letpub获取期刊数据
    :return: ISSN 期刊名 期刊指标 中科院分区 学科领域 SCI/SCIE 是否OA 录用比例 审稿周期 近期文章 查看数
    """
    url: str = f'https://www.letpub.com.cn/journalappAjaxXS.php?querytype=autojournal&term={journal_name}'
    r: requests.Response = requests.get(url=url, headers=headers)
    # 提取精准匹配的结果 -- [0]
    try:
        issn: str = json.loads(r.text)[0]['issn']
        if issn == '':
            return []
    except Exception as e:
        logger.info(f'请求错误：{e}')
        return []
    # 请求信息
    postUrl: str = 'https://www.letpub.com.cn/index.php?page=journalapp&view=search'
    request_params: dict = {
        "searchname": "",
        "searchissn": issn,
        "searchfield": "",
        "searchimpactlow": "",
        "searchimpacthigh": "",
        "searchscitype": "",
        "view": "search",
        "searchcategory1": "",
        "searchcategory2": "",
        "searchjcrkind": "",
        "searchopenaccess": "",
        "searchsort": "relevance"
    }
    # 二次请求查询更快
    r2: requests.Response = requests.post(url=postUrl, headers=headers, data=request_params)
    # 爬取信息
    soup = BeautifulSoup(r2.text, 'lxml')
    td = soup.find_all('td', attrs={
        'style': 'border:1px #DDD solid; border-collapse:collapse; text-align:left; padding:8px 8px 8px 8px;'})
    temp_letpub_data = [d.text for d in td]
    return temp_letpub_data


def insert_sci_msg(payload: pd.DataFrame) -> pd.DataFrame:
    """
        获取SCI信息
    :return:
    """
    res_dict: dict = {}
    # 遍历每个期刊
    for line in payload.loc[:, 'journal']:
        # TODO: 排除不想查询的 (line in exclude_list or)
        if line.isspace():
            continue
        journal_data = get_msg_from_letpub(line)
        # 爬取结果判空
        if len(journal_data) == 0:
            continue
        res_dict[line] = journal_data
        time.sleep(round(random.uniform(0, 1), 2))
    # 增加期刊的列
    payload_res: pd.DataFrame = payload.assign(issn='', journal_name='', target='', area='', field='', sci='', is_oa='',
                                               employment_ratio='',
                                               review_cycle='', recent='', view='')
    # 把爬取的数据填充进去
    for index, row in payload_res.iterrows():
        print(f'已解决：{row["title"]}')
        if row['journal'] in res_dict:
            '''
                0-ISSN
                1-期刊名
                2-期刊指标
                3-中科院分区
                4-学科领域 
                5-SCI/SCIE 
                6-是否OA 
                7-录用比例
                8-审稿周期
                9-近期文章
                10-查看数
            '''
            match_item = res_dict[row['journal']]
            row['issn'] = match_item[0]
            row['journal_name'] = match_item[1]
            row['target'] = match_item[2]
            row['area'] = match_item[3]
            row['field'] = match_item[4]
            row['sci'] = match_item[5]
            row['is_oa'] = match_item[6]
            row['employment_ratio'] = match_item[7]
            row['review_cycle'] = match_item[8]
            row['recent'] = match_item[9]
            row['view'] = match_item[10]
            payload_res.iloc[index] = row
    return payload_res


if __name__ == '__main__':
    start = time.time()
    # 提取论文名/期刊
    res: pd.DataFrame = extra_title_journal()
    # 获取期刊信息
    sci_res: pd.DataFrame = insert_sci_msg(res)
    # 保存EXCEL
    save_excel(sci_res)
    print(f"耗时：{time.time() - start:.2f}秒")
