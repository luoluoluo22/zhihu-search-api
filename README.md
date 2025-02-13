# 知乎搜索 API 服务

这是一个基于 FastAPI 和 Pyppeteer 的知乎搜索 API 服务。它可以模拟浏览器行为，执行知乎搜索并返回搜索结果。

## 功能特点

- 支持知乎搜索内容的 API 化
- 自动处理浏览器环境
- 支持本地开发和云端部署
- 完整的 CORS 支持
- RESTful API 设计

## 本地开发

1. 克隆仓库：
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 创建 `.env` 文件并设置知乎 Cookie：
```
ZHIHU_COOKIE='your_zhihu_cookie_here'
```

4. 运行服务：
```bash
python -m uvicorn app:app --reload
```

服务将在 http://localhost:8000 启动。

## API 端点

- `GET /`: 健康检查
- `GET /search/{query}`: 执行知乎搜索
  - `query`: 搜索关键词

## 部署到 Render

1. Fork 或克隆此仓库到你的 GitHub 账号

2. 在 Render 上创建新的 Web Service：
   - 选择 "New Web Service"
   - 连接你的 GitHub 仓库

3. 配置部署设置：
   - 配置文件已经预设在 `render.yaml` 中
   - Render 会自动识别并使用这些配置
   - 构建过程会自动下载 Chromium（在构建阶段完成）

4. 添加环境变量：
   - 在 Render 的环境变量设置中添加 `ZHIHU_COOKIE`
   - 将你的知乎 Cookie 字符串粘贴为值

5. 部署：
   - 点击 "Create Web Service"
   - Render 将自动执行以下步骤：
     1. 安装依赖
     2. 下载 Chromium（在构建阶段）
     3. 启动服务

## 部署说明

- **构建过程**：
  - 使用 `build.sh` 脚本自动化构建
  - 在构建阶段预先下载 Chromium
  - 构建失败会自动重试（最多3次）

- **资源配置**：
  - 构建内存：1024MB
  - 运行内存：starter plan
  - 实例数量：1（可根据需求调整）

- **自动部署**：
  - 启用了自动部署功能
  - 推送到主分支会触发自动部署

## 注意事项

1. Cookie 安全：
   - 不要在代码中硬编码 Cookie
   - 定期更新 Cookie 以确保可用性
   - 在生产环境中安全存储 Cookie

2. 资源使用：
   - Chromium 在构建阶段下载，不会影响运行时性能
   - 每个请求会启动一个新的浏览器实例，注意资源管理

3. 限制：
   - 请遵守知乎的使用条款
   - 建议实现请求频率限制
   - 注意处理并发请求

## 故障排除

1. 如果构建失败：
   - 检查构建日志中的 Chromium 下载状态
   - 确认构建内存是否足够
   - 可以尝试手动触发重新构建

2. 如果运行时出错：
   - 检查 Cookie 是否有效
   - 确认 Chromium 是否正确安装
   - 查看应用日志获取详细错误信息

3. 如果遇到内存问题：
   - 考虑升级到更高的计划
   - 优化并发请求数量

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE) 