### 工业视觉检测平台

### 安装配置步骤

以下是安装和配置工业视觉检测平台的基本步骤：

#### 前提条件

确保已安装以下软件和工具：

- Python 3.x
- Node.js (用于前端开发)
- PostgreSQL 数据库
- Git

#### 步骤

1. **克隆项目代码**

   ```bash
   git clone <repository_url>
   cd platform
   ```

2. **后端设置**

   - 创建虚拟环境（可选但推荐）

     ```bash
     conda create -n SE python=3.9
     ```

   - 安装依赖包

     ```bash
     pip install -r requirements.txt
     ```

   - 运行后端服务

     ```bash
     cd server
     python app.py
     ```

3. **前端设置**

   ```
   cd ../client
   ```

   - 安装依赖包

     ```
     yarn install
     yarn build
     ```

   - 运行前端开发服务器

     ```bash
     npm run serve
     ```

4. **访问应用程序**

   打开浏览器访问 `http://localhost:8080` 查看工业视觉检测平台应用程序。