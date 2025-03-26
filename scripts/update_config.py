#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import json
import logging
from pathlib import Path

# 确保日志目录存在
Path('logs').mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/update_config.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('update_config')

def mask_sensitive_info(text):
    """脱敏敏感信息"""
    if not text:
        return ""
    if len(text) <= 4:
        return '*' * len(text)
    return text[:2] + '*' * (len(text) - 4) + text[-2:]

def update_config_with_env_accounts():
    """
    从环境变量中获取账号信息，并将其合并到config.yaml文件中
    环境变量格式为JSON数组：[{"username": "user1", "password": "pass1"}, ...]
    """
    # 获取当前脚本所在目录的父目录（项目根目录）
    root_dir = Path(__file__).parent.parent.absolute()
    config_path = root_dir / 'config.yaml'
    
    logger.info(f"开始更新配置文件: {config_path}")
    
    # 检查环境变量是否存在
    env_accounts = os.environ.get('NEWBOTAI_ACCOUNTS')
    if not env_accounts:
        logger.warning("环境变量 NEWBOTAI_ACCOUNTS 不存在，跳过更新")
        return
    
    try:
        # 解析环境变量中的账号数据
        env_accounts_data = json.loads(env_accounts)
        valid_accounts = [acc for acc in env_accounts_data if 'username' in acc and 'password' in acc]
        
        if len(valid_accounts) != len(env_accounts_data):
            logger.warning(f"发现 {len(env_accounts_data) - len(valid_accounts)} 个无效账号格式被忽略")
        
        logger.info(f"从环境变量中加载了 {len(valid_accounts)} 个有效账号")
        
        # 读取现有配置文件
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                logger.info(f"成功读取现有配置文件")
            except Exception as e:
                logger.error(f"读取配置文件失败: {e}")
                config = {}
        else:
            logger.info(f"配置文件不存在，将创建新文件")
            config = {}
        
        # 确保配置中有accounts字段
        if 'accounts' not in config:
            config['accounts'] = []
            logger.info("初始化accounts字段")
        
        # 创建一个集合来存储已有的账号（用户名和密码组合）
        existing_accounts = {(acc['username'], acc['password']) for acc in config['accounts']}
        logger.info(f"现有配置中包含 {len(existing_accounts)} 个账号")
        
        # 添加新账号（去重）
        added_count = 0
        for account in valid_accounts:
            account_tuple = (account['username'], account['password'])
            if account_tuple not in existing_accounts:
                config['accounts'].append({
                    'username': account['username'],
                    'password': account['password']
                })
                existing_accounts.add(account_tuple)
                added_count += 1
                logger.debug(f"添加新账号: {mask_sensitive_info(account['username'])}")
        
        if added_count > 0:
            logger.info(f"添加了 {added_count} 个新账号到配置文件")
        else:
            logger.info("没有发现新账号需要添加")
        
        # 保存更新后的配置文件
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            logger.info(f"配置文件已更新，现在共有 {len(config['accounts'])} 个账号")
        except Exception as e:
            logger.error(f"保存配置文件时出错: {e}")
    
    except json.JSONDecodeError as e:
        logger.error(f"环境变量 NEWBOTAI_ACCOUNTS 不是有效的JSON格式: {e}")
        # 尝试查看问题部分
        preview = env_accounts[:50] + '...' if len(env_accounts) > 50 else env_accounts
        logger.error(f"JSON内容预览: {preview}")
    except Exception as e:
        logger.error(f"更新配置文件时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        logger.info("开始执行账号配置更新脚本")
        update_config_with_env_accounts()
        logger.info("账号配置更新脚本执行完成")
    except Exception as e:
        logger.critical(f"脚本执行过程中发生严重错误: {str(e)}")
        import traceback
        logger.critical(traceback.format_exc()) 
