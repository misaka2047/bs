---

template: report
type: 实验报告
title: 2024fall B/S体系软件设计 课程任务设计文档
name: 魏源
id: 3220101787
course: B/S体系软件设计
major: 计算机科学与技术
college: 浙江大学
schedule: 周五3，4节
instructor: 胡晓军
lab_date: 2024/11/11
---

## 设计目标

<b>需要实现的基本功能如下：</b>

- 1. 实现用户注册、登录功能，用户注册时需要填写必要的信息并验证，如用户名、密码要
      求在6 字节以上，email 的格式验证，并保证用户名和email 在系统中唯一，用户登录后
      可以进行以下操作。 
  
- 2. 通过商品名称在主流电商平台上查询该商品实时价格 
	- i. 商品名称建议分词处理优化查询；
	-  ii. 查询多个结果的处理 
	-  iii. 很多平台需要平台用户登录验证后才可以进行查询 
	
- 3. 支持至少2 个以上平台查询价格进行比较（淘宝、京东等）。 

- 4. 建立商品库，将商品信息和商品价格保存在数据库中。商品信息包含名称、多级品类、规格、条码、图片等，方便后续查询。 

- 5. 提供商品查询界面能显示商品信息，把历史价格用图表形式显示（如价格走势图）。 

- 6. 支持设置降价提醒，针对指定商品定时查询最新价格，如有降价发送提醒，可以通过邮件，App 推送等方式实现。 

- 7. 样式适配手机，开发手机 App 或能够在手机浏览器/微信等应用内置的浏览器中友好显示。 

<b>增强功能：</b> 如开发手机端，可以用相机拍摄商品图片或扫码商品条码进行商品查询。 

  > [!TIP]
  >
  > 为了提交作业方便，项目使用的数据库，建议使用`mysql`，提交作业时同时附带建库建表的脚本文件或数据。

## 总体设计思路 

<b>技术栈：</b>Vue + Flask + MySQL

### 前端设计

使用Vue开发一个多页面的小型前端应用，主要包括三个页面：

- 登录页面
- 注册页面
- 比价与查询页面

使用Vue-router管理页面跳转。

### 后端设计

- 使用Python Flask框架实现一个与前端对接的数据库接口程序，接收前端的请求（注册用户、核对登陆信息、查阅商品信息等），并对接数据库进行查询。
- 使用Python实现一个爬取商品信息的程序，爬取商品信息给数据库接口程序，加入数据库的同时发送给前端。
- 使用MySQL数据库系统存储数据库信息，建表内容有：
  - `users`，表项`username`（主键），`email`（候选码），`password`。
  - `goods`，表项`name`，`gid`（主键），`argument`，`category`（暂分为家电、数码产品、食品、日用品、衣物、其他），`image`
  - `prices`，表项`gid`（外键），`price`，`date`，`pid`（主键）

### 设计目标分析

#### 登录与注册模块

- 前端保证用户输入，如果有不当输入及时过滤，如，通过正则表达式限制邮箱格式。

- 后端数据库存储用户信息于表格`users`中，表项`username`，`email`，`password`。

  > [!TIP]
  >
  > 值得注意的是，存储于数据库的通常是密码的哈希值，为了避免数据库泄露带来密码泄露的风险，保护用户的隐私。当用户输入密码后，调用`bcrypt`加密。

#### 商品实时价格查询

- 根据用户输入，生成请求访问多个电商平台，爬取价格信息。

  - 用户输入考虑分词处理，将对同一商品的不同查询表述绑定到同一商品上。

  - 设置合适的爬取策略。

- 处理爬取结果：丢弃明显与用户需求不相符的结果（可能是平台竞价排名推荐的一些不相关产品），在列表中显示其他结果，列表提供缩略图和简要商品信息，以及跳转至目标电商商品详情页的链接。

- 比价：每次查询显示每个平台查询结果的均价。

- 显示查询汇总结果，如果数据库暂无该商品，将其加入数据库。
  - 数据库内商品，一定时间间隔爬取一次价格，加入数据库内。

#### 收藏和降价提醒

- 用户可以将商品查询结果设置为收藏，数据库内储存用户收藏的查询结果。
- 用户在线一段时间或者每次登录时，查询数据库内用户收藏的商品价格是否降价（满足一个设定的幅度阈值才会提醒用户）

- 如果有降价商品，网站将向用户推送一条通知。

#### 适配手机

尽量采用手机和电脑都可以有较好显示效果的布局方案，如果实在无法妥协，则会为手机设计单独的显示效果。







## 目前进度



#### 前端页面

目前初步完成了登录、注册和商品展示页，以及他们之间的跳转路由管理。

![未标题-1](C:\Users\Lenovo\Pictures\未标题-1.png)

![未标题-2](C:\Users\Lenovo\Pictures\未标题-2.png)

- 实现了正则表达式限制邮箱格式。
- 实现了初步的跳转关系。
- 实现了初步的手机显示适配。
- 商品显示因为目前只是初步，样式还会有所调整。

#### 商品爬取

目前暂定爬取苏宁易购和京东的商品。暂时输出为`json`，输出的格式还没有统一，之后会进行调整。

- 京东：爬取京东热卖二级域名的结果，这个页面是静态页面，正常编写请求然后从页面里解析数据。

  ```python
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
  
  # 定义基础url
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
  def analysisData(baseurl):
      # 获取指定网页
      url = baseurl
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
                      'SKU ID': product.get('sku_id'),
                      '商品名称': product.get('ad_title'),
                      '图片链接': product.get('image_url'),
                      '点击链接': product.get('click_url'),
                      '价格': price
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
          excel_filename = f'商品信息_{timestamp}.xlsx'
          df.to_excel(excel_filename, index=False)
  
          # 输出到 JSON 文件
          json_filename = f'商品信息_{timestamp}.json'
          with open(json_filename, 'w', encoding='utf-8') as json_file:
              json.dump(filtered_products, json_file, ensure_ascii=False, indent=4)
          
          # 输出平均价格
          print(f"商品信息已输出到 '{excel_filename}' 和 '{json_filename}'")
          print(f"去除最贵和最便宜的商品后的平均价格: {average_price:.2f} 元")
      else:
          print("未找到包含商品信息的<script>标签。")
      return
   
   
  def main():
      analysisData(baseurl)
   
  if __name__ == "__main__":
      main()
  ```

  

- 苏宁易购：爬取手机适配页面二级域名的结果，这是一个动态页面，但可以通过继续伪造请求的方法获取商品信息。

  ```python
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
  def analysisData(baseurl):
      # 获取指定网页
      url = baseurl
      html = geturl(url)
      soup = BeautifulSoup(html, "html5lib")
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
                  "partnumber0": partnumbers[i][0],
                  "partnumber1": partnumbers[i][1],
                  "goodurl": goodurl,
                  "title": title,
                  "img_url": img_url,
                  "price": ppjson
              }
              # 添加到列表
              data_list.append(data)
          # 定义文件名
          filename = f"./sn_{keyword}{timestamp}.json"
          # 将列表写入 JSON 文件
          with open(filename, 'w', encoding='utf-8') as f:
              json.dump(data_list, f, ensure_ascii=False, indent=4)
          print(f"数据已保存到 {filename}")
      else:
          print("未找到包含商品信息的<script>标签。")
      return
   
  def main():
      analysisData(baseurl)
   
  if __name__ == "__main__":
      main()
  ```

  

- 淘宝：淘宝的反爬取特别严格，最可行的方案是用selenium模拟浏览器输入，但由于这种方法效率和灵活性都很差，而且需要实现密码输入、反人机验证，工作量太大，目前暂时还没有实现。
