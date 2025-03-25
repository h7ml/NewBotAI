import json
import subprocess
import time
import random
import logging
from typing import Dict, Optional
from datetime import datetime
import os

# 确保logs目录存在
os.makedirs('./logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/token.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def mask_sensitive_info(text: str) -> str:
    """遮蔽敏感信息"""
    text = str(text)
    text = text.replace(text, '******') if 'session=' in text else text
    return text

def load_cookies() -> Dict:
    """从cookies_only.json加载cookies"""
    try:
        with open('cookies_only.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载cookies失败: {str(e)}")
        return {}

def get_token_list(session: str, user_id: str) -> Dict:
    """获取token列表"""
    curl_command = [
        'curl',
        '-s', '-S',  # 静默模式但显示错误
        'https://openai.newbotai.cn/api/token/?p=1&size=10',
        '-H', 'Accept: application/json, text/plain, */*',
        '-H', 'Accept-Language: zh-CN,zh;q=0.9',
        '-H', 'Cache-Control: no-store',
        '-H', 'Connection: keep-alive',
        '-i',
        '-b', f'session={session}',
        '-H', 'Referer: https://openai.newbotai.cn/token',
        '-H', 'Sec-Fetch-Dest: empty',
        '-H', 'Sec-Fetch-Mode: cors',
        '-H', 'Sec-Fetch-Site: same-origin',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        '-H', f'VoApi-User: {user_id}',
        '-H', 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        '-H', 'sec-ch-ua-mobile: ?0',
        '-H', 'sec-ch-ua-platform: "macOS"'
    ]
    
    try:
        process = subprocess.Popen(
            curl_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logging.error(f"获取token列表失败: {stderr.strip()}")
            return {}
        
        # 提取HTTP响应体(跳过头部)
        parts = stdout.split('\r\n\r\n')
        if len(parts) <= 1:
            parts = stdout.split('\n\n')
        
        if len(parts) > 1:
            body = parts[-1].strip()
            # 查找JSON开始的位置（第一个{字符）
            json_start = body.find('{')
            if json_start >= 0:
                result = body[json_start:]
                try:
                    data = json.loads(result)
                    if not data.get('data'):
                        logging.error(f"获取token列表返回无效数据: {result[:200]}...")
                    return data
                except json.JSONDecodeError:
                    logging.error(f"获取token列表返回非JSON数据: {result[:200]}...")
                    return {}
        
        # 如果上述方法失败，尝试直接查找JSON
        json_start = stdout.find('{"data"')
        if json_start >= 0:
            json_text = stdout[json_start:]
            try:
                data = json.loads(json_text)
                if not data.get('data'):
                    logging.error(f"获取token列表返回无效数据: {json_text[:200]}...")
                return data
            except json.JSONDecodeError:
                # 如果不是完整JSON，尝试找到最后一个}
                json_end = json_text.rfind('}') + 1
                if json_end > 0:
                    result = json_text[:json_end]
                    try:
                        data = json.loads(result)
                        if not data.get('data'):
                            logging.error(f"获取token列表返回无效数据: {result[:200]}...")
                        return data
                    except json.JSONDecodeError:
                        pass
        
        logging.error(f"无法从响应中提取JSON数据: {stdout[:200]}...")
        return {}
            
    except Exception as e:
        logging.error(f"获取token列表异常: {str(e)}")
        return {}

def create_token(session: str, user_id: str, name: str) -> bool:
    """创建新token"""
    data = {
        "name": name,
        "remain_quota": 500000000,
        "expired_time": -1,
        "unlimited_quota": True,
        "model_limits_enabled": False,
        "model_limits": "",
        "allow_ips": "",
        "group": ""
    }
    
    curl_command = [
        'curl',
        '-s', '-S',
        'https://openai.newbotai.cn/api/token/',
        '-X', 'POST',
        '-H', 'Accept: application/json, text/plain, */*',
        '-H', 'Accept-Language: zh-CN,zh;q=0.9',
        '-H', 'Cache-Control: no-store',
        '-H', 'Connection: keep-alive',
        '-H', 'Content-Type: application/json',
        '-b', f'session={session}',
        '-H', 'Origin: https://openai.newbotai.cn',
        '-H', 'Referer: https://openai.newbotai.cn/token',
        '-H', 'Sec-Fetch-Dest: empty',
        '-H', 'Sec-Fetch-Mode: cors',
        '-H', 'Sec-Fetch-Site: same-origin',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        '-H', f'VoApi-User: {user_id}',
        '-H', 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        '-H', 'sec-ch-ua-mobile: ?0',
        '-H', 'sec-ch-ua-platform: "macOS"',
        '--data-raw', json.dumps(data)
    ]
    
    try:
        process = subprocess.Popen(
            curl_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logging.error(f"创建token失败: {stderr.strip()}")
            return False
        
        try:
            response = json.loads(stdout)
            if not response.get('success', False):
                logging.error(f"创建token返回失败: {stdout[:200]}...")
            return response.get('success', False)
        except json.JSONDecodeError:
            logging.error(f"创建token返回非JSON数据: {stdout[:200]}...")
            return False
            
    except Exception as e:
        logging.error(f"创建token异常: {str(e)}")
        return False

def format_timestamp(timestamp: int) -> str:
    """将时间戳格式化为指定格式"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "永不过期"

def update_token_md(token_info: Dict, is_first: bool = False) -> None:
    """更新token.md文件"""
    try:
        # 构建Markdown表格内容
        header = "| 名称 | 密钥 | 状态 | 已用额度 | 剩余额度 | 创建时间 | 过期时间 |\n"
        separator = "|------|------|------|----------|----------|----------|----------|\n"
        
        # 格式化token信息
        status = "已启用" if token_info.get('status') == 1 else "未启用"
        used_quota = f"${token_info.get('used_quota', 0):.2f}"
        remain_quota = "无限制" if token_info.get('unlimited_quota') else str(token_info.get('remain_quota', 0))
        created_time = format_timestamp(token_info.get('created_time', 0))
        expired_time = "永不过期" if token_info.get('expired_time', -1) == -1 else format_timestamp(token_info.get('expired_time'))
        
        row = f"| {token_info.get('name', '')} | sk-{token_info.get('key', '')} | {status} | {used_quota} | {remain_quota} | {created_time} | {expired_time} |\n"
        
        # 写入文件
        mode = 'w' if is_first else 'a'  # 第一次写入时使用覆盖模式，之后使用追加模式
        with open('token.md', mode, encoding='utf-8') as f:
            if is_first:  # 只在第一次写入表头
                f.write(header + separator)
            f.write(row)
        
        logging.info("token.md更新成功")
    except Exception as e:
        logging.error(f"更新token.md失败: {str(e)}")

def main():
    """主函数"""
    try:
        # 加载cookies
        cookies = load_cookies()
        if not cookies:
            logging.error("未找到cookies")
            return
        
        # 清空token.md文件
        try:
            with open('token.md', 'w', encoding='utf-8') as f:
                pass
            logging.info("清空token.md文件成功")
        except Exception as e:
            logging.error(f"清空token.md文件失败: {str(e)}")
        
        is_first = True  # 标记是否是第一次写入
        for username, cookie_data in cookies.items():
            session = cookie_data.get('cookies', {}).get('session')
            if not session:
                logging.warning(f"账号 {username} 未找到session")
                continue
            
            logging.info(f"正在处理账号: {username}")
            
            user_id = str(cookie_data.get('id'))
            if not user_id:
                logging.error(f"账号 {username} 未找到用户ID")
                continue
            
            logging.info(f"账号 {username} 的用户ID为: {user_id}")
            
            # 获取token列表
            token_list = get_token_list(session, user_id)
            records = token_list.get('data', {}).get('records', [])
            
            if not records:
                logging.info(f"账号 {username} 未找到token，开始创建")
                if create_token(session, user_id, username):
                    logging.info("token创建成功，重新获取token列表")
                    time.sleep(2)  # 等待2秒让服务器处理
                    token_list = get_token_list(session, user_id)
                    records = token_list.get('data', {}).get('records', [])
                else:
                    logging.error("token创建失败")
                    continue
            
            if records:
                # 更新token.md
                update_token_md(records[0], is_first)
                is_first = False  # 第一次写入后设置为False
                logging.info(f"账号 {username} 处理完成")
            else:
                logging.error(f"账号 {username} 未能获取到token信息")
            
            # 添加随机延迟
            delay = random.uniform(3, 5)
            logging.info(f"等待 {delay:.1f} 秒后处理下一个账号")
            time.sleep(delay)
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()
