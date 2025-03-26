#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import yaml
import json
import logging
import requests
import math
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

class Logger:
    _instance = None
    
    def __new__(cls, name='NewBotAI'):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup_logger(name)
        return cls._instance
    
    def _setup_logger(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 检查处理器是否已存在，如果存在则先清除
        if self.logger.handlers:
            self.logger.handlers.clear()
        
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
    
    def __init__(self, name='NewBotAI'):
        pass  # 初始化在__new__中已完成
    
    def info(self, msg):
        self.logger.info(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)

# 全局变量用于追踪进度
total_accounts = 0
processed_accounts = 0

# 用户代理列表
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.2623.75",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
]

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

def get_random_ip() -> str:
    """生成随机IP地址，用于X-Forwarded-For头"""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def calculate_backoff_time(retries: int, base_delay: float = 5.0, max_delay: float = 60.0) -> float:
    """根据失败次数计算指数退避等待时间"""
    delay = min(base_delay * (2 ** retries) + random.uniform(0, 1), max_delay)
    return delay

def update_progress():
    """更新并打印进度信息"""
    global processed_accounts, total_accounts
    processed_accounts += 1
    progress = (processed_accounts / total_accounts) * 100 if total_accounts > 0 else 0
    print(f"\r处理进度: [{processed_accounts}/{total_accounts}] {progress:.1f}%", end="", flush=True)
    if processed_accounts == total_accounts:
        print()  # 完成后换行

def sign_in_account(username: str, cookies: Dict, batch_id: int = 0, retry_count: int = 0, max_retries: int = 3) -> Dict:
    """执行签到，支持429限流错误重试"""
    logger = Logger()
    sign_url = 'https://openai.newbotai.cn/api/user/clock_in?turnstile='
    
    # 随机选择用户代理
    user_agent = random.choice(USER_AGENTS)
    # 生成随机IP
    fake_ip = get_random_ip()
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-store',
        'Connection': random.choice(['keep-alive', 'close']),
        'Content-Length': '0',
        'Origin': 'https://openai.newbotai.cn',
        'Referer': f'https://openai.newbotai.cn/profile?t={int(time.time())}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': user_agent,
        'VoApi-User': cookies.get('voapi_user', ''),
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': random.choice(['"macOS"', '"Windows"', '"Linux"']),
        'X-Forwarded-For': fake_ip
    }
    
    cookies_dict = {'session': cookies.get('session', '')}
    
    if retry_count == 0:
        logger.info(f"[批次{batch_id}] 签到账号: {username}，VoApi-User: {cookies.get('voapi_user', '')}")
    else:
        logger.info(f"[批次{batch_id}] 第{retry_count}次重试签到账号: {username}")
    
    try:
        response = requests.post(sign_url, headers=headers, cookies=cookies_dict)
        logger.info(f"[批次{batch_id}] API响应状态码: {response.status_code}")
        
        # 处理429限流错误
        if response.status_code == 429:
            if retry_count < max_retries:
                # 指数退避策略，每次重试等待时间增加
                wait_time = calculate_backoff_time(retry_count)
                logger.warning(f"[批次{batch_id}] 遇到限流(429)，等待{wait_time:.1f}秒后重试...")
                time.sleep(wait_time)
                return sign_in_account(username, cookies, batch_id, retry_count + 1, max_retries)
            else:
                update_progress()  # 更新进度
                return {
                    'username': username,
                    'status': '失败',
                    'message': '达到最大重试次数，限流问题未解决'
                }
        
        try:
            result = response.json()
            logger.info(f"[批次{batch_id}] API响应内容: {result}")
            
            # 处理签到成功的情况
            if result.get('code') == 200 or (result.get('success') is True):
                update_progress()  # 更新进度
                return {
                    'username': username,
                    'status': '成功',
                    'message': result.get('msg', result.get('message', '签到成功'))
                }
            # 处理已经签到过的情况
            elif "已经签到过" in result.get('message', ''):
                update_progress()  # 更新进度
                return {
                    'username': username,
                    'status': '成功',
                    'message': '今天已签到'
                }
            # 处理其他失败情况
            else:
                update_progress()  # 更新进度
                return {
                    'username': username,
                    'status': '失败',
                    'message': result.get('message', result.get('msg', '未知错误'))
                }
        except ValueError:
            logger.error(f"[批次{batch_id}] 解析JSON响应失败: {response.text[:100]}")
            update_progress()  # 更新进度
            return {
                'username': username,
                'status': '失败',
                'message': f"解析响应失败: {response.text[:50]}..."
            }
    except Exception as e:
        logger.error(f"[批次{batch_id}] 请求异常: {str(e)}")
        update_progress()  # 更新进度
        return {
            'username': username,
            'status': '失败',
            'message': str(e)
        }

def process_account_batch(batch: List[Tuple[str, Dict]], batch_id: int) -> List[Dict]:
    """处理一批账号"""
    logger = Logger()
    batch_results = []
    
    for i, (username, account_data) in enumerate(batch):
        # 获取cookies
        cookies = {
            'session': account_data.get('cookies', {}).get('session', ''),
            'voapi_user': str(account_data.get('id', ''))
        }
        
        if not cookies['session'] or not cookies['voapi_user']:
            logger.warning(f"[批次{batch_id}] 账号 {username} 的cookies不完整，跳过")
            batch_results.append({
                'username': username,
                'status': '失败',
                'message': 'cookies不完整'
            })
            update_progress()  # 更新进度
            continue
        
        # 执行签到
        result = sign_in_account(username, cookies, batch_id)
        batch_results.append(result)
        
        # 在批次内的账号之间添加随机延迟，避免频繁请求
        if i < len(batch) - 1:  # 如果不是批次中的最后一个账号
            delay = random.uniform(8, 15)  # 增加延迟时间
            logger.info(f"[批次{batch_id}] 等待 {delay:.1f} 秒后处理下一个账号")
            time.sleep(delay)
    
    return batch_results

