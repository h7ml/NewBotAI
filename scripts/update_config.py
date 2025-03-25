#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('update_config')

def update_config_with_env_accounts():
    """
    从环境变量中获取账号信息，并将其合并到config.yaml文件中
    环境变量格式为JSON数组：[{"username": "user1", "password": "pass1"}, ...]
    """
    # 获取当前脚本所在目录的父目录（项目根目录）
    root_dir = Path(__file__).parent.parent.absolute()
    config_path = root_dir / 'config.yaml'
    
    # 检查环境变量是否存在
    env_accounts = os.environ.get('NEWBOTAI_ACCOUNTS')
    if not env_accounts:
        logger.info("环境变量 NEWBOTAI_ACCOUNTS 不存在，跳过更新")
        return
    
    try:
        # 解析环境变量中的账号数据
        env_accounts_data = json.loads(env_accounts)
        logger.info(f"从环境变量中加载了 {len(env_accounts_data)} 个账号")
        
        # 读取现有配置文件
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # 确保配置中有accounts字段
        if 'accounts' not in config:
            config['accounts'] = []
        
        # 创建一个集合来存储已有的账号（用户名和密码组合）
        existing_accounts = {(acc['username'], acc['password']) for acc in config['accounts']}
        
        # 添加新账号（去重）
        added_count = 0
        for account in env_accounts_data:
            if 'username' in account and 'password' in account:
                account_tuple = (account['username'], account['password'])
                if account_tuple not in existing_accounts:
                    config['accounts'].append({
                        'username': account['username'],
                        'password': account['password']
                    })
                    existing_accounts.add(account_tuple)
                    added_count += 1
        
        logger.info(f"添加了 {added_count} 个新账号到配置文件")
        
        # 保存更新后的配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
        
        logger.info(f"配置文件已更新，现在共有 {len(config['accounts'])} 个账号")
    
    except json.JSONDecodeError:
        logger.error("环境变量 NEWBOTAI_ACCOUNTS 不是有效的JSON格式")
    except Exception as e:
        logger.error(f"更新配置文件时出错: {e}")

if __name__ == "__main__":
    update_config_with_env_accounts() 
