<template>
  <div class="container">
    <h1>知乎搜索</h1>
    <div class="search-box">
      <input 
        v-model="searchQuery" 
        @keyup.enter="search"
        placeholder="输入搜索关键词"
        type="text"
      >
      <button @click="search" :disabled="loading">
        {{ loading ? '搜索中...' : '搜索' }}
      </button>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="results.length" class="results">
      <div v-for="item in results" :key="item.id" class="result-item">
        <h3>{{ item.object.title }}</h3>
        <p>{{ item.object.excerpt }}</p>
        <a :href="item.object.url" target="_blank">查看详情</a>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  setup() {
    const searchQuery = ref('')
    const results = ref([])
    const loading = ref(false)
    const error = ref('')

    const search = async () => {
      if (!searchQuery.value.trim()) return
      
      loading.value = true
      error.value = ''
      
      try {
        const response = await axios.get(`/.netlify/functions/search?q=${encodeURIComponent(searchQuery.value)}`)
        results.value = response.data.data || []
      } catch (err) {
        error.value = '搜索出错：' + (err.response?.data?.error || err.message)
      } finally {
        loading.value = false
      }
    }

    return {
      searchQuery,
      results,
      loading,
      error,
      search
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 8px 20px;
  background-color: #0066ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
}

.result-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.error {
  color: red;
  margin: 10px 0;
}
</style> 