<script setup>
import { ref, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const md = new MarkdownIt({
  html: false, // 禁用 HTML 以防止 XSS
  linkify: true,
  breaks: true
})

const messages = ref([
  { role: 'ai', content: '你好！我是 智行助手，可以帮你查询天气、写文件或规划出行路线。' }
])
const userInput = ref('')
const isLoading = ref(false)
const loadingStatus = ref('')
const chatContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content || isLoading.value) return

  // 1. 添加用户消息
  messages.value.push({ role: 'user', content })
  userInput.value = ''
  isLoading.value = true
  loadingStatus.value = '正在思考...'
  await scrollToBottom()

  // 2. 准备 AI 消息占位
  const aiMessage = { role: 'ai', content: '' }
  messages.value.push(aiMessage)

  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: content })
    })

    const data = await response.json()
    
    if (data.status === 'success') {
       aiMessage.content = data.content
    } else if (data.status === 'empty') {
       aiMessage.content = '(未获取到回复，请重试)'
    } else {
       aiMessage.content = `[系统错误: ${data.error || '未知错误'}]`
    }

  } catch (e) {
    aiMessage.content = `[网络请求出错: ${e.message}]`
  } finally {
    isLoading.value = false
    loadingStatus.value = ''
    scrollToBottom()
  }
}

const renderMarkdown = (text) => {
  return md.render(text || '')
}
</script>

<template>
  <div class="chat-wrapper">
    <div class="chat-container">
      <!-- 顶部栏 -->
      <div class="chat-header">
        <div class="header-content">
          <div class="status-dot"></div>
          <h2>智行助手</h2>
        </div>
        <div class="header-subtitle">Powered by Qwen & MCP</div>
      </div>
      
      <!-- 消息列表 -->
      <div class="messages" ref="chatContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message-row', msg.role]">
          <div class="avatar">
            <span v-if="msg.role === 'ai'" class="avatar-image">
              <!-- 卡通人物头像 SVG -->
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 100 100">
                <!-- 头部 -->
                <circle cx="50" cy="40" r="25" fill="#FFD7B5"/>
                <!-- 头发 -->
                <path d="M25 40 Q15 20 25 10 Q35 0 50 0 Q65 0 75 10 Q85 20 75 40" fill="#8B4513"/>
                <!-- 眼睛 -->
                <circle cx="40" cy="35" r="5" fill="#333"/>
                <circle cx="60" cy="35" r="5" fill="#333"/>
                <!-- 嘴巴 -->
                <path d="M40 50 Q50 60 60 50" stroke="#333" stroke-width="2" fill="none"/>
                <!-- 耳朵 -->
                <circle cx="25" cy="40" r="5" fill="#FFD7B5"/>
                <circle cx="75" cy="40" r="5" fill="#FFD7B5"/>
                <!-- 身体 -->
                <rect x="35" y="65" width="30" height="20" fill="#4CAF50"/>
                <!-- 手臂 -->
                <rect x="25" y="65" width="10" height="15" fill="#4CAF50"/>
                <rect x="65" y="65" width="10" height="15" fill="#4CAF50"/>
              </svg>
            </span>
            <span v-else>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </span>
          </div>
          <div class="message-bubble">
            <div v-if="msg.role === 'ai'" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
            <div v-else>{{ msg.content }}</div>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-indicator">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
          <span>{{ loadingStatus }}</span>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-box">
          <input 
            v-model="userInput" 
            @keyup.enter="sendMessage"
            placeholder="输入你的问题..." 
            :disabled="isLoading"
          />
          <button @click="sendMessage" :disabled="isLoading || !userInput.trim()" class="send-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 整体容器 */
.chat-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  /* 科技感背景 */
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  position: relative;
  overflow: hidden;
}

/* 科技感网格效果 */
.chat-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56, 189, 248, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  background-position: center center;
  pointer-events: none;
}

