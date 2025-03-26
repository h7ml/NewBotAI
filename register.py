import random
import string
import time
import yaml
import argparse
import requests
import json
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

def generate_accounts(num_accounts=1000):
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

def load_cookies(username: str) -> Dict:
    """加载账号对应的cookies信息"""
    cookies_path = Path('cookies_only.json')
    if not cookies_path.exists():
        return {}
    
    try:
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
            
        # 查找指定用户名的cookies
        for account in cookies_data:
            if account.get('username') == username:
                return {
                    'session': account.get('session', ''),
                    'voapi_user': account.get('voapi_user', '')
                }
    except Exception as e:
        print(f"加载cookies文件失败: {str(e)}")
    
    return {}

def sign_in_account(username: str, password: str, max_retries: int = 3) -> Dict:
    """使用API对单个账号执行签到，带重试机制"""
    logger = Logger()
    logger.info(f"开始执行账号 {username} 的签到")
    
    # 加载cookies
    cookies = load_cookies(username)
    if not cookies.get('session') or not cookies.get('voapi_user'):
        logger.warning(f"账号 {username} 的cookies不存在或不完整，尝试登录获取")
        cookies = login_account(username, password)
        if not cookies:
            logger.error(f"账号 {username} 登录失败，无法进行签到")
            return {'status': "登录失败", 'balance_info': None}
    
    url = 'https://openai.newbotai.cn/api/user/clock_in?turnstile='
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-store',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Cookie': f'session={cookies["session"]}',
        'Origin': 'https://openai.newbotai.cn',
        'Referer': 'https://openai.newbotai.cn/profile',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'VoApi-User': cookies['voapi_user'],
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试签到 (尝试 {attempt + 1}/{max_retries})")
            
            response = requests.post(url, headers=headers)
            response_json = response.json()
            
            if response_json.get('success'):
                logger.info(f"账号 {username} 签到成功！")
                
                # 获取余额信息
                balance_info = get_balance_info(cookies)
                
                return {
                    'status': "签到成功",
                    'balance_info': balance_info
                }
            else:
                error_msg = response_json.get('message', '未知错误')
                # 如果已经签到，算作成功
                if "今日已打卡" in error_msg:
                    logger.info(f"账号 {username} 今日已签到")
                    
                    # 获取余额信息
                    balance_info = get_balance_info(cookies)
                    
                    return {
                        'status': "今日已签到",
                        'balance_info': balance_info
                    }
                else:
                    logger.warning(f"账号 {username} 签到失败: {error_msg}")
                    
                    if "身份验证" in error_msg or "登录" in error_msg:
                        logger.info("尝试重新登录获取新cookies")
                        cookies = login_account(username, password)
                        if cookies:
                            headers['Cookie'] = f'session={cookies["session"]}'
                            headers['VoApi-User'] = cookies['voapi_user']
                            continue
                    
                    return {
                        'status': f"签到失败: {error_msg}",
                        'balance_info': None
                    }
        except Exception as e:
            logger.error(f"签到过程出错: {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"等待 5 秒后重试...")
                time.sleep(5)
        
        # 在重试之前等待
        if attempt < max_retries - 1:
            time.sleep(2)
    
    return {'status': "签到失败: 超过最大重试次数", 'balance_info': None}

def login_account(username: str, password: str) -> Dict:
    """登录账号并获取cookies"""
    logger = Logger()
    logger.info(f"尝试登录账号: {username}")
    
    url = 'https://openai.newbotai.cn/api/user/login'
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-store',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://openai.newbotai.cn',
        'Referer': 'https://openai.newbotai.cn/login',
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
        "password": password
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        cookies = response.cookies
        
        if not cookies.get('session'):
            logger.error(f"登录失败: 未获取到session")
            return {}
        
        # 解析返回的数据，获取VoApi-User
        response_json = response.json()
        if not response_json.get('success'):
            logger.error(f"登录失败: {response_json.get('message', '未知错误')}")
            return {}
        
        user_id = response_json.get('data', {}).get('id')
        if not user_id:
            logger.error("登录失败: 未获取到用户ID")
            return {}
        
        cookies_data = {
            'session': cookies.get('session'),
            'voapi_user': str(user_id)
        }
        
        # 更新cookies_only.json
        save_cookies(username, cookies_data)
        
        logger.info(f"登录成功，获取到cookies")
        return cookies_data
        
    except Exception as e:
        logger.error(f"登录过程出错: {str(e)}")
        return {}

def save_cookies(username: str, cookies_data: Dict) -> None:
    """保存cookies到文件"""
    cookies_path = Path('cookies_only.json')
    
    # 读取现有cookies
    existing_cookies = []
    if cookies_path.exists():
        try:
            with open(cookies_path, 'r', encoding='utf-8') as f:
                existing_cookies = json.load(f)
        except:
            existing_cookies = []
    
    # 查找并更新对应用户的cookies
    found = False
    for i, account in enumerate(existing_cookies):
        if account.get('username') == username:
            existing_cookies[i] = {
                'username': username,
                'session': cookies_data['session'],
                'voapi_user': cookies_data['voapi_user']
            }
            found = True
            break
    
    # 如果没找到，就添加新的
    if not found:
        existing_cookies.append({
            'username': username,
            'session': cookies_data['session'],
            'voapi_user': cookies_data['voapi_user']
        })
    
    # 保存到文件
    with open(cookies_path, 'w', encoding='utf-8') as f:
        json.dump(existing_cookies, f, indent=2, ensure_ascii=False)

def get_balance_info(cookies: Dict) -> Dict:
    """获取账户余额信息"""
    logger = Logger()
    logger.info("获取账户余额信息")
    
    url = 'https://openai.newbotai.cn/api/user/info'
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-store',
        'Connection': 'keep-alive',
        'Cookie': f'session={cookies["session"]}',
        'Referer': 'https://openai.newbotai.cn/profile',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'VoApi-User': cookies['voapi_user']
    }
    
    try:
        response = requests.get(url, headers=headers)
        response_json = response.json()
        
        if response_json.get('success') and response_json.get('data'):
            user_data = response_json['data']
            balance_info = {
                'balance': user_data.get('balance', 0),
                'consumed': user_data.get('used_balance', 0),
                'requests': user_data.get('user_request_count', 0)
            }
            logger.info(f"获取余额信息成功: {balance_info}")
            return balance_info
    except Exception as e:
        logger.error(f"获取余额信息失败: {str(e)}")
    
    return None

