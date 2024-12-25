import urllib.request, urllib.error
from bs4 import BeautifulSoup
import re
import xlwt
import json
import pandas as pd
from datetime import datetime
import urllib.parse
import os

keyword = "摄像头"

# 对 keyword 进行 URL 编码
encoded_keyword = urllib.parse.quote(keyword)

# 定义基础url
baseurl = "https://m.suning.com/search/" + encoded_keyword + "/"
 
# 定义一个函数getHtmlByURL,得到指定url网页的内容
def geturl(url):
    # 自定义headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    html = ""
    try:
        resp = urllib.request.urlopen(req)
        html = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html
 
# 定义一个函数，并解析这个网页
def analysisData(url):
    # 获取指定网页
    html = geturl(url)
    soup = BeautifulSoup(html, "html5lib")
    # print(soup)
    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 存储所有商品信息的列表
    data_list = []
    
    # 找到包含商品信息的<script>标签
    script_tag = soup.find('script', string=lambda text: text and 'var partnumber = ' in text)

    if script_tag:
        script_content = script_tag.string
        # 提取 partnumbers
        partnumbers = re.findall(r'var partnumber = "(\d+)"\+ "_" \+ "(\d+)";', script_content)
        # 遍历所有 partnumber
        for i in range(len(partnumbers)):
            # 构建价格查询URL
            priceurl = "https://ds.suning.com/ds/generalForTile/0000000"+ partnumbers[i][0] +"-025-2-"+ partnumbers[i][1] +"-1--"
            phtml = geturl(priceurl)
            pjson = json.loads(phtml).get('rs')
            ppjson = pjson[0].get('price')
            # 构建商品URL
            goodurl = "https://m.suning.com/product/"+ partnumbers[i][1] +"/"+ partnumbers[i][0] +".html"
            ghtml = geturl(goodurl)
            gsoup = BeautifulSoup(ghtml, "html5lib")
            # 提取标题
            title_tag = gsoup.find("title")
            title = title_tag.string if title_tag else "无标题"
            # 提取图片URL
            img_tag = gsoup.find("img")
            img_url = img_tag["src"] if img_tag else "无图片"
            # 将信息保存到字典
            data = {
                'platform': 'Suning',
                'gid': partnumbers[i][0] + "_" + partnumbers[i][1],
                "title": title,
                "imgurl": img_url,
                "clickurl": goodurl,
                "price": ppjson 
            }
            # 添加到列表
            data_list.append(data)
        # 定义文件名
        filename = f"./sn_{keyword}{timestamp}.json"
        # 将列表写入 JSON 文件
        '''with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)
        print(f"数据已保存到 {filename}")'''
    else:
        print("未找到包含商品信息的<script>标签。")
    return data_list
 
def main():
    analysisData(baseurl)
 
if __name__ == "__main__":
    main()