/* 科技感光效 */
.chat-wrapper::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, transparent 70%);
  animation: pulse-glow 8s ease-in-out infinite;
  pointer-events: none;
}

@keyframes pulse-glow {
  0% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.1); opacity: 0.6; }
  100% { transform: scale(1); opacity: 0.3; }
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 850px;
  width: 100%;
  max-width: 950px;
  /* 玻璃拟态效果 */
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

/* 顶部科技感装饰线 */
.chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
  opacity: 1;
  z-index: 2;
}

/* 头部样式 */
.chat-header {
  padding: 20px 28px;
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; transform: scale(0.95); }
  50% { opacity: 1; transform: scale(1.05); }
  100% { opacity: 0.6; transform: scale(0.95); }
}

.chat-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.5px;
  font-family: 'Inter', sans-serif;
  text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);
}

.header-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 消息列表区域 */
.messages {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 28px;
  position: relative;
  z-index: 1;
}

/* 滚动条样式 - 科技感 */
.messages::-webkit-scrollbar {
  width: 6px;
}
.messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}
.messages::-webkit-scrollbar-thumb {
  background: rgba(56, 189, 248, 0.5);
  border-radius: 3px;
  transition: all 0.3s ease;
}
.messages::-webkit-scrollbar-thumb:hover {
  background: rgba(56, 189, 248, 0.8);
}

.message-row {
  display: flex;
  gap: 16px;
  max-width: 85%;
  animation: fadeIn 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-row.user {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 0 20px rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.avatar-image {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.message-row.ai .avatar {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(129, 140, 248, 0.2));
  border: 1px solid rgba(56, 189, 248, 0.3);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
}

.message-row.user .avatar {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(34, 197, 94, 0.2));
  color: #fff;
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.message-bubble {
  padding: 16px 20px;
  border-radius: 16px;
  font-size: 1rem;
  line-height: 1.65;
  position: relative;
  word-break: break-word;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.message-row.ai .message-bubble {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  border-top-left-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2), 0 0 10px rgba(56, 189, 248, 0.1);
}

.message-row.user .message-bubble {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(129, 140, 248, 0.2));
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #ffffff;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
}

/* Loading 状态 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  margin-left: 64px;
  color: #94a3b8;
  font-size: 0.85rem;
  font-family: monospace;
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  width: fit-content;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dot {
  width: 6px;
  height: 6px;
  background: #38bdf8;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.8);
}

/* 输入区域 */
.input-area {
  padding: 24px 32px;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-box {
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.08);
  padding: 8px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
}

.input-box:focus-within {
  background: rgba(255, 255, 255, 0.1);
  border-color: #38bdf8;
  box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.2), 0 4px 12px rgba(0,0,0,0.1);
}

input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px 16px;
  color: #e2e8f0;
  font-size: 1rem;
  outline: none;
}

input::placeholder {
  color: #64748b;
}

.send-btn {
  background: linear-gradient(135deg, #38bdf8, #818cf8);
  border: none;
  color: white;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
  position: relative;
  overflow: hidden;
}

.send-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.6s ease;
}

.send-btn:hover:not(:disabled)::before {
  left: 100%;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(56, 189, 248, 0.4);
}

.send-btn:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: #64748b;
  cursor: not-allowed;
  box-shadow: none;
}

/* Markdown 样式适配科技感 */
:deep(.markdown-body) {
  color: #e2e8f0;
  font-size: 1rem;
  line-height: 1.7;
}

:deep(.markdown-body p) {
  margin-bottom: 0.8em;
}

:deep(.markdown-body a) {
  color: #38bdf8;
  text-decoration: none;
  font-weight: 500;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
}

:deep(.markdown-body code) {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.markdown-body pre) {
  background: rgba(0, 0, 0, 0.5);
  padding: 20px;
  border-radius: 12px;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

:deep(.markdown-body pre code) {
  background: transparent;
  color: #e2e8f0;
  border: none;
  padding: 0;
}
</style>
