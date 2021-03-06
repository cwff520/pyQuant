# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 23:11:16 2018

@author: CS
"""

import urllib.request
from bs4 import BeautifulSoup
import re
#import pandas as pd
import time
#import os
import csv
#import pymysql
import requests


#定义读取整个网页的函数
def get_html(url):
    #获取请求头，以浏览器身份查看网页信息
    headers = ("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36")
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    html = opener.open(url).read()
    html = html.decode("gbk","ignore")
    return html


def get_stockcode(html):
    #利用正则表达式定位股票代码
    pat = '<a target="_blank" href="http://quote.eastmoney.com/\S\S(.*?).html">'
    #根据正则表达式的定位爬取所有股票代码
    code = re.compile(pat).findall(html)
    return code


#定义一个爬虫函数，锁定网易财经网页中股票数据的具体位置
def crawl_stockdata(code,year,season):
    #将网址中自变量设置为str类型
    #code = str(code)
    year = str(year)
    season = str(season)
    #网易财经的URL形式
    dataUrl = 'http://quotes.money.163.com/trade/lsjysj_'+code+'.html?year='+year+'&season='+season
    #获取网易财经的整版网页
    #stockdata = get_html(dataUrl)
    stockdata = requests.get(dataUrl)
    #利用BeautiSoup库将HTML文档格式化
    soup = BeautifulSoup(stockdata.text,'lxml')
    #利用BeautiSoup库中的find_all(div,attr)函数定位到股票数据的表格
    table = soup.find_all('table',{'class':'table_bg001'})[0]
    #从大表格中具体定位到<tr></tr>标签下的11个股票数据
    rows = table.find_all('tr')
    return rows[::-1]


'''定义一个写入csv文件的函数，所有股票代码已经通过正则表达式从东方财经爬取，
而一年只有四个季度，后来又发现随便输入一个年份网页不会报错，仅仅显示没有数据，
不妨从1991年开始爬取，表格中数据为空则跳过对应年份的网页接着爬'''
def writeCsv(code):
    #code = str(code)
    #csvFile = open('E:\\symbols\\' + code + '.csv','wb')   wb 是python 2.*的写法，在3.*里面貌似要报错
    csvFile = open('E:\\symbols\\' + code + '.csv','w', newline = '')
    writer = csv.writer(csvFile)
    writer.writerow(('日期','开盘价','最高价','最低价','收盘价','涨跌额','涨跌幅','成交量','成交额','振幅','换手率'))
    try:
        #遍历1991年到2018年的URL
        for i in range(1991,2019):
            #遍历每个年份1季度到4季度的URL
            for j in range(1,5):
                #调用定位具体股票数据位置的函数
                rows = crawl_stockdata(code,i,j)
                #将<table></table>标签中的11个数据写入csv文件中
                for row in rows:
                    csvRow = []
                    if row.find_all('td') != []:
                        for cell in row.find_all('td'):
                            csvRow.append(cell.get_text().replace(',',''))
                        if csvRow != []:
                            writer.writerow(csvRow)
                time.sleep(2)#睡眠2秒
    except:
        #如果爬虫失败则抛出异常
        print("crawling goes wrong.")
    finally:
        csvFile.close()

#主函数
if __name__ == '__main__':
    #东方财富网所有股票代码的URL
    codeUrl = 'http://quote.eastmoney.com/stocklist.html'
    #调用上述函数获取所有股票代码
    code = get_stockcode(get_html(codeUrl))
    codeList = []#创建一个存储所有股票代码的列表
    
    #遍历所有股票代码中的个股，取出其中的深沪，创业板，中小板股票代码
    # 这段代码可以考虑更新，应该一句就可以搞定的，至少可以“与”起来
    for single in code:
        if single[0] == '0':
            codeList.append(single)
        if single[0] == '3':
            codeList.append(single)
        if single[0] == '6':
            codeList.append(single)
    #遍历集合中每一个股票代码,将对应数据爬取到csv文件中
    for s in codeList:
        time_start = time.time()
        writeCsv(s)
        print('Time spent on stock '+s+' is %d sec.' % (time.time()-time_start))






































