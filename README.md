# NewBotAI 自动注册与签到脚本

<div align="center" style="margin: 20px 0; padding: 15px; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%); border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">

<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-bottom: 10px;">

[![Auto Sign CI](https://img.shields.io/badge/🤖_Auto_Sign-Passing-success?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/h7ml/NewBotAI/actions/workflows/sign.yml)
[![Python Version](https://img.shields.io/badge/Python-3.6+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

</div>

<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">

[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square&logo=open-source-initiative&logoColor=white)](https://github.com/h7ml/NewBotAI/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/h7ml/NewBotAI?style=flat-square&logo=github&logoColor=white&color=yellow)](https://github.com/h7ml/NewBotAI/stargazers)
[![Forks](https://img.shields.io/github/forks/h7ml/NewBotAI?style=flat-square&logo=github&logoColor=white&color=blue)](https://github.com/h7ml/NewBotAI/network)
[![Issues](https://img.shields.io/github/issues/h7ml/NewBotAI?style=flat-square&logo=github&logoColor=white&color=orange)](https://github.com/h7ml/NewBotAI/issues)

</div>

</div>

## 📌 项目简介

🌟 **NewBotAI 自动注册与签到脚本** 是一个功能强大的工具，旨在帮助用户在 NewBotAI 平台上轻松完成账号批量注册、签到任务以及账户管理。通过此脚本，你可以尽享 NewBotAI 提供的 **免费试用988种 AI 模型** 的福利！

> **NewBotAI** 提供了丰富的 AI 模型资源，每日签到即可获得 $50 点数，注册即送 $50 点数，让你白嫖多种 AI 模型，无需额外投入。
---

- **轻松批量注册账号**
- **管理多个账户**
- **自动完成每日签到，领取平台奖励**

> **NewBotAI 平台亮点：**
>
> - 提供 **988 种 AI 模型** 免费试用
> - 注册即赠送 **50 美元** 账户余额
> - 每日签到再送 **50 美元**

---

## ✨ 功能特点

- **批量注册**：支持自动注册大量账户。
- **多账户管理**：通过 YAML 文件轻松管理多个账户。
- **自动签到**：模拟人工操作，降低账号被封风险。
- **日志记录**：详细记录签到结果及账户余额。
- **灵活配置**：支持自定义浏览器设置和命令行工具管理。

---

## 📦 环境安装

1. 克隆项目代码：

   ```bash
   git clone https://github.com/h7ml/NewBotAI.git
   cd NewBotAI
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

### 主要依赖

| 依赖名称           | 用途                                   |
|--------------------|--------------------------------------|
| **DrissionPage**   | 浏览器自动化操作                     |
| **PyYAML**         | 管理 YAML 配置文件                   |
| **python-dateutil**| 日期与时间处理                       |
| **playwright**     | `register.py` 中的自动化操作         |
| **selenium**       | `sign.py` 中的自动化操作             |
| **webdriver-manager** | 自动管理 WebDriver                |

---

## ⚙️ 配置文件说明

1. 复制模板配置文件：

   ```bash
   cp config.yaml.example config.yaml
   ```

2. 编辑 `config.yaml`，添加账户信息：

   ```yaml
   accounts:
     - username: "your_email1"
       password: "your_password1"
     - username: "your_email2"
       password: "your_password2"
   ```

### 配置文件特点

- **自动创建**：如果配置文件不存在，脚本会自动生成。
- **追加模式**：注册的新账号会自动追加至配置文件。
- **灵活管理**：支持通过命令行工具管理账号。

---

## 🚀 使用方法

### 1. 命令行工具

通过 `main.py` 统一管理所有功能：

```bash
# 查看帮助信息
python main.py

# 注册账号
python main.py register --num-accounts 100 --show-browser

# 执行签到
python main.py sign

# 管理账号配置
python main.py config add -u username1 -p password1  # 添加单个账号
python main.py config add -f accounts.csv           # 批量导入账号
python main.py config list                          # 列出所有已配置账号
python main.py config clear --confirm              # 清空所有账号
```

---

### 2. 批量注册账号

使用 `register.py` 脚本快速注册账号：

```bash
# 默认无头模式，注册 1000 个账号
python register.py

# 显示浏览器窗口
python register.py --show-browser

# 指定注册数量
python register.py --num-accounts 500
```

> **提示**：注册的账号会自动保存到以下文件：
>
> - `accounts.txt`：保存所有生成的账号名。
> - `config.yaml`：成功注册的账号及密码。

---

### 3. 自动签到

使用 `sign.py` 脚本完成自动签到：

```bash
python sign.py
```

签到完成后，结果将记录在 `logs` 目录下的日志文件中。

---

### 4. GitHub Actions 自动签到

本项目支持使用 **GitHub Actions** 每日自动签到。

#### 配置步骤

1. **Fork 此仓库** 到你的 GitHub 账号。
2. 在仓库的 `Settings -> Secrets and variables -> Actions` 中添加以下 Secret：
   - `NEWBOTAI_ACCOUNTS`：包含账号信息的 JSON 数组，格式如下：

     ```json
     [
       {"username": "账号1", "password": "密码1"},
       {"username": "账号2", "password": "密码2"}
     ]
     ```

3. GitHub Actions 将在每天 UTC 时间 0 点（北京时间 8 点）自动运行签到脚本。
4. 你也可以在 `Actions` 页面手动触发签到工作流。

#### 查看运行结果

- 在仓库的 Actions 标签页查看运行日志。
- 每次签到成功后，签到结果将记录在日志中。

---

## 📋 日志与文件说明

- **日志文件**：保存在 `logs` 目录下，按日期生成独立的日志文件。
- **重要文件**：
  - `main.py`: 统一命令行工具。
  - `register.py`: 用于批量注册账号。
  - `sign.py`: 用于每日签到。
  - `config.yaml`: 账户配置文件。
  - `accounts.txt`: 生成的账号列表。
  - `requirements.txt`: 依赖项列表。

---

## 🛠️ 常见问题

### 1. 如何解决依赖安装失败？

请确保您的 Python 版本为 **3.6 或更高**，并使用 `pip` 安装依赖。如果遇到问题，尝试升级 `pip`：

```bash
pip install --upgrade pip
```

### 2. GitHub Actions 未自动执行签到？

请确认 `NEWBOTAI_ACCOUNTS` Secret 已正确配置，且仓库中的 Actions 功能已启用。

---

## 🤝 贡献指南

欢迎开发者为本项目贡献代码！您可以通过以下方式参与：

1. 提交 Issue 反馈问题或建议。
2. Fork 本仓库并提交 Pull Request。
3. 添加新功能或优化现有代码。

---

## 📄 开源协议

本项目基于 [MIT License](https://github.com/h7ml/NewBotAI/blob/main/LICENSE) 开源，欢迎自由使用与修改。

---

## 📞 联系我们

- **Email**: <h7ml@qq.com>
- **GitHub**: [h7ml/NewBotAI](https://github.com/h7ml/NewBotAI)
