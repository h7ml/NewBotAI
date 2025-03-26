# NewBotAI 自动注册与签到脚本

<div align="center">

[![Auto Sign CI](https://img.shields.io/badge/🤖_Auto_Sign-Passing-success?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/h7ml/NewBotAI/actions/workflows/sign.yml)
[![Python Version](https://img.shields.io/badge/Python-3.6+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square&logo=open-source-initiative&logoColor=white)](https://github.com/h7ml/NewBotAI/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/h7ml/NewBotAI?style=flat-square&logo=github&logoColor=white&color=yellow)](https://github.com/h7ml/NewBotAI/stargazers)
[![Forks](https://img.shields.io/github/forks/h7ml/NewBotAI?style=flat-square&logo=github&logoColor=white&color=blue)](https://github.com/h7ml/NewBotAI/network)
[![Issues](https://img.shields.io/github/issues/h7ml/NewBotAI?style=flat-square&logo=github&logoColor=white&color=orange)](https://github.com/h7ml/NewBotAI/issues)

</div>

## 📌 项目简介

NewBotAI 自动注册与签到脚本帮助用户在 NewBotAI 平台上完成账号批量注册、签到任务和账户管理，让您轻松享受**免费试用988种 AI 模型**的福利。

> **平台优势：** 每日签到获得 $50 点数，注册即送 $50 点数，无需额外投入。

## ✨ 核心功能

- **批量注册**：自动化创建大量账户
- **多账户管理**：通过 YAML 配置轻松管理账户
- **自动签到**：智能模拟人工操作，降低风险
- **日志记录**：详细跟踪签到结果与余额变化
- **灵活配置**：支持自定义浏览器与命令行管理

## 📦 快速开始

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/h7ml/NewBotAI.git
cd NewBotAI

# 安装依赖
pip install -r requirements.txt

# 准备配置文件
cp config.yaml.example config.yaml
```

### 主要依赖

| 依赖 | 用途 |
|------|------|
| DrissionPage | 浏览器自动化 |
| PyYAML | 配置管理 |
| playwright | 注册自动化 |
| selenium | 签到自动化 |
| webdriver-manager | WebDriver管理 |

## ⚙️ 配置说明

编辑 `config.yaml` 添加账户信息：

```yaml
accounts:
  - username: "your_email1"
    password: "your_password1"
  - username: "your_email2"
    password: "your_password2"
```

**特点：**

- 自动创建缺失的配置文件
- 注册新账号时自动追加至配置
- 支持命令行工具管理账号

## 🚀 使用指南

### 命令行工具

```bash
# 查看帮助
python main.py

# 注册账号
python main.py register --num-accounts 100 --show-browser

# 执行签到
python main.py sign

# 管理账号
python main.py config add -u username1 -p password1  # 添加账号
python main.py config add -f accounts.csv           # 批量导入
python main.py config list                          # 列出账号
python main.py config clear --confirm              # 清空账号
```

### 独立脚本

#### 批量注册

```bash
# 默认无头模式注册1000个账号
python register.py

# 显示浏览器窗口
python register.py --show-browser

# 指定注册数量
python register.py --num-accounts 500
```

注册的账号自动保存至 `accounts.txt` 和 `config.yaml`。

#### 自动签到

```bash
python sign.py
```

签到结果保存在 `logs` 目录下。

### API密钥管理与使用

成功注册并签到后，可以获取API密钥进行开发调用。所有可用的API密钥会自动记录在`token.md`文件中，格式如下：

| 名称 | 密钥 | 状态 | 已用额度 | 剩余额度 | 创建时间 | 过期时间 |
|------|------|------|----------|----------|----------|----------|
| temp_xxxx | sk-xxxxxxxx | 已启用 | $0.00 | 无限制 | 2025-03-26 xx:xx:xx | 永不过期 |

#### API调用示例

使用获取到的API密钥，可以直接调用NewBotAI提供的API服务：

```bash
curl https://openai.newbotai.cn/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-VefRuCzVAFDGiH0ep1T0CXeo26DMUu1EtEwh1tIKqd8B7rvR" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

返回结果示例：

```json
{
  "id": "chatcmpl-BFCoxEmiO1tI7Sl9jx0GMFJgrun5o",
  "object": "chat.completion",
  "created": 1742963903,
  "model": "gpt-3.5-turbo-0125",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！有什么可以帮助你的吗？"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 17,
    "total_tokens": 26
  },
  "system_fingerprint": "fp_0165350fbb"
}
```

#### 密钥优势

- **无限制额度**：所有密钥都提供无限制的使用额度
- **永久有效**：密钥永不过期，可长期使用
- **多密钥备选**：自动生成多个密钥，可根据需要轮换使用

#### 获取更多密钥

执行注册脚本可以获取更多账号和对应的API密钥：

```bash
python register.py --num-accounts 10
python get_token.py  # 从已注册账号获取API密钥
```

### GitHub Actions 自动签到

1. **Fork 此仓库**到您的GitHub账号
2. 添加 Secret：`NEWBOTAI_ACCOUNTS`，格式如下：

   ```json
   [
     {"username": "账号1", "password": "密码1"},
     {"username": "账号2", "password": "密码2"}
   ]
   ```

3. Actions 将在每天北京时间8点自动运行

## 📋 文件说明

- `main.py`: 统一命令行工具
- `register.py`: 批量注册账号
- `sign.py`: 每日签到
- `get_token.py`: 获取API密钥
- `token.md`: API密钥记录表
- `config.yaml`: 账户配置
- `accounts.txt`: 账号列表
- `logs/`: 日志目录

## 🛠️ 常见问题

1. **依赖安装失败？**
   确保Python版本≥3.6，尝试升级pip：

   ```bash
   pip install --upgrade pip
   ```

2. **Actions未自动执行？**
   检查Secret配置是否正确，Actions功能是否启用。

3. **API密钥无法使用？**
   确保账号已成功签到并获取了API密钥，检查`token.md`文件中密钥的状态是否为"已启用"。

## 🤝 参与贡献

欢迎通过以下方式参与：

- 提交Issue反馈问题
- Fork仓库并提交PR
- 添加新功能或优化代码

## 📄 开源协议

本项目基于 [MIT License](https://github.com/h7ml/NewBotAI/blob/main/LICENSE) 开源。

## 📞 联系方式

- **Email**: <h7ml@qq.com>
- **GitHub**: [h7ml/NewBotAI](https://github.com/h7ml/NewBotAI)
