<template>
  <div class="login-container">
    <div class="login-form">
      <h2>登录</h2>
      <form @submit.prevent="login">
        <input v-model="username" placeholder="用户名" required />
        <input type="password" v-model="password" placeholder="密码" required />
        <button type="submit">登录</button>
        <p>还没有账号？<router-link to="/register">注册</router-link></p>
      </form>
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
    const username = ref('');
    const password = ref('');
    const errorMessage = ref('');

    const login = async () => {
      errorMessage.value = ''; // 清空错误信息

      try {
        // 向后端发送登录请求
        const response = await fetch('http://localhost:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: username.value,
            password: password.value,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          // 登录失败，显示后端返回的错误信息
          errorMessage.value = data.error || '登录失败，请检查用户名或密码';
        } else {
          // 登录成功，保存用户信息到 localStorage
          localStorage.setItem('user', JSON.stringify({ username: username.value }));
          
          // 可以保存其他信息（如 token）：
          // localStorage.setItem('token', data.token); 

          alert(data.message || '登录成功！');
          window.location.href = '/products'; // 跳转到商品页面
        }
      } catch (err) {
        // 网络错误处理
        errorMessage.value = '网络错误，请稍后再试';
      }
    };

    return { username, password, login, errorMessage };
  },
};
</script>

<style scoped>
.login-container {
  background-image: url('../assets/background.jpg');
  background-size: cover;
  background-position: center;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-form {
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  width: 300px;
}

.login-form h2 {
  margin-bottom: 20px;
  text-align: center;
}

.login-form input {
  width: 95%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.login-form button {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.login-form button:hover {
  background-color: #45a049;
}

.login-form p {
  text-align: center;
}

.error-message {
  color: red;
  text-align: center;
  margin-top: 10px;
}
</style>
