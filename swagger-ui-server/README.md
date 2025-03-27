# Swagger UI 服务器

使用Express和Swagger UI展示API文档。

## 本地开发

### 安装依赖

```bash
cd swagger-ui-server
npm install
```

### 启动开发服务器

```bash
npm run dev
```

服务器将在 <http://localhost:3000> 启动。

## 部署到Vercel

### 方法1：通过Vercel CLI

1. 安装Vercel CLI:

```bash
npm install -g vercel
```

2. 登录Vercel:

```bash
vercel login
```

3. 部署项目:

```bash
cd swagger-ui-server
vercel
```

### 方法2：通过Vercel网站

1. 访问 [Vercel](https://vercel.com) 并登录
2. 点击 "New Project"
3. 导入你的Git仓库
4. 选择 "swagger-ui-server" 目录作为根目录
5. 点击 "Deploy"

## 配置说明

- `swagger.yml` - API文档定义
- `index.js` - Express服务器配置
- `vercel.json` - Vercel部署配置

## 自定义

如需修改API文档，请编辑 `swagger.yml` 文件。
