# 智行助手 - 部署指南

本指南将帮助你将智行助手部署到免费的云端平台，让任何人都可以通过互联网访问。

## 📋 部署方案

- **前端**: Vercel (免费)
- **后端**: Railway (免费)
- **总成本**: $0/月

## 🚀 部署步骤

### 第一步：准备代码仓库

1. **初始化 Git 仓库** (如果还没有)
```bash
cd /Users/stacey/Desktop/Trae_Projects/mult_agent
git init
git add .
git commit -m "Initial commit"
```

2. **推送到 GitHub**
   - 在 GitHub 上创建新仓库
   - 推送代码到 GitHub

### 第二步：部署后端到 Railway

1. **注册 Railway**
   - 访问 https://railway.app/
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库
   - 选择 `example/mcp_agent` 目录

3. **配置环境变量**
   在 Railway 项目设置中添加以下环境变量：
   ```
   DASHSCOPE_API_KEY=你的阿里通义千问 API Key
   OPENWEATHER_API_KEY=你的 OpenWeather API Key
   AMAP_API_KEY=你的高德地图 API Key
   ```

4. **获取后端 URL**
   - 部署完成后，Railway 会提供一个 URL
   - 记住这个 URL，格式类似：`https://your-app.railway.app`

### 第三步：部署前端到 Vercel

1. **注册 Vercel**
   - 访问 https://vercel.com/
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "Add New" -> "Project"
   - 选择你的 GitHub 仓库
   - 选择 `example/mcp_agent/front/mcp_agent` 目录

3. **配置环境变量**
   在 Vercel 项目设置中添加：
   ```
   VITE_API_BASE_URL=https://your-app.railway.app
   ```
   将 `your-app.railway.app` 替换为你的 Railway 后端 URL

4. **部署**
   - 点击 "Deploy"
   - 等待部署完成（通常 1-2 分钟）

5. **获取前端 URL**
   - 部署完成后，Vercel 会提供一个 URL
   - 格式类似：`https://your-app.vercel.app`

### 第四步：测试部署

1. **访问前端**
   - 打开浏览器访问你的 Vercel URL
   - 例如：https://your-app.vercel.app

2. **测试功能**
   - 输入 "你好" 测试基本对话
   - 输入 "北京的天气" 测试天气查询
   - 输入 "搜索北京的咖啡店" 测试地图功能

## 🔧 故障排查

### 前端无法连接后端

**问题**: 前端显示 "网络请求出错"

**解决方案**:
1. 检查 Vercel 环境变量 `VITE_API_BASE_URL` 是否正确
2. 确保 Railway 后端 URL 可以访问
3. 检查 Railway 后端是否正在运行

### 后端部署失败

**问题**: Railway 部署失败

**解决方案**:
1. 检查 `requirements.txt` 是否包含所有依赖
2. 检查 `Procfile` 是否存在且格式正确
3. 查看 Railway 日志获取详细错误信息

### 环境变量未生效

**问题**: API 调用失败，显示缺少 API Key

**解决方案**:
1. 确认 Railway 环境变量已正确配置
2. 重新部署 Railway 项目
3. 检查环境变量名称是否正确（区分大小写）

## 📊 监控和维护

### Railway 后端监控

1. **查看日志**
   - 登录 Railway 控制台
   - 选择你的项目
   - 点击 "Logs" 查看实时日志

2. **监控资源使用**
   - Railway 免费套餐限制：
     - 512 MB RAM
     - 0.5 CPU
     - 500 小时/月

### Vercel 前端监控

1. **查看部署历史**
   - 登录 Vercel 控制台
   - 选择你的项目
   - 查看 "Deployments"

2. **查看访问日志**
   - 在 Vercel 控制台查看访问统计

## 🔄 更新部署

### 更新代码

1. **修改本地代码**
2. **提交到 GitHub**
   ```bash
   git add .
   git commit -m "Update features"
   git push
   ```

3. **自动部署**
   - Vercel 和 Railway 会自动检测到更新
   - 自动重新部署最新代码

## 💡 优化建议

### 性能优化

1. **启用缓存**
   - Vercel 自动缓存静态资源
   - 可以显著提升加载速度

2. **使用 CDN**
   - Vercel 全球 CDN 自动分发
   - 用户访问最近的服务器

### 安全建议

1. **保护 API Key**
   - 不要将 API Key 提交到 Git
   - 使用环境变量管理敏感信息

2. **启用 HTTPS**
   - Vercel 和 Railway 自动提供 HTTPS
   - 确保所有通信都使用加密连接

## 📞 支持

如果遇到问题：

1. **查看文档**
   - Vercel: https://vercel.com/docs
   - Railway: https://docs.railway.app

2. **社区支持**
   - GitHub Issues
   - Stack Overflow

3. **联系支持**
   - Vercel Support
   - Railway Support

## 🎉 完成！

现在你的智行助手已经部署到云端，任何人都可以通过互联网访问了！

**你的应用地址**:
- 前端: https://your-app.vercel.app
- 后端: https://your-app.railway.app

享受你的云端智能出行助手吧！🚀
