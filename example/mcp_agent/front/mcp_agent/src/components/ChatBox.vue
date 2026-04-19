<script setup>
import { ref, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'

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
    const response = await fetch('http://localhost:8000/chat', {
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
        <div class="header-subtitle">智能出行 · AI助手</div>
      </div>
      
      <!-- 消息列表 -->
      <div class="messages" ref="chatContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message-row', msg.role]">
          <div class="avatar">
            <span v-if="msg.role === 'ai'">
              <!-- 卡通机器人头像 -->
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                <!-- 机器人头部 -->
                <rect x="6" y="4" width="12" height="10" rx="2" fill="url(#robotGradient)" stroke="#00d4ff" stroke-width="1.5"/>
                <!-- 天线 -->
                <line x1="12" y1="4" x2="12" y2="1" stroke="#00d4ff" stroke-width="1.5" stroke-linecap="round"/>
                <circle cx="12" cy="1" r="1.5" fill="#00ff88"/>
                <!-- 眼睛 -->
                <circle cx="9.5" cy="8" r="2" fill="#00ff88"/>
                <circle cx="14.5" cy="8" r="2" fill="#00ff88"/>
                <!-- 眼睛高光 -->
                <circle cx="10" cy="7.5" r="0.6" fill="#fff"/>
                <circle cx="15" cy="7.5" r="0.6" fill="#fff"/>
                <!-- 嘴巴 -->
                <path d="M9 11 Q12 13 15 11" stroke="#00d4ff" stroke-width="1.5" stroke-linecap="round" fill="none"/>
                <!-- 身体 -->
                <rect x="8" y="14" width="8" height="6" rx="1" fill="url(#robotBodyGradient)" stroke="#00d4ff" stroke-width="1"/>
                <!-- 胸口灯 -->
                <circle cx="12" cy="17" r="1.5" fill="#00ff88">
                  <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
                </circle>
                <!-- 渐变定义 -->
                <defs>
                  <linearGradient id="robotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#0066ff;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#00d4ff;stop-opacity:1" />
                  </linearGradient>
                  <linearGradient id="robotBodyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#1a1f3a;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#0a0e27;stop-opacity:1" />
                  </linearGradient>
                </defs>
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
/* 整体容器 - 科技感深色主题 */
.chat-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  /* 深色科技感背景 */
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1321 100%);
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(0, 102, 255, 0.08) 0%, transparent 50%),
    linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 50px 50px, 50px 50px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 850px;
  width: 100%;
  max-width: 950px;
  /* 深色玻璃拟态 */
  background: rgba(16, 20, 40, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 24px;
  box-shadow: 
    0 0 60px rgba(0, 102, 255, 0.15),
    0 20px 40px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
}

/* 顶部装饰线 - 霓虹蓝 */
.chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #00d4ff, #0066ff, #00d4ff);
  background-size: 200% 100%;
  animation: gradientMove 3s linear infinite;
}

@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

/* 头部样式 - 科技感 */
.chat-header {
  padding: 20px 28px;
  background: rgba(10, 14, 39, 0.9);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
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
  background: #00ff88;
  border-radius: 50%;
  box-shadow: 0 0 10px #00ff88, 0 0 20px rgba(0, 255, 136, 0.5);
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
  color: #00d4ff;
  letter-spacing: 0.5px;
  font-family: 'Inter', sans-serif;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.header-subtitle {
  font-size: 0.75rem;
  color: #00d4ff;
  font-weight: 600;
  background: rgba(0, 212, 255, 0.1);
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid rgba(0, 212, 255, 0.3);
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
}

/* 滚动条样式 - 深色科技感 */
.messages::-webkit-scrollbar {
  width: 6px;
}
.messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}
.messages::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}
.messages::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
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
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(16, 20, 40, 0.8);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 0 15px rgba(0, 212, 255, 0.2);
}

.message-row.ai .avatar {
  background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
  color: #fff;
  border: 1px solid rgba(0, 212, 255, 0.5);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

.message-row.user .avatar {
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  color: #fff;
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

.message-bubble {
  padding: 16px 20px;
  border-radius: 16px;
  font-size: 1rem;
  line-height: 1.65;
  position: relative;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.message-row.ai .message-bubble {
  background: rgba(16, 20, 40, 0.9);
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #e0f2fe;
  border-top-left-radius: 4px;
  box-shadow: 0 0 20px rgba(0, 102, 255, 0.1);
}

.message-row.user .message-bubble {
  background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
  color: #ffffff;
  border-top-right-radius: 4px;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

/* Loading 状态 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  margin-left: 56px;
  color: #00d4ff;
  font-size: 0.85rem;
  font-family: monospace;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 20px;
  width: fit-content;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.dot {
  width: 6px;
  height: 6px;
  background: #00d4ff;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
  box-shadow: 0 0 10px #00d4ff;
}

/* 输入区域 */
.input-area {
  padding: 24px 32px;
  background: rgba(10, 14, 39, 0.9);
  border-top: 1px solid rgba(0, 212, 255, 0.2);
}

.input-box {
  display: flex;
  gap: 12px;
  background: rgba(16, 20, 40, 0.8);
  padding: 8px;
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
}

.input-box:focus-within {
  background: rgba(16, 20, 40, 1);
  border-color: #00d4ff;
  box-shadow: 0 0 0 4px rgba(0, 212, 255, 0.15), 0 0 20px rgba(0, 212, 255, 0.2);
}

input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px 16px;
  color: #e0f2fe;
  font-size: 1rem;
  outline: none;
}

input::placeholder {
  color: #64748b;
}

.send-btn {
  background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
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
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

.send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 0 25px rgba(0, 212, 255, 0.5);
}

.send-btn:disabled {
  background: rgba(100, 116, 139, 0.3);
  color: #475569;
  cursor: not-allowed;
  box-shadow: none;
}

/* Markdown 样式适配深色科技感主题 */
:deep(.markdown-body) {
  color: #e0f2fe;
  font-size: 1rem;
  line-height: 1.7;
}

:deep(.markdown-body p) {
  margin-bottom: 0.8em;
}

:deep(.markdown-body a) {
  color: #00d4ff;
  text-decoration: none;
  font-weight: 500;
}

:deep(.markdown-body code) {
  background: rgba(0, 212, 255, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

:deep(.markdown-body pre) {
  background: rgba(10, 14, 39, 0.9);
  padding: 20px;
  border-radius: 12px;
  overflow-x: auto;
  border: 1px solid rgba(0, 212, 255, 0.3);
  box-shadow: 0 0 20px rgba(0, 102, 255, 0.1);
}

:deep(.markdown-body pre code) {
  background: transparent;
  color: #00d4ff;
  border: none;
  padding: 0;
}
</style>
