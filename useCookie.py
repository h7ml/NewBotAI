import yaml
import json
from typing import Dict, List
import time
import logging
import random
import os
import subprocess
import re

# 确保logs目录存在
os.makedirs('./logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/cookies.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_accounts() -> List[Dict[str, str]]:
    """加载账号配置"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['accounts']

def mask_sensitive_info(text: str) -> str:
    """遮蔽敏感信息，如密码和cookie值"""
    # 遮蔽密码
    text = re.sub(r'password":"[^"]+', 'password":"******', text)
    # 遮蔽cookie值
    text = re.sub(r'session=([^;]+)', 'session=******', text)
    # 遮蔽access_token
    text = re.sub(r'access_token":"[^"]+', 'access_token":"******', text)
    # 遮蔽其他可能的敏感信息
    text = re.sub(r'X-Safe":"[^"]+', 'X-Safe":"******', text)
    return text

def extract_cookies(curl_output: str) -> Dict[str, str]:
    """从curl输出中提取cookies"""
    logging.info("开始提取cookies")
    cookies = {}
    
    # 查找所有Set-Cookie行
    for line in curl_output.split('\n'):
        line = line.strip()
        if line.startswith('Set-Cookie:'):
            # 记录日志时遮蔽敏感信息
            masked_line = mask_sensitive_info(line)
            logging.info(f"找到Set-Cookie行: {masked_line}")
            
            # 提取cookie部分
            cookie_part = line.replace('Set-Cookie:', '').strip()
            # 提取名称和值
            if '=' in cookie_part:
                name_value = cookie_part.split(';')[0].strip()
                name, value = name_value.split('=', 1)
                cookies[name] = value
                # 记录日志时遮蔽敏感信息
                logging.info(f"提取到cookie: {name}=******")
    
    # 如果未找到cookies，尝试使用正则表达式
    if not cookies:
        logging.warning("未通过行查找到cookies，尝试使用正则表达式")
        cookie_pattern = re.compile(r'Set-Cookie:\s*([^=]+)=([^;]+)')
        for match in cookie_pattern.finditer(curl_output):
            name, value = match.groups()
            cookies[name.strip()] = value.strip()
            logging.info(f"通过正则提取到cookie: {name}=******")
    
    # 直接提取session cookie
    if not cookies:
        logging.warning("正则表达式也未找到cookies，尝试直接提取session")
        session_match = re.search(r'Set-Cookie:.*?session=([^;]+)', curl_output, re.DOTALL)
        if session_match:
            cookies['session'] = session_match.group(1)
            logging.info("直接提取到session: ******")
    
    return cookies

def extract_status_code(curl_output: str) -> int:
    """从curl输出中提取状态码"""
    status_pattern = re.compile(r'HTTP/\d\.\d (\d+)')
    match = status_pattern.search(curl_output)
    if match:
        return int(match.group(1))
    return 0

def extract_response_body(curl_output: str) -> str:
    """从curl输出中提取响应体"""
    # 查找空行后的所有内容
    parts = curl_output.split('\r\n\r\n')
    # 如果没有找到带\r\n的分隔，尝试用普通换行符
    if len(parts) <= 1:
        parts = curl_output.split('\n\n')
    
    if len(parts) > 1:
        # 获取最后一个部分，这应该是响应体
        body = parts[-1].strip()
        # 查找JSON开始的位置（第一个{字符）
        json_start = body.find('{')
        if json_start >= 0:
            result = body[json_start:]
            # 确保结果是有效的JSON
            try:
                json.loads(result)  # 验证JSON是否有效
                logging.info(f"提取到的响应体: {result[:100]}...")
                return result
            except json.JSONDecodeError:
                logging.warning(f"提取的响应体不是有效的JSON: {result[:100]}...")
                # 尝试查找最后一个完整的JSON对象
                json_end = body.rfind('}') + 1
                if json_end > json_start:
                    result = body[json_start:json_end]
                    try:
                        json.loads(result)
                        logging.info(f"通过查找JSON结束位置提取到响应体: {result[:100]}...")
                        return result
                    except json.JSONDecodeError:
                        pass
        
        # 如果以上方法都失败，尝试直接在整个输出中查找完整的JSON对象
        json_start = curl_output.find('{"data"')
        if json_start >= 0:
            json_end = curl_output.find('"}', json_start)
            if json_end > 0:
                # 确保我们获取完整的JSON
                json_end = curl_output.find('}', json_end) + 1
                result = curl_output[json_start:json_end]
                try:
                    json.loads(result)
                    logging.info(f"通过直接查找数据字段提取到响应体: {result[:100]}...")
                    return result
                except json.JSONDecodeError:
                    pass
        
        logging.warning(f"响应体不包含JSON数据或格式不正确: {body[:100]}...")
        return body
    logging.warning("响应体为空或未找到HTTP头部与响应体的分隔")
    
    # 最后尝试：直接在整个响应中查找JSON
    json_start = curl_output.find('{"data"')
    if json_start >= 0:
        json_text = curl_output[json_start:]
        try:
            # 尝试解析并验证JSON
            parsed = json.loads(json_text)
            logging.info(f"通过直接查找提取到响应体: {json_text[:100]}...")
            return json_text
        except json.JSONDecodeError:
            # 如果不是完整JSON，尝试找到最后一个}
            json_end = json_text.rfind('}') + 1
            if json_end > 0:
                result = json_text[:json_end]
                try:
                    json.loads(result)
                    logging.info(f"找到部分JSON: {result[:100]}...")
                    return result
                except json.JSONDecodeError:
                    pass
    
    return ""

def extract_user_id(response_body: str) -> int:
    """从响应体中提取用户ID"""
    logging.info(f"开始提取用户ID，响应体长度: {len(response_body)}")
    
    try:
        # 预处理响应体：处理换行符和空格
        clean_body = response_body.replace('\n', '').replace('\r', '')
        
        # 尝试查找并提取JSON部分
        json_start = clean_body.find('{')
        json_end = clean_body.rfind('}') + 1
        
        logging.info(f"JSON范围: {json_start} 到 {json_end}")
        
        if json_start >= 0 and json_end > json_start:
            json_str = clean_body[json_start:json_end]
            logging.info(f"尝试解析JSON: {json_str[:100]}...")
            
            response_data = json.loads(json_str)
            logging.info(f"JSON解析成功，键列表: {list(response_data.keys())}")
            
            if 'success' in response_data:
                logging.info(f"success值: {response_data['success']}")
            
            if 'data' in response_data:
                data = response_data['data']
                logging.info(f"data键列表: {list(data.keys()) if isinstance(data, dict) else '非字典类型'}")
                
                if isinstance(data, dict) and 'id' in data:
                    user_id = data['id']
                    logging.info(f"成功提取到用户ID: {user_id}")
                    return user_id
                else:
                    logging.warning("data中不包含id字段")
            else:
                logging.warning("响应中不包含data字段")
    except json.JSONDecodeError as e:
        logging.warning(f"JSON解析错误: {str(e)}")
        logging.info(f"原始响应: {response_body}")
        # 尝试直接用正则表达式提取ID
        try:
            id_match = re.search(r'"id"\s*:\s*(\d+)', clean_body)
            if id_match:
                user_id = int(id_match.group(1))
                logging.info(f"通过正则表达式提取到用户ID: {user_id}")
                return user_id
            else:
                logging.warning("正则表达式未能匹配到ID")
        except Exception as regex_error:
            logging.warning(f"正则表达式提取错误: {str(regex_error)}")
    except Exception as e:
        logging.warning(f"提取用户ID时发生错误: {str(e)}")
    
    # 最后的尝试：不管前面出了什么错，直接用正则表达式从原始响应中提取
    try:
        id_match = re.search(r'"id"\s*:\s*(\d+)', response_body)
        if id_match:
            user_id = int(id_match.group(1))
            logging.info(f"最后尝试：通过正则表达式提取到用户ID: {user_id}")
            return user_id
    except Exception:
        pass
        
    logging.warning("未能提取到用户ID")
    return None

def get_cookies_with_curl(username: str, password: str, max_retries: int = 3) -> Dict:
    """使用curl命令获取cookies"""
    for attempt in range(max_retries):
        try:
            logging.info(f"正在请求账号: {username} (尝试 {attempt + 1}/{max_retries})")
            
            # 构建curl命令
            curl_command = [
                'curl',
                'https://openai.newbotai.cn/api/user/login',
                '-X', 'POST',
                '-i',
                '-H', 'Host: openai.newbotai.cn',
                '-H', 'Connection: keep-alive',
                '-H', 'sec-ch-ua-platform: macOS',
                '-H', 'Cache-Control: no-store',
                '-H', 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                '-H', 'VoApi-User: 193',
                '-H', 'sec-ch-ua-mobile: ?0',
                '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                '-H', 'Accept: application/json, text/plain, */*',
                '-H', 'Origin: https://openai.newbotai.cn',
                '-H', 'Sec-Fetch-Site: same-origin',
                '-H', 'Sec-Fetch-Mode: cors',
                '-H', 'Sec-Fetch-Dest: empty',
                '-H', 'Referer: https://openai.newbotai.cn/login?expired=true',
                '-H', 'Accept-Language: zh-CN,zh;q=0.9',
                '-H', 'Content-Type: application/json',
                '--data-raw', f'{{"username":"{username}","password":"{password}"}}'
            ]
            
            # 执行curl命令
            process = subprocess.Popen(
                curl_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # 记录日志时遮蔽敏感信息
            masked_stdout = mask_sensitive_info(stdout)
            logging.info(f"curl响应: {masked_stdout}")
            
            if stderr:
                logging.warning(f"curl错误输出: {stderr}")
            
            # 检查进程返回码
            if process.returncode != 0:
                logging.error(f"curl命令执行失败，返回码: {process.returncode}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 6))
                    continue
                return {
                    'username': username,
                    'error': f"curl命令执行失败，返回码: {process.returncode}",
                    'status': None,
                    'response': None,
                    'id': None
                }
            
            # 提取状态码
            status_code = extract_status_code(stdout)
            logging.info(f"账号 {username} 响应状态码: {status_code}")
            
            if status_code == 200:
                # 提取cookies
                cookies = extract_cookies(stdout)
                # 记录日志时遮蔽敏感信息
                masked_cookies = {k: "******" for k in cookies.keys()}
                logging.info(f"账号 {username} 获取到cookies: {masked_cookies}")
                
                # 提取响应体并遮蔽敏感信息
                response_body = extract_response_body(stdout)
                masked_body = mask_sensitive_info(response_body)
                
                # 提取用户ID
                user_id = extract_user_id(response_body)
                if user_id:
                    logging.info(f"账号 {username} 获取到用户ID: {user_id}")
                
                return {
                    'username': username,
                    'cookies': cookies,
                    'status': status_code,
                    'response': masked_body,  # 使用遮蔽后的响应体
                    'id': user_id
                }
            elif status_code == 429:
                wait_time = random.uniform(5, 8)
                logging.warning(f"账号 {username} 触发限流，等待 {wait_time:.1f} 秒后重试")
                time.sleep(wait_time)
            else:
                logging.error(f"账号 {username} 请求失败，状态码: {status_code}")
                response_body = extract_response_body(stdout)
                masked_body = mask_sensitive_info(response_body)
                return {
                    'username': username,
                    'error': f"请求失败，状态码: {status_code}",
                    'status': status_code,
                    'response': masked_body,  # 使用遮蔽后的响应体
                    'id': None
                }
                
        except Exception as e:
            logging.error(f"账号 {username} 发生错误: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(3, 6))
            else:
                return {
                    'username': username,
                    'error': f"发生错误: {str(e)}",
                    'status': None,
                    'response': None,
                    'id': None
                }
    
    return {
        'username': username,
        'error': f"达到最大重试次数 ({max_retries})",
        'status': None,
        'response': None,
        'id': None
    }

def main():
    """主函数"""
    try:
        accounts = load_accounts()
        logging.info(f"成功加载 {len(accounts)} 个账号")
        results = []
        
        for account in accounts:
            result = get_cookies_with_curl(account['username'], account['password'])
            results.append(result)
            
            # 增加账号之间的等待时间
            delay = random.uniform(4, 7)
            logging.info(f"等待 {delay:.1f} 秒后处理下一个账号")
            time.sleep(delay)
        
        # 输出结果预览用于调试（遮蔽敏感信息）
        preview_results = []
        for r in results[:2]:
            preview = r.copy()
            if 'cookies' in preview:
                preview['cookies'] = {k: "******" for k in preview['cookies'].keys()}
            if 'response' in preview:
                preview['response'] = mask_sensitive_info(preview['response'])
            preview_results.append(preview)
        
        logging.info(f"处理完成，结果预览: {json.dumps(preview_results, ensure_ascii=False, indent=2)}")
        
        # 保存结果（保存原始数据，但日志中显示遮蔽后的数据）
        try:
            with open('cookies_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logging.info("结果已保存到 cookies_results.json")
        except Exception as e:
            logging.error(f"保存cookies_results.json失败: {str(e)}")
        
        # 单独保存cookies到另一个文件
        try:
            cookies_dict = {}
            for res in results:
                if res.get('cookies'):
                    cookies_dict[res['username']] = {
                        'cookies': res['cookies'],
                        'id': res.get('id')
                    }
            
            with open('cookies_only.json', 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
            logging.info("cookies和用户ID已单独保存到 cookies_only.json")
        except Exception as e:
            logging.error(f"保存cookies_only.json失败: {str(e)}")
        
        # 统计成功和失败数量
        success_count = sum(1 for r in results if r.get('status') == 200)
        fail_count = len(results) - success_count
        logging.info(f"成功: {success_count} 个，失败: {fail_count} 个")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")

if __name__ == '__main__':
    main() 