def log_result(results: List[Dict]):
    """记录签到结果到sign.md文件"""
    with open('sign.md', 'a', encoding='utf-8') as f:
        # 写入当前时间
        f.write(f"## 签到时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 写入表头
        f.write('| 账号 | 状态 | 消息 |\n')
        f.write('|------|------|------|\n')
        
        # 写入结果
        for result in results:
            f.write(f"| {result['username']} | {result['status']} | {result['message']} |\n")
        
        # 写入统计信息
        success_count = sum(1 for r in results if r['status'] == '成功')
        fail_count = sum(1 for r in results if r['status'] == '失败')
        f.write(f"\n- 总计: {len(results)} 个账号\n")
        f.write(f"- 成功: {success_count} 个\n")
        f.write(f"- 失败: {fail_count} 个\n")
        f.write(f"- 成功率: {(success_count/len(results)*100):.1f}%\n")

def main():
    # 初始化日志记录器
    logger = Logger()
    logger.info("开始运行签到程序")
    
    try:
        global total_accounts, processed_accounts
        
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
        
        # 设置全局统计变量
        total_accounts = len(available_accounts)
        processed_accounts = 0
        
        logger.info(f"共有 {total_accounts} 个账号需要处理")
        
        # 记录处理时间
        start_time = time.time()
        
        # 配置参数
        batch_size = 5  # 每批处理的账号数量
        num_workers = 2  # 并行处理的批次数量
        inter_batch_delay = (30, 60)  # 批次之间的延迟范围（秒）
        
        # 分批处理
        batches = []
        for i in range(0, total_accounts, batch_size):
            batch_accounts = list(available_accounts.items())[i:i+batch_size]
            batches.append(batch_accounts)
        
        logger.info(f"账号已分为 {len(batches)} 个批次，每批最多 {batch_size} 个账号")
        
        all_results = []
        
        # 显示初始进度
        print(f"总计 {total_accounts} 个账号需要处理")
        print(f"\r处理进度: [0/{total_accounts}] 0.0%", end="", flush=True)
        
        # 使用线程池并行处理批次
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            batch_futures = {}
            
            # 启动前几个批次
            active_batches = min(num_workers, len(batches))
            for i in range(active_batches):
                batch_futures[executor.submit(process_account_batch, batches[i], i)] = i
            
            completed_batches = 0
            
            # 处理完成的批次并启动新批次
            while batch_futures:
                # 等待一个批次完成
                done, _ = concurrent.futures.wait(
                    batch_futures.keys(), 
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for future in done:
                    batch_id = batch_futures[future]
                    try:
                        batch_results = future.result()
                        all_results.extend(batch_results)
                        
                        success_count = sum(1 for r in batch_results if r['status'] == '成功')
                        fail_count = sum(1 for r in batch_results if r['status'] == '失败')
                        
                        logger.info(f"批次 {batch_id} 完成处理，成功: {success_count} 个，失败: {fail_count} 个")
                        
                        # 删除已完成的任务
                        del batch_futures[future]
                        completed_batches += 1
                        
                        # 如果还有未处理的批次，启动新批次
                        next_batch_id = active_batches
                        if next_batch_id < len(batches):
                            # 添加批次间随机延迟，减轻服务器负担
                            delay = random.uniform(inter_batch_delay[0], inter_batch_delay[1])
                            logger.info(f"等待 {delay:.1f} 秒后启动下一批次")
                            time.sleep(delay)
                            
                            batch_futures[executor.submit(process_account_batch, batches[next_batch_id], next_batch_id)] = next_batch_id
                            active_batches += 1
                    
                    except Exception as e:
                        logger.error(f"处理批次 {batch_id} 时发生错误: {str(e)}")
                        del batch_futures[future]
                        completed_batches += 1
        
        # 记录签到结果
        if all_results:
            log_result(all_results)
            logger.info(f"签到结果已记录到 sign.md")
        
        # 计算总耗时
        total_time = time.time() - start_time
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = ""
        if hours > 0:
            time_str += f"{int(hours)}小时"
        if minutes > 0:
            time_str += f"{int(minutes)}分"
        time_str += f"{int(seconds)}秒"
        
        # 打印统计信息
        success_count = sum(1 for r in all_results if r['status'] == '成功')
        fail_count = sum(1 for r in all_results if r['status'] == '失败')
        
        logger.info("所有账号处理完成")
        logger.info(f"总耗时: {time_str}")
        logger.info(f"成功: {success_count} 个")
        logger.info(f"失败: {fail_count} 个")
        if total_accounts > 0:
            logger.info(f"成功率: {(success_count/total_accounts*100):.1f}%")
        
        print(f"\n处理完成! 成功: {success_count} 个，失败: {fail_count} 个，总耗时: {time_str}")
        
    except Exception as e:
        logger.error(f"程序执行出错：{str(e)}")
        raise

if __name__ == "__main__":
    main() 
