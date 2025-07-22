# Peler Panel 服务器管理面板开发文档

## 项目概述

Peler Panel 是一个基于 Python Flask 的个人服务器管理面板，用于管理和快速访问服务器上的各种服务。用户可以通过可视化的卡片界面添加、编辑、删除和排序服务链接。

## 功能特性

### 核心功能
- ✅ 服务卡片管理（增删改查）
- ✅ 可视化卡片展示（图标 + 名称 + 描述 + 链接）
- ✅ 拖拽排序功能
- ✅ 实时搜索筛选
- ✅ 密码认证管理
- ✅ 响应式设计
- ✅ 新窗口打开链接

### 用户界面
- **主界面**: 网格布局展示所有服务卡片
- **编辑界面**: 模态框形式的卡片编辑器
- **图标选择器**: Bootstrap Icons 选择对话框
- **搜索栏**: 实时搜索名称和描述
- **认证窗口**: 管理员密码验证

## 技术架构

### 技术栈
- **后端框架**: Python Flask
- **前端框架**: Bootstrap 5
- **图标库**: Bootstrap Icons
- **数据存储**: JSON 文件
- **JavaScript库**: 
  - jQuery (DOM操作)
  - Bootstrap JS (模态框等组件)
  - SortableJS (拖拽排序)

### 项目结构
```
peler-panel/
├── app.py                 # Flask 主应用
├── data/
│   └── cards.json        # 卡片数据存储
├── static/
│   ├── css/
│   │   └── style.css     # 自定义样式
│   └── js/
│       └── main.js       # 前端JavaScript
├── templates/
│   └── index.html        # 主页面模板
└── requirements.txt      # Python依赖
```

## 数据结构设计

### JSON 数据格式
```json
{
  "cards": [
    {
      "id": "unique_id_string",
      "name": "服务名称",
      "icon": "bi-server",
      "url": "https://example.com",
      "description": "服务描述信息",
      "order": 1,
      "created_time": "2025-07-22T10:30:00.000Z"
    }
  ],
  "config": {
    "last_updated": "2025-07-22T10:30:00.000Z",
    "total_cards": 1
  }
}
```

### 字段说明
- **id**: 唯一标识符（UUID格式）
- **name**: 服务名称（不允许重复）
- **icon**: Bootstrap Icons 类名（如：bi-server）
- **url**: 服务访问链接
- **description**: 服务描述
- **order**: 排序位置（数字，越小越靠前）
- **created_time**: 创建时间（ISO格式）

## API 接口设计

### 认证接口
- `POST /api/auth` - 管理员密码验证
- `POST /api/logout` - 退出登录

### 卡片管理接口
- `GET /api/cards` - 获取所有卡片
- `POST /api/cards` - 创建新卡片
- `PUT /api/cards/<id>` - 更新卡片
- `DELETE /api/cards/<id>` - 删除卡片
- `POST /api/cards/reorder` - 批量更新排序

### 工具接口
- `GET /api/icons` - 获取可用图标列表
- `POST /api/validate-name` - 验证名称唯一性

## 前端功能详解

### 主页面功能
1. **卡片网格显示**
   - 自适应网格布局
   - 每张卡片显示图标、名称、描述
   - 支持响应式设计

2. **实时搜索**
   - 搜索名称和描述字段
   - 无需按回车，输入即搜索
   - 高亮匹配结果

3. **拖拽排序**
   - 使用 SortableJS 实现
   - 拖拽后自动保存排序
   - 流畅的拖拽动画

### 管理功能
1. **认证系统**
   - 点击"添加卡片"或"编辑"触发认证
   - Session 持续到浏览器关闭
   - 错误提示和重试机制

2. **卡片编辑器**
   - 模态框形式
   - 表单验证（必填字段、名称重复检查）
   - 支持添加和编辑模式

3. **图标选择器**
   - 独立的模态框对话框
   - 支持类名搜索（如输入"server"）
   - 图标预览和点击选择
   - 常用图标分类显示

## 用户体验设计

### 交互流程
1. **普通用户访问**:
   ```
   访问首页 → 查看卡片 → 使用搜索 → 点击卡片跳转（新窗口）
   ```

2. **管理员操作**:
   ```
   点击管理按钮 → 密码验证 → 编辑/添加卡片 → 选择图标 → 保存 → 拖拽排序
   ```

### 响应式断点
- **手机** (< 576px): 1列布局
- **平板** (576px - 768px): 2列布局
- **桌面** (768px - 992px): 3列布局
- **大屏** (> 992px): 4-5列布局

### 用户反馈
- 操作成功/失败的 Toast 提示
- 加载状态指示器
- 表单验证错误提示
- 确认删除对话框

## 安全考虑

### 认证安全
- 密码使用环境变量存储
- Session 基于服务器端验证
- 防止暴力破解（错误次数限制）

### 数据安全
- 输入数据验证和过滤
- XSS 防护
- JSON 数据格式验证
- 文件读写权限控制

## 部署要求

### 环境依赖
```
Python >= 3.8
Flask >= 2.0
```

### 环境变量
```bash
ADMIN_PASSWORD=your_secure_password
FLASK_SECRET_KEY=your_secret_key
DATA_PATH=./data/cards.json
```

### 运行配置
- 开发模式: `flask run --debug`
- 生产模式: 使用 Gunicorn 或 uWSGI
- 端口: 默认 5000（可配置）

## 扩展功能预留

### 未来可能的功能
- [ ] 多用户支持
- [ ] 卡片分类/标签
- [ ] 服务状态监控
- [ ] 数据导入/导出
- [ ] 主题切换
- [ ] 访问统计
- [ ] API 接口文档

### 技术升级路径
- 数据库迁移 (SQLite → PostgreSQL)
- 前端框架升级 (Vue.js/React)
- 容器化部署 (Docker)
- API 版本控制

## 开发注意事项

### 代码规范
- 遵循 PEP 8 Python 代码风格
- 使用 ESLint 检查 JavaScript
- 统一的错误处理机制
- 完整的注释文档

### 测试策略
- 单元测试覆盖关键函数
- API 接口测试
- 前端交互测试
- 跨浏览器兼容性测试

### 性能优化
- JSON 文件大小监控
- 静态资源缓存
- 图片懒加载
- API 请求去重

---

**文档版本**: 1.0  
**创建时间**: 2025-07-22  
**最后更新**: 2025-07-22