import random
import string
import time
import yaml
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, expect
from pathlib import Path
from typing import Dict

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

def register_account(page, username: str, password: str, max_retries: int = 3) -> bool:
    """注册单个账号，带重试机制"""
    for attempt in range(max_retries):
        try:
            # 导航到注册页面
            page.goto('https://openai.newbotai.cn/register?aff=DsaD')
            # 等待页面加载完成
            page.wait_for_load_state('networkidle')
            page.wait_for_load_state('domcontentloaded')
            
            # 等待用户名输入框出现
            page.wait_for_selector('#username', state='visible', timeout=60000)
            
            # 检查并关闭公告
            try:
                close_button = page.get_by_role("button", name="关闭公告")
                if close_button.is_visible(timeout=5000):
                    close_button.click()
                    time.sleep(1)
            except PlaywrightTimeoutError:
                # 如果没有公告弹窗，继续执行
                pass
            
            # 填写表单
            username_input = page.locator('#username')
            username_input.fill(username)
            time.sleep(random.uniform(0.5, 1))
            
            password_input = page.locator('#password')
            password_input.fill(password)
            time.sleep(random.uniform(0.5, 1))
            
            password2_input = page.locator('#password2')
            password2_input.fill(password)
            time.sleep(random.uniform(0.5, 1))
            
            # 等待注册按钮可点击
            register_button = page.get_by_role("button", name="注册")
            register_button.wait_for(state='visible', timeout=60000)
            
            # 创建响应监听器并点击注册
            with page.expect_response("**/api/user/register*", timeout=60000) as response_info:
                register_button.click()
                
                try:
                    response = response_info.value
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
                    print(f"解析响应失败：{str(e)}")
                    if attempt < max_retries - 1:
                        print(f"等待 5 秒后重试...")
                        time.sleep(5)
                    continue
                
        except Exception as e:
            print(f"注册过程出错（尝试 {attempt + 1}/{max_retries}）：{str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 5 秒后重试...")
                time.sleep(5)
            continue
            
        time.sleep(2)  # 在重试之前等待
    
    return False

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量注册账号脚本')
    parser.add_argument('--show-browser', action='store_true', help='显示浏览器窗口（默认为无头模式）')
    parser.add_argument('--num-accounts', type=int, default=1000, help='要注册的账号数量（默认100个）')
    args = parser.parse_args()

    try:
        # 生成随机账号
        print("正在生成随机账号...")
        accounts = generate_accounts(args.num_accounts)
        password = "autoregister@123"
        
        # 加载现有配置
        print("加载配置文件...")
        config = load_config()
        
        # 启动浏览器
        print(f"启动浏览器... {'显示模式' if args.show_browser else '无头模式'}")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=not args.show_browser,  # 默认使用无头模式
                args=['--start-maximized']
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            # 设置全局超时时间
            context.set_default_timeout(60000)  # 60秒
            
            page = context.new_page()
            
            # 注册每个账号
            success_count = 0
            fail_count = 0
            
            for i, username in enumerate(accounts, 1):
                print(f"\n开始注册第 {i}/{len(accounts)} 个账号: {username}")
                success = register_account(page, username, password)
                
                if success:
                    success_count += 1
                    # 将成功注册的账号添加到配置，保持格式一致
                    config['accounts'].append({
                        'username': username,
                        'password': password
                    })
                    # 保存配置
                    save_config(config)
                else:
                    fail_count += 1
                
                # 随机延迟，模拟人工操作
                if i < len(accounts):  # 如果不是最后一个账号
                    delay = random.uniform(2, 4)
                    print(f"等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
            
            # 关闭浏览器
            context.close()
            browser.close()
            
            # 打印统计信息
            print(f"\n注册完成！")
            print(f"成功：{success_count} 个")
            print(f"失败：{fail_count} 个")
            print(f"成功率：{(success_count/len(accounts)*100):.1f}%")
            
    except Exception as e:
        print(f"程序执行出错：{str(e)}")
        raise

if __name__ == "__main__":
    main() 
