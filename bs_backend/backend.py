from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from jd import analysisData as jd_analysisData
from sn import analysisData as sn_analysisData
import urllib.parse
from datetime import datetime
import matplotlib.pyplot as plt

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 配置数据库连接
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "app"
}

# 数据库连接函数
def get_db_connection():
    return mysql.connector.connect(**db_config)


# 绘制价格-时间折线图
def plot_price_history(data, gid):
    if not data:
        print(f"No data found for gid: {gid}")
        return
    print(f"Plotting price history for gid: {gid}")
    # 将数据按平台分组
    platforms = {}
    try:
        for row in data:
            platform = row['platform']
            if platform not in platforms:
                platforms[platform] = {'dates': [], 'prices': []}
            platforms[platform]['dates'].append(row['date'])  # 直接使用 date 类型
            platforms[platform]['prices'].append(row['price'])
    except Exception as e:
        print(f"Failed to group data by platform: {e}")
    print(f"Data grouped by platform: {platforms}")
    # 为每个平台绘制一张图
    for platform, details in platforms.items():
        plt.figure(figsize=(10, 6))
        plt.plot(details['dates'], details['prices'], marker='o', label=platform)
        plt.title(f"Price History on {platform}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()
        plt.gcf().autofmt_xdate()  # 自动调整日期格式
        # 保存图片到路径./static/images/price_{platform}.png
        plt.savefig(f"./static/images/price_{platform}.png")
        # plt.show()
        print(f"Price history plot saved for gid {gid} on {platform}")
    print(f"Price history plots saved for gid: {gid}")

# API 路由
@app.route('/register', methods=['POST'])
def register():
    data = request.json  # 获取前端发送的 JSON 数据
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 验证输入
    if not username or not email or not password:
        return jsonify({"error": "所有字段都是必填项"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 插入用户数据
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        conn.commit()
        return jsonify({"message": "注册成功"}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"数据库错误: {err}"}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 查询所有用户
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        return jsonify(users), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"数据库错误: {err}"}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user['password'] == password:  # 简单比较密码（建议使用哈希加密）
            user_id = user['id']

            # (1) 查询用户的收藏商品列表
            cursor.execute("""
                SELECT g.gid, g.name, uf.price AS old_price
                FROM user_favorites uf
                JOIN goods g ON uf.gid = g.gid
                WHERE uf.id = %s
            """, (user_id,))
            favorites = cursor.fetchall()

            if not favorites:
                return jsonify({'message': '登录成功，无收藏商品'}), 200

            # (2) 使用爬虫函数查询商品并计算均价
            updated_products = []
            price_drops = []
            for item in favorites:
                gid = item['gid']
                name = item['name']
                old_price = item['old_price']

                # 爬取商品信息
                encoded_keyword = urllib.parse.quote(name)
                jd_query = "https://re.jd.com/search?keyword=" + encoded_keyword + "&enc=utf-8"
                sn_query = "https://m.suning.com/search/" + encoded_keyword + "/"

                jd_data = jd_analysisData(jd_query)
                sn_data = sn_analysisData(sn_query)

                all_prices = [float(item['price']) for item in jd_data + sn_data]
                avg_price = sum(all_prices) / len(all_prices) if all_prices else None

                if avg_price is not None:
                    updated_products.append((gid, avg_price, datetime.now()))

                    # 检测降价
                    if avg_price < old_price:
                        price_drops.append(name)

            # (3) 更新数据库中商品的价格信息和更新日期
            for gid, price, update_date in updated_products:
                cursor.execute("""
                    UPDATE user_favorites
                    SET price = %s, date = %s
                    WHERE gid = %s AND id = %s
                """, (price, update_date, gid, user_id))

            conn.commit()

            msg = '登录成功' 
            if price_drops:
                msg += '，以下商品降价：' + ', '.join(price_drops)

            # (4) 如果商品降价，则向前端发送降价商品名称
            return jsonify({
                'message': msg
            }), 200

        else:
            return jsonify({'error': '用户名或密码错误'}), 401

    except Exception as e:
        print(e)
        return jsonify({'error': '服务器内部错误'}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/search', methods=['POST'])
def search_products():
    data = request.json
    query = data.get('query', '').strip()  # 获取搜索关键字

    if not query:
        print("关键字为空")
        return jsonify({[]})  # 如果关键字为空，返回空列表

    # 把关键字转为京东和苏宁的搜索链接
    # 对 keyword 进行 URL 编码
    encoded_keyword = urllib.parse.quote(query)
    jd_query = "https://re.jd.com/search?keyword=" + encoded_keyword + "&enc=utf-8"
    sn_query = "https://m.suning.com/search/" + encoded_keyword + "/"

    # 调用京东和苏宁的爬虫函数，获取商品信息
    jd_data = jd_analysisData(jd_query)
    sn_data = sn_analysisData(sn_query)

    # 计算今日此商品在京东和苏宁的平均价格
    jd_price = sum([float(item['price']) for item in jd_data]) / len(jd_data)
    sn_price = sum([float(item['price']) for item in sn_data]) / len(sn_data)
    gid = 0
    
    #获取今日时间戳，精确到天
    timestamp = datetime.now().strftime('%Y-%m-%d')

    # 查询数据库有无商品信息，若无则插入一条商品信息。
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM goods WHERE name = %s", (query,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("INSERT INTO goods (name) VALUES (%s)",
                           (query,))
            conn.commit()
        cursor.execute("SELECT * FROM goods WHERE name = %s", (query,))
        result = cursor.fetchone()
        gid = result[0]

        # 向prices表插入价格信息
        try:
            cursor.execute("INSERT INTO prices (gid, price, date, platform) VALUES (%s, %s, %s, %s)",
                        (gid, jd_price, str(timestamp), 'JD'))
            cursor.execute("INSERT INTO prices (gid, price, date, platform) VALUES (%s, %s, %s, %s)",
                            (gid, sn_price, str(timestamp), 'Suning'))
        except Exception as e:
            print(f"Failed to insert price data: {e}")
        finally:
            conn.commit()
            cursor = conn.cursor(dictionary=True)
            # 查询价格信息
            print("checking prices")
            cursor.execute("SELECT * FROM prices WHERE gid = %s", (gid,))
            print("SELECT * FROM prices WHERE gid = %d"%(gid))
            data = cursor.fetchall()
            # 绘制价格-时间折线图
            plot_price_history(data, gid)
    except Exception as e:
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()
        return jd_data + sn_data

@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    username = data.get('username')
    keyword = data.get('keyword')
    price = data.get('averagePrice')
    print(data)
    if not username or not keyword or not price:
        return jsonify({'error': '所有字段都是必填项'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime('%Y-%m-%d')
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT gid FROM goods WHERE name = %s", (keyword,))
        gid = cursor.fetchone()[0]
        cursor.execute("INSERT INTO user_favorites (id, gid, price, date) VALUES (%s, %s, %s, %s)",
                       (user_id, gid, price, timestamp))
        conn.commit()
        return jsonify({'message': '添加收藏成功'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

# 主程序
if __name__ == '__main__':
    app.run(debug=True)
