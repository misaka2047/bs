import urllib.request, urllib.error
from bs4 import BeautifulSoup
import re
import xlwt
import json
import pandas as pd
from datetime import datetime
import urllib.parse

keyword = "iphone12"

# 对 keyword 进行 URL 编码
encoded_keyword = urllib.parse.quote(keyword)

# 定义基础url，发现规律，每页最后变动的是start=后面的数字
baseurl = "https://re.jd.com/search?keyword=" + encoded_keyword + "&enc=utf-8"
 
 
# 定义一个函数getHtmlByURL,得到指定url网页的内容
def geturl(url):
    # 自定义headers(伪装，告诉服务器，我们是什么类型的机器,以免被反爬虫)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    # 利用Request类来构造自定义头的请求
    req = urllib.request.Request(url, headers=headers)
    # 定义一个接收变量，用于接收
    html = ""
    try:
        # urlopen()方法的参数，发送给服务器并接收响应
        resp = urllib.request.urlopen(req)
        # urlopen()获取页面内容，返回的数据格式为bytes类型，需要decode()解码，转换成str类型
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
    # 指定解析器解析html,得到BeautifulSoup对象
    soup = BeautifulSoup(html, "html5lib")
    
    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 找到包含商品信息的<script>标签
    script_tag = soup.find('script', type='text/javascript', string=lambda text: text and 'var pageData =' in text)

    if script_tag:
        # 提取 JavaScript 代码
        script_content = script_tag.string
        # 找到 JSON 数据部分
        json_data = script_content.split('var pageData =', 1)[1].split('};', 1)[0] + '}'
        
        # 解析 JSON 数据
        product_data = json.loads(json_data)
        
        # 筛选商品信息
        filtered_products = []
        prices = []
        for product in product_data['result']:
            price = product.get('price')
            if price is not None and price != '':
                price = float(price)  # 转换为浮点数
                filtered_products.append({
                    'platform': 'JD',
                    'gid': product.get('sku_id'),
                    'title': product.get('ad_title'),
                    'imgurl': "https://img13.360buyimg.com/cms/" + product.get('image_url'),
                    'clickurl': product.get('click_url'),
                    'price': str(price) #转为字符串
                })
                prices.append(price)
        
        # 计算去除最贵和最便宜的三个商品后的平均价格
        if len(prices) > 6:  # 确保有足够的数据点
            prices.sort()
            trimmed_prices = prices[3:-3]  # 去除最便宜的三个和最贵的三个
            average_price = sum(trimmed_prices) / len(trimmed_prices)
        else:
            average_price = sum(prices) / len(prices) if prices else 0

        # 创建 DataFrame
        df = pd.DataFrame(filtered_products)
        
        # 输出到 Excel 文件
        '''excel_filename = f'商品信息_{timestamp}.xlsx'
        df.to_excel(excel_filename, index=False)'''

        # 输出到 JSON 文件
        '''json_filename = f'商品信息_{timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(filtered_products, json_file, ensure_ascii=False, indent=4)'''
        
        # 输出平均价格
        '''print(f"商品信息已输出到 '{excel_filename}' 和 '{json_filename}'")
        print(f"去除最贵和最便宜的商品后的平均价格: {average_price:.2f} 元")'''
    else:
        print("未找到包含商品信息的<script>标签。")
    return filtered_products
 
 
def main():
    analysisData(baseurl)
 
if __name__ == "__main__":
    main()