const express = require('express');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// 启用 CORS
app.use(cors());

// 加载 Swagger 定义
try {
  const swaggerDocument = yaml.load(fs.readFileSync(path.join(__dirname, 'swagger.yml'), 'utf8'));

  // 创建自定义模板
  const customHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>API文档</title>
  <link rel="stylesheet" type="text/css" href="./swagger-ui.css" />
  <style>
    .swagger-ui .topbar { display: none }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>

  <script src="./swagger-ui-bundle.js"></script>
  <script src="./swagger-ui-standalone-preset.js"></script>
  <script>
    window.onload = function() {
      // 开始时执行授权
      const ui = SwaggerUIBundle({
        spec: ${JSON.stringify(swaggerDocument)},
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout",
        docExpansion: 'list',
        defaultModelsExpandDepth: 0,
        persistAuthorization: true,
        // 直接配置初始化授权信息
        onComplete: function() {
          // 预先配置授权信息
          ui.preauthorizeApiKey("api_key", "Bearer sk-VefRuCzVAFDGiH0ep1T0CXeo26DMUu1EtEwh1tIKqd8B7rvR");
        }
      });
      
      window.ui = ui;
    }
  </script>
</body>
</html>
  `;

  // 提供自定义HTML和静态资源
  app.get('/', (req, res) => {
    res.setHeader('Content-Type', 'text/html');
    res.send(customHtml);
  });

  // 使用swagger-ui-express的静态资源
  app.use(express.static(path.dirname(require.resolve('swagger-ui-dist/absolute-path.js'))));

  app.listen(port, () => {
    console.log(`Swagger UI 服务器运行在: http://localhost:${port}`);
  });
} catch (e) {
  console.error('无法启动 Swagger UI 服务器:', e);
} 
