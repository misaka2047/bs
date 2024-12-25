<template>
  <div class="product-list">
    <div class="header">
      <div class="user-info">
        <!-- 根据时间段显示不同的问候语 -->
        <span v-if="username">{{ getGreetingMessage(username) }}</span>
        <span v-else>未登录</span>
      </div>
    </div>
    <div class="search-container">
      <input v-model="searchQuery" @keyup.enter="fetchProducts" placeholder="搜索商品..." />
      <button @click="fetchProducts" :disabled="isLoading">搜索</button>
    </div>
    <!-- 展示栏 -->
    <div v-if="!isLoading && products.length > 0" class="display-container">
      <img :src="products[0].imgurl" alt="商品图片" />
      <p>今日均价：<b>{{ averagePrice }}</b>元</p>
      <button @click="addToFavorites">收藏</button>
    </div>
    <!-- 根据条件动态展示图片 -->
    <div v-if="showImages" class="banner-container">
      <img :src="`http://localhost:5000/static/images/price_JD.png?t=${timestamp}`" alt="京东价格" />
      <img :src="`http://localhost:5000/static/images/price_Suning.png?t=${timestamp}`" alt="苏宁价格" />
    </div>
    <!-- 加载状态提示 -->
    <div v-if="isLoading" class="loading-container">正在搜索，请稍候...</div>
    <div class="products">
      <div v-if="!isLoading && products.length === 0">在搜索栏输入感兴趣的商品吧！</div>
      <div v-for="product in products" :key="product.gid" class="product-item">
        <img :src="product.imgurl" alt="商品图片" />
        <h3>{{ product.title }}</h3>
        <p>平台: {{ product.platform }}</p>
        <p>价格: {{ product.price }}元</p>
        <a :href="product.clickurl" target="_blank">查看详情</a>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const searchQuery = ref('');
    const products = ref([]); // 用于存储后端返回的商品数据
    const showImages = ref(false); // 控制是否显示图片
    const timestamp = ref(Date.now()); // 时间戳，用于刷新图片
    const isLoading = ref(false); // 控制加载状态
    const username = ref(''); // 用于存储当前用户的用户名
    const averagePrice = ref(0); // 今日均价

    // 获取当前登录的用户名
    onMounted(() => {
      const user = JSON.parse(localStorage.getItem('user'));
      if (user) {
        username.value = user.username; // 假设用户名存储在 localStorage 中
      }
    });

    // 根据当前时间生成问候语
    const getGreetingMessage = (username) => {
      const now = new Date();
      const hour = now.getHours();

      if (hour >= 5 && hour < 8) {
        return `${username}，早上好！`;
      } else if (hour >= 8 && hour < 12) {
        return `${username}，上午好！`;
      } else if (hour >= 12 && hour < 14) {
        return `${username}，中午好！`;
      } else if (hour >= 14 && hour < 18) {
        return `${username}，下午好！`;
      } else {
        return `${username}，晚上好！`;
      }
    };

    // 从后端获取商品数据
    const fetchProducts = async () => {
      isLoading.value = true; // 开始加载
      try {
        const response = await fetch('http://localhost:5000/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: searchQuery.value, // 将搜索关键字发送到后端
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          console.error('获取商品数据失败:', data.error || '未知错误');
          return;
        }

        products.value = data || []; // 假设后端直接返回商品数组

        // 计算均价
        if (products.value.length > 0) {
          averagePrice.value = (
            products.value.reduce((sum, product) => sum + parseFloat(product.price), 0) / products.value.length
          ).toFixed(2);
        }

        // 搜索完成后刷新图片
        showImages.value = true; // 搜索后显示图片
        timestamp.value = Date.now(); // 更新时间戳，刷新图片
      } catch (err) {
        console.error('网络错误:', err);
      } finally {
        isLoading.value = false; // 加载完成
      }
    };

    // 收藏功能
    const addToFavorites = async () => {
      try {
        const response = await fetch('http://localhost:5000/favorites', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: username.value,
            keyword: searchQuery.value,
            averagePrice: averagePrice.value,
          }),
        });

        if (!response.ok) {
          console.error('收藏失败:', await response.text());
          return;
        }

        alert('收藏成功！');
      } catch (err) {
        console.error('网络错误:', err);
      }
    };

    return { searchQuery, products, fetchProducts, showImages, timestamp, isLoading, username, averagePrice, getGreetingMessage, addToFavorites };
  },
};
</script>

<style scoped>
.product-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.user-info {
  font-size: 16px;
  color: #333;
}

.search-container {
  margin-bottom: 20px;
}

.search-container input {
  padding: 10px;
  margin-right: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.search-container button {
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.search-container button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.search-container button:hover:enabled {
  background-color: #45a049;
}

.display-container {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background-color: #f9f9f9;
  text-align: center;
}

.display-container img {
  max-width: 200px;
  height: auto;
  margin-bottom: 10px;
}

.banner-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.banner-container img {
  width: 500px; /* 图片宽度 */
  height: auto; /* 保持宽高比 */
  border-radius: 10px; /* 可选：圆角样式 */
}

.loading-container {
  text-align: center;
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
}

.products {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.product-item {
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 10px;
  width: 200px; /* 商品项宽度 */
  text-align: center;
}

.product-item img {
  max-width: 100%; /* 图片自适应 */
  border-radius: 5px;
}
</style>