def log_result(account: str, status: str, balance_info: Dict = None):
    """记录签到结果到日志文件"""
    logger = Logger()
    try:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'{today}.md')
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"记录签到结果 - 账号: {account}, 状态: {status}")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'\n## 账号: {account}\n')
            f.write(f'- 时间: {timestamp}\n')
            f.write(f'- 状态: {status}\n')
            if balance_info:
                f.write('- 账户信息:\n')
                f.write(f'  - 当前余额: {balance_info["balance"]}\n')
                f.write(f'  - 历史消耗: {balance_info["consumed"]}\n')
                f.write(f'  - 请求次数: {balance_info["requests"]}\n')
            f.write('\n---\n')
        
        logger.info("签到结果已记录到日志文件")
    except Exception as e:
        logger.error(f"记录签到结果时出错: {e}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量签到脚本')
    args = parser.parse_args()

    logger = Logger()
    try:
        # 加载现有配置
        logger.info("加载配置文件...")
        config = load_config()
        
        if not config.get('accounts'):
            logger.error("配置文件中没有账号信息")
            return
        
        total_accounts = len(config['accounts'])
        logger.info(f"共有 {total_accounts} 个账号需要处理")
        
        success_count = 0
        fail_count = 0
        
        for i, account in enumerate(config['accounts'], 1):
            username = account.get('username')
            password = account.get('password')
            
            if not username or not password:
                logger.warning(f"第 {i} 个账号信息不完整，跳过")
                fail_count += 1
                continue
            
            logger.info(f"\n开始处理第 {i}/{total_accounts} 个账号: {username}")
            
            # 执行签到
            result = sign_in_account(username, password)
            status = result.get('status', '未知状态')
            balance_info = result.get('balance_info')
            
            # 记录日志
            log_result(username, status, balance_info)
            
            if "成功" in status or "已签到" in status:
                success_count += 1
            else:
                fail_count += 1
            
            # 随机延迟，模拟人工操作
            if i < total_accounts:  # 如果不是最后一个账号
                delay = random.uniform(2, 4)
                logger.info(f"等待 {delay:.1f} 秒后继续...")
                time.sleep(delay)
        
        # 打印统计信息
        logger.info(f"\n签到完成！")
        logger.info(f"成功：{success_count} 个")
        logger.info(f"失败：{fail_count} 个")
        logger.info(f"成功率：{(success_count/total_accounts*100):.1f}%")
        
    except Exception as e:
        logger.error(f"程序执行出错：{str(e)}")
        raise

if __name__ == "__main__":
    main() 
