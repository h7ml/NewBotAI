# NewBotAI 自动注册与签到脚本

这是一个用于 NewBotAI 平台的自动注册和签到脚本集合，支持账号批量注册、多账户管理和自动签到功能。

> NewBotAI 是一个可以白嫖多种Ai模型的平台，可以免费试用多种AI模型，目前可以白嫖988种模型。注册就送50刀，每日签到送50刀。

<img src="./screenhot/model.jpg" alt="model" />
<img src="https://img.shields.io/badge/Version-1.0.0-green" alt="Version" />

## 功能特点

- 支持账号批量自动注册
- 支持多账户配置和管理
- 模拟人工操作，降低被检测风险
- 自动记录签到结果和账户余额
- 支持自定义浏览器配置
- 详细的日志记录
- 命令行统一管理工具
- 灵活的账号配置管理

## 安装依赖

```bash
pip install -r requirements.txt
```

### 依赖项说明

- **DrissionPage**: 用于浏览器自动化
- **PyYAML**: 用于处理YAML配置文件
- **python-dateutil**: 用于日期时间处理
- **playwright**: 用于register.py脚本中的自动化操作
- **selenium**: 用于sign.py脚本中的自动化操作
- **webdriver-manager**: 用于自动管理WebDriver

## 配置说明

1. 复制并修改配置文件

```bash
cp config.yaml.example config.yaml
```

2. 编辑 `config.yaml` 文件，添加你的账户信息：

```yaml
accounts:
  - username: "your_email1"
    password: "your_password1"
  - username: "your_email2"
    password: "your_password2"
```

3. 配置文件说明：
   - 配置文件使用追加模式，不会覆盖已有账号
   - 成功注册的新账号会自动追加到配置文件
   - 如果配置文件不存在，则会自动创建
   - 可以通过命令行工具管理账号配置

## 使用方法

### 命令行工具

使用 `main.py` 统一命令行工具:

```bash
# 显示帮助信息
python main.py

# 注册账号
python main.py register --num-accounts 100 --show-browser

# 执行签到
python main.py sign

# 账号配置管理
python main.py config add -u username1 -p password1  # 添加单个账号
python main.py config add -f accounts.csv  # 批量导入账号
python main.py config list  # 列出所有配置的账号
python main.py config clear --confirm  # 清空所有账号
```

### 账号配置管理

管理config.yaml中的账号配置：

```bash
# 添加单个账号
python main.py config add -u username1 -p password1

# 从文件批量导入账号
# 文件格式支持：
# 1. 每行一个用户名（将使用默认密码）
# 2. 每行格式为 "username,password"
python main.py config add -f accounts.txt --default-password mypassword

# 列出所有已配置账号
python main.py config list

# 清空所有账号配置（需要确认）
python main.py config clear --confirm
```

### 账号注册

使用 `register.py` 脚本批量注册账号：

```bash
# 默认无头模式注册1000个账号
python register.py

# 显示浏览器窗口
python register.py --show-browser

# 指定注册数量
python register.py --num-accounts 500
```

注册的账号会自动保存到：

- `accounts.txt`：保存所有生成的账号名
- `config.yaml`：添加成功注册的账号及密码

### 账号签到

使用 `sign.py` 脚本执行自动签到：

```bash
python sign.py
```

## 日志说明

- 日志文件保存在 `logs` 目录下
- 按日期生成独立的markdown格式日志文件
- 记录每个账号的签到状态和余额信息
- 可查看详细的操作日志和错误信息

## 脚本文件说明

- `main.py`: 统一命令行工具，整合所有功能
- `register.py`: 批量注册账号
- `sign.py`: 自动签到
- `config.yaml`: 配置文件
- `accounts.txt`: 生成的账号列表
- `requirements.txt`: 依赖项列表

## 参数设置

### main.py 参数

## GitHub Actions 自动签到

本项目支持使用GitHub Actions自动执行每日签到任务。

### 配置步骤

1. Fork本仓库到你的GitHub账号
2. 在仓库的Settings -> Secrets and variables -> Actions中添加以下Secret:
   - `NEWBOTAI_ACCOUNTS`: 包含账号信息的JSON数组，格式如下：

     ```json
     [
       {"username": "账号1", "password": "密码1"},
       {"username": "账号2", "password": "密码2"}
     ]
     ```

3. GitHub Actions将按照预设的时间（每天UTC 0点，北京时间8点）自动运行签到脚本
4. 你也可以在Actions页面手动触发工作流运行

### 查看运行结果

- 在仓库的Actions标签页可以查看每次运行的详细日志
- 每次成功运行后，签到结果将记录在日志中
