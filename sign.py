#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import yaml
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List

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

def load_config() -> Dict:
    """加载配置文件"""
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {'accounts': []}
    return {'accounts': []}

def load_available_accounts() -> Dict:
    """加载cookies_only.json中已有的账号信息"""
    cookies_path = Path('cookies_only.json')
    if not cookies_path.exists():
        return {}
    
    try:
        with open(cookies_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载cookies文件失败: {str(e)}")
        return {}

def load_cookies(username: str) -> Dict:
    """加载账号对应的cookies信息"""
    cookies_path = Path('cookies_only.json')
    if not cookies_path.exists():
        return {}
    
    try:
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
            
        # 查找指定用户名的cookies
        user_data = cookies_data.get(username)
        if user_data:
            return {
                'session': user_data.get('cookies', {}).get('session', ''),
                'voapi_user': str(user_data.get('id', ''))
            }
    except Exception as e:
        print(f"加载cookies文件失败: {str(e)}")
    
    return {}

def sign_in_account(username: str, cookies: Dict) -> Dict:
    """执行签到"""
    logger = Logger()
    sign_url = 'https://openai.newbotai.cn/api/user/clock_in?turnstile='
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-store',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Origin': 'https://openai.newbotai.cn',
        'Referer': 'https://openai.newbotai.cn/profile',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'VoApi-User': cookies.get('voapi_user', ''),
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    
    cookies_dict = {'session': cookies.get('session', '')}
    
    logger.info(f"签到账号: {username}，VoApi-User: {cookies.get('voapi_user', '')}")
    
    try:
        response = requests.post(sign_url, headers=headers, cookies=cookies_dict)
        logger.info(f"API响应状态码: {response.status_code}")
        
        try:
            result = response.json()
            logger.info(f"API响应内容: {result}")
            
            # 处理签到成功的情况
            if result.get('code') == 200 or (result.get('success') is True):
                return {
                    'username': username,
                    'status': '成功',
                    'message': result.get('msg', result.get('message', '签到成功'))
                }
            # 处理已经签到过的情况
            elif "已经签到过" in result.get('message', ''):
                return {
                    'username': username,
                    'status': '成功',
                    'message': '今天已签到'
                }
            # 处理其他失败情况
            else:
                return {
                    'username': username,
                    'status': '失败',
                    'message': result.get('message', result.get('msg', '未知错误'))
                }
        except ValueError:
            logger.error(f"解析JSON响应失败: {response.text[:100]}")
            return {
                'username': username,
                'status': '失败',
                'message': f"解析响应失败: {response.text[:50]}..."
            }
    except Exception as e:
        logger.error(f"请求异常: {str(e)}")
        return {
            'username': username,
            'status': '失败',
            'message': str(e)
        }

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
    existing_cookies = {}
    if cookies_path.exists():
        try:
            with open(cookies_path, 'r', encoding='utf-8') as f:
                existing_cookies = json.load(f)
        except Exception as e:
            logger = Logger()
            logger.error(f"读取cookies文件失败: {str(e)}")
            existing_cookies = {}
    
    # 更新对应用户的cookies
    existing_cookies[username] = {
        'cookies': {
            'session': cookies_data['session']
        },
        'id': cookies_data['voapi_user']
    }
    
    # 保存到文件
    with open(cookies_path, 'w', encoding='utf-8') as f:
        json.dump(existing_cookies, f, indent=2, ensure_ascii=False)

def log_result(results: List[Dict]):
    """记录签到结果到sign.md文件"""
    with open('sign.md', 'a', encoding='utf-8') as f:
        # 写入表头
        f.write('| 账号 | 状态 | 消息 |\n')
        f.write('|------|------|------|\n')
        
        # 写入结果
        for result in results:
            f.write(f"| {result['username']} | {result['status']} | {result['message']} |\n")

def main():
    # 初始化日志记录器
    logger = Logger()
    logger.info("开始运行签到程序")
    
    try:
        # 清空上一次的签到结果
        sign_file = Path('sign.md')
        if sign_file.exists():
            logger.info("清空上一次的签到结果...")
            sign_file.unlink()  # 删除文件
        
        # 加载已有cookies的账号
        logger.info("加载cookies_only.json中的账号...")
        available_accounts = load_available_accounts()
        
        if not available_accounts:
            logger.error("cookies_only.json中没有可用的账号信息")
            return
        
        total_accounts = len(available_accounts)
        logger.info(f"共有 {total_accounts} 个账号需要处理")
        
        success_count = 0
        fail_count = 0
        
        # 遍历cookies_only.json中的账号
        sign_results = []
        for index, (username, account_data) in enumerate(available_accounts.items(), 1):
            logger.info(f"正在处理第 {index}/{total_accounts} 个账号: {username}")
            
            # 获取cookies
            cookies = {
                'session': account_data.get('cookies', {}).get('session', ''),
                'voapi_user': str(account_data.get('id', ''))
            }
            
            if not cookies['session'] or not cookies['voapi_user']:
                logger.warning(f"账号 {username} 的cookies不完整，跳过")
                sign_results.append({
                    'username': username,
                    'status': '失败',
                    'message': 'cookies不完整'
                })
                fail_count += 1
                continue
            
            # 执行签到
            result = sign_in_account(username, cookies)
            sign_results.append(result)
            
            status = result.get('status', '未知状态')
            if "成功" in status:
                success_count += 1
                logger.info(f"账号 {username} 签到成功")
            else:
                fail_count += 1
                logger.warning(f"账号 {username} 签到失败: {result.get('message', '未知错误')}")
            
            # 随机延迟，模拟人工操作
            if index < total_accounts:  # 如果不是最后一个账号
                delay = random.uniform(2, 4)
                logger.info(f"等待 {delay:.1f} 秒后处理下一个账号")
                time.sleep(delay)
        
        # 记录签到结果
        if sign_results:
            log_result(sign_results)
            logger.info(f"签到结果已记录到 sign.md")
        
        # 打印统计信息
        logger.info("所有账号处理完成")
        logger.info(f"成功：{success_count} 个")
        logger.info(f"失败：{fail_count} 个")
        if total_accounts > 0:
            logger.info(f"成功率：{(success_count/total_accounts*100):.1f}%")
    except Exception as e:
        logger.error(f"程序执行出错：{str(e)}")
        raise

if __name__ == "__main__":
    main() 
