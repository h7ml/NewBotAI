import random
import string
import time
import yaml
import argparse
import requests
from pathlib import Path
from typing import Dict
from datetime import datetime
import os
import logging

class Logger:
    def __init__(self, name='NewBotAI'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 确保日志目录存在
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器 - 记录所有日志
        log_file = os.path.join(log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器 - 记录INFO及以上级别
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)

def generate_random_username():
    """生成随机用户名"""
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"temp_{random_suffix}"

def generate_accounts(num_accounts=10):
    """生成指定数量的随机账号"""
    accounts = []
    used_suffixes = set()
    
    while len(accounts) < num_accounts:
        username = generate_random_username()
        suffix = username.split('_')[1]
        if suffix not in used_suffixes:
            used_suffixes.add(suffix)
            accounts.append(username)
    
    # 保存到accounts.txt
    with open('accounts.txt', 'w') as f:
        for account in accounts:
            f.write(f"{account}\n")
    
    return accounts

def load_config() -> Dict:
    """加载配置文件"""
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {'accounts': []}
    return {'accounts': []}

def save_config(config: Dict) -> None:
    """保存配置文件，保持YAML格式一致性，使用追加模式而非覆盖"""
    config_path = Path('config.yaml')
    
    # 如果文件不存在，直接创建并写入
    if not config_path.exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)
        print("配置文件不存在，已创建新文件")
        return
    
    # 如果文件存在，加载现有配置并合并
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            existing_config = yaml.safe_load(f) or {'accounts': []}
        
        # 确保accounts键存在
        if 'accounts' not in existing_config:
            existing_config['accounts'] = []
            
        # 检查是否有重复账号，避免重复添加
        existing_usernames = {acc.get('username') for acc in existing_config['accounts']}
        new_accounts = [acc for acc in config['accounts'] if acc.get('username') not in existing_usernames]
        
        # 追加新账号
        existing_config['accounts'].extend(new_accounts)
        
        # 写回文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(existing_config, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)
        
        print(f"已追加 {len(new_accounts)} 个新账号到配置文件")
    except Exception as e:
        print(f"更新配置文件时出错: {str(e)}")
        # 出错时尝试直接覆盖写入
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)
        print("出错后已重新写入配置文件")

def register_account(username: str, password: str, max_retries: int = 3) -> bool:
    """使用API注册单个账号，带重试机制"""
    url = 'https://openai.newbotai.cn/api/user/register?turnstile='
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-store',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://openai.newbotai.cn',
        'Referer': 'https://openai.newbotai.cn/register?aff=DsaD',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    
    data = {
        "username": username,
        "password": password,
        "password2": password,
        "email": "",
        "verification_code": "",
        "aff_code": "DsaD"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response_json = response.json()
            
            if response_json.get('success'):
                print(f"账号 {username} 注册成功！")
                return True
            else:
                error_msg = response_json.get('message', '未知错误')
                print(f"账号 {username} 注册失败（尝试 {attempt + 1}/{max_retries}）：{error_msg}")
                if "已存在" in error_msg:  # 如果是用户名已存在，不再重试
                    return False
        except Exception as e:
            print(f"注册过程出错（尝试 {attempt + 1}/{max_retries}）：{str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 5 秒后重试...")
                time.sleep(5)
        
        # 在重试之前等待
        if attempt < max_retries - 1:
            time.sleep(2)
    
    return False

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量注册账号脚本')
    parser.add_argument('--num', type=int, default=10, help='需要注册的账号数量，默认为10')
    parser.add_argument('--password', type=str, default='autoregister@123', help='账号密码，默认为autoregister@123')
    args = parser.parse_args()

    logger = Logger()
    try:
        # 生成随机账号
        logger.info(f"开始生成 {args.num} 个随机账号...")
        accounts = generate_accounts(args.num)
        
        total_accounts = len(accounts)
        logger.info(f"成功生成 {total_accounts} 个随机账号")
        
        # 准备注册并保存的账号列表
        registered_accounts = []
        success_count = 0
        fail_count = 0
        
        for i, username in enumerate(accounts, 1):
            logger.info(f"\n开始注册第 {i}/{total_accounts} 个账号: {username}")
            
            # 执行注册
            success = register_account(username, args.password)
            
            if success:
                success_count += 1
                # 添加到已注册账号列表
                registered_accounts.append({
                    'username': username,
                    'password': args.password
                })
                logger.info(f"账号 {username} 注册成功并已添加到列表")
            else:
                fail_count += 1
                logger.warning(f"账号 {username} 注册失败，跳过")
            
            # 随机延迟，模拟人工操作
            if i < total_accounts:  # 如果不是最后一个账号
                delay = random.uniform(2, 4)
                logger.info(f"等待 {delay:.1f} 秒后继续...")
                time.sleep(delay)
        
        # 保存到配置文件
        if registered_accounts:
            config = {'accounts': registered_accounts}
            save_config(config)
            logger.info(f"已将 {len(registered_accounts)} 个成功注册的账号保存到配置文件")
        
        # 打印统计信息
        logger.info(f"\n注册完成！")
        logger.info(f"成功：{success_count} 个")
        logger.info(f"失败：{fail_count} 个")
        if total_accounts > 0:
            logger.info(f"成功率：{(success_count/total_accounts*100):.1f}%")
        
    except Exception as e:
        logger.error(f"程序执行出错：{str(e)}")
        raise

if __name__ == "__main__":
    main() 
