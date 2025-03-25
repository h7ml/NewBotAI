#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import yaml
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import atexit

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

# 浏览器配置
BROWSER_CONFIG = {
    'language': 'zh-CN',  # 浏览器语言
    'timeout': 30,  # 超时时间(秒)
    'input_delay': {  # 输入延迟(秒)
        'min': 0.1,
        'max': 0.3
    },
    'click_delay': {  # 点击延迟(秒)
        'min': 0.2,
        'max': 0.5
    }
}

# 网站配置
SITE_CONFIG = {
    'login_url': 'https://openai.newbotai.cn/login',
    'dash_url': 'https://openai.newbotai.cn/dash',
    'profile_url': 'https://openai.newbotai.cn/profile'
}

class NewBotAISignIn:
    def __init__(self):
        # 初始化日志记录器
        self.logger = Logger()
        self.logger.info("初始化 NewBotAISignIn 实例")
        
        # 加载配置文件
        self.config = self._load_config()
        self.logger.info("配置文件加载完成")
        
        # 确保日志目录存在
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 初始化浏览器配置
        self.options = self._init_browser_options()
        
        # 浏览器实例
        self.driver = None
        self.wait = None
        
        # 注册退出处理函数
        atexit.register(self._cleanup)
        self.logger.info("初始化完成")

    def _cleanup(self):
        """清理浏览器实例"""
        try:
            if self.driver:
                self.logger.info("正在关闭浏览器实例")
                self.driver.quit()
                self.driver = None
                self.logger.info("浏览器实例已关闭")
        except Exception as e:
            self.logger.error(f"关闭浏览器实例时出错: {e}")

    def _load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
            self.logger.info(f"正在加载配置文件: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.info("配置文件加载成功")
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            raise

    def _init_browser_options(self):
        """初始化浏览器配置"""
        try:
            self.logger.info("开始初始化浏览器配置")
            options = Options()
            
            # 设置浏览器语言
            options.add_argument(f'--lang={BROWSER_CONFIG["language"]}')
            
            # 设置浏览器启动参数
            options.add_argument('--disable-gpu')  # 禁用GPU加速
            options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
            options.add_argument('--no-sandbox')  # 禁用沙箱
            options.add_argument('--disable-infobars')  # 禁用信息栏
            options.add_argument('--disable-notifications')  # 禁用通知
            options.add_argument('--disable-extensions')  # 禁用扩展
            options.add_argument('--disable-popup-blocking')  # 禁用弹窗拦截
            options.add_argument('--window-size=1366,768')  # 设置窗口大小
            
            # 设置 User-Agent
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
            
            # 设置其他选项
            options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化标记
            options.add_argument('--disable-web-security')  # 禁用网页安全性检查
            options.add_argument('--allow-running-insecure-content')  # 允许运行不安全内容
            
            self.logger.info("浏览器配置初始化完成")
            return options
        except Exception as e:
            self.logger.error(f"初始化浏览器配置失败: {e}")
            raise

    def _ensure_browser(self):
        """确保浏览器实例存在并正常运行"""
        try:
            if not self.driver:
                self.logger.info("创建新的浏览器实例")
                # 直接使用 Chrome WebDriver
                self.driver = webdriver.Chrome(options=self.options)
                self.wait = WebDriverWait(self.driver, BROWSER_CONFIG['timeout'])
                self.logger.info("浏览器实例创建成功")
            return self.driver
        except Exception as e:
            self.logger.error(f"创建浏览器实例失败: {e}")
            raise

    def _wait_for_element(self, by, value, timeout=None):
        """等待元素出现并返回"""
        try:
            timeout = timeout or BROWSER_CONFIG['timeout']
            self.logger.info(f"等待元素出现: {by}={value}, 超时时间: {timeout}秒")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            self.logger.info(f"元素已找到: {by}={value}")
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素超时: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"等待元素时出错: {by}={value}, 错误: {e}")
            return None

    def _wait_for_url_change(self, expected_url_start, timeout=None):
        """等待URL变化到预期的开始部分"""
        try:
            timeout = timeout or BROWSER_CONFIG['timeout']
            self.logger.info(f"等待URL变化到: {expected_url_start}, 超时时间: {timeout}秒")
            return WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.current_url.startswith(expected_url_start)
            )
        except TimeoutException:
            self.logger.warning(f"等待URL变化超时，当前URL: {self.driver.current_url}")
            return False
        except Exception as e:
            self.logger.error(f"等待URL变化时出错: {e}")
            return False

    def _handle_notice_modal(self):
        """处理公告模态框"""
        try:
            self.logger.info("开始处理公告模态框")
            
            # 等待模态框出现
            try:
                modal = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"][aria-labelledby="semi-modal-title"]'))
                )
                
                # 检查是否是公告模态框
                title = modal.find_element(By.CSS_SELECTOR, '.semi-modal-title')
                if title and title.text == '公告':
                    self.logger.info("确认为公告模态框")
                    
                    # 查找并点击关闭按钮，优先使用"今日关闭"
                    close_buttons = [
                        '今日关闭',
                        '关闭公告',
                        '关闭'
                    ]
                    
                    for button_text in close_buttons:
                        try:
                            self.logger.info(f"尝试查找按钮: {button_text}")
                            close_button = modal.find_element(By.XPATH, f'.//button[contains(., "{button_text}")]')
                            if close_button:
                                self._random_delay('click')
                                close_button.click()
                                self.logger.info("已点击关闭按钮")
                                
                                # 等待模态框消失
                                WebDriverWait(self.driver, 5).until(
                                    EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
                                )
                                self.logger.info("模态框已消失")
                                return True
                        except NoSuchElementException:
                            continue
                    
                    self.logger.warning("未找到任何关闭按钮")
                else:
                    self.logger.info("模态框不是公告模态框")
            except TimeoutException:
                self.logger.info("未发现模态框")
            
            return False
        except Exception as e:
            self.logger.error(f"处理公告模态框时出错: {e}")
            return False

    def _random_delay(self, action_type='input'):
        """模拟人工操作的随机延迟"""
        if action_type == 'input':
            delay_range = BROWSER_CONFIG['input_delay']
        else:  # click
            delay_range = BROWSER_CONFIG['click_delay']
        delay = random.uniform(delay_range['min'], delay_range['max'])
        self.logger.debug(f"随机延迟 {action_type}: {delay:.2f}秒")
        time.sleep(delay)

    def _simulate_typing(self, element, text):
        """模拟人工输入"""
        self.logger.info(f"模拟输入文本，长度: {len(text)}")
        for char in text:
            element.send_keys(char)
            self._random_delay('input')
        self.logger.info("文本输入完成")

    def _log_result(self, account, status, balance_info=None):
        """记录签到结果到日志文件"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = os.path.join(self.log_dir, f'{today}.md')
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.logger.info(f"记录签到结果 - 账号: {account}, 状态: {status}")
            
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
            
            self.logger.info("签到结果已记录到日志文件")
        except Exception as e:
            self.logger.error(f"记录签到结果时出错: {e}")

    def _get_balance_info(self):
        """获取账户余额信息"""
        try:
            self.logger.info("开始获取账户余额信息")
            descriptions = self._wait_for_element(By.CLASS_NAME, 'semi-descriptions')
            if not descriptions:
                self.logger.warning("未找到余额信息元素")
                return None
            
            values = descriptions.find_elements(By.CLASS_NAME, 'semi-descriptions-value')
            if len(values) >= 3:
                balance_info = {
                    'balance': values[0].text,
                    'consumed': values[1].text,
                    'requests': values[2].text
                }
                self.logger.info(f"成功获取余额信息: {balance_info}")
                return balance_info
        except Exception as e:
            self.logger.error(f"获取余额信息失败: {e}")
        return None

    def _take_screenshot(self, name):
        """保存截图用于调试"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{name}.png"
            screenshot_path = os.path.join(self.log_dir, 'screenshots')
            os.makedirs(screenshot_path, exist_ok=True)
            self.driver.save_screenshot(os.path.join(screenshot_path, filename))
            self.logger.info(f"截图已保存: {filename}")
        except Exception as e:
            self.logger.error(f"保存截图失败: {e}")

    def sign_in(self, username, password):
        """执行签到流程"""
        try:
            self.logger.info(f"开始执行签到流程 - 账号: {username}")
            
            # 确保浏览器实例存在
            self._ensure_browser()
            
            # 访问登录页面
            self.logger.info(f"访问登录页面: {SITE_CONFIG['login_url']}")
            self.driver.get(SITE_CONFIG['login_url'])
            # 等待页面加载完成
            WebDriverWait(self.driver, BROWSER_CONFIG['timeout']).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            # 刷新页面
            self.driver.refresh()
            
            # 等待一段时间让页面完全渲染
            time.sleep(2)
            
            # 处理公告模态框
            self._handle_notice_modal()
            
            # 等待并填写登录表单
            self.logger.info("开始填写登录表单")
            
            # 保存登录页面截图
            self._take_screenshot('login_page')
            
            # 等待页面上的任何输入框出现
            self.logger.info("等待登录表单加载")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "input"))
            )
            
            # 获取所有输入框
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            username_input = None
            password_input = None
            
            # 遍历所有输入框，根据属性识别用户名和密码字段
            for input_field in inputs:
                input_type = input_field.get_attribute("type")
                placeholder = input_field.get_attribute("placeholder")
                
                if input_type == "text" or (placeholder and "用户名" in placeholder):
                    username_input = input_field
                    self.logger.info("找到用户名输入框")
                elif input_type == "password":
                    password_input = input_field
                    self.logger.info("找到密码输入框")
                
                if username_input and password_input:
                    break
            
            if not username_input or not password_input:
                raise Exception("找不到登录表单")
            
            # 清空输入框
            username_input.clear()
            password_input.clear()
            
            # 模拟输入账号密码
            self._simulate_typing(username_input, username)
            self._simulate_typing(password_input, password)
            
            # 点击登录按钮
            self.logger.info("尝试登录")
            
            # 查找所有可能的登录按钮
            button_selectors = [
                (By.XPATH, '//button[contains(text(), "登录")]'),
                (By.CSS_SELECTOR, 'button.semi-button-primary'),
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.CSS_SELECTOR, '.semi-button')
            ]
            
            login_button = None
            for by, selector in button_selectors:
                try:
                    elements = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_all_elements_located((by, selector))
                    )
                    # 遍历找到的元素，检查文本内容
                    for element in elements:
                        if '登录' in element.text:
                            login_button = element
                            self.logger.info(f"找到登录按钮: {element.text}")
                            break
                    if login_button:
                        break
                except:
                    continue
            
            if not login_button:
                raise Exception("找不到登录按钮")
            
            self._random_delay('click')
            login_button.click()
            
            # 保存登录后截图
            self._take_screenshot('after_login')
            
            # 等待跳转到仪表盘
            if not self._wait_for_url_change(SITE_CONFIG['dash_url']):
                raise Exception("登录失败或跳转超时")
            
            # 访问个人资料页面
            self.logger.info(f"访问个人资料页面: {SITE_CONFIG['profile_url']}")
            self.driver.get(SITE_CONFIG['profile_url'])
            
            # 等待页面加载完成
            WebDriverWait(self.driver, BROWSER_CONFIG['timeout']).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            
            # 保存个人资料页面截图
            self._take_screenshot('profile_page')
            
            # 检查签到按钮
            self.logger.info("检查签到状态")
            sign_button = self._wait_for_element(
                By.XPATH,
                '//span[contains(text(), "今日签到打卡") or contains(text(), "今日已签到")]/..'
            )
            
            if not sign_button:
                raise Exception("找不到签到按钮")
            
            button_text = sign_button.find_element(By.CLASS_NAME, 'semi-button-content').text
            self.logger.info(f"签到按钮状态: {button_text}")
            
            if button_text == "今日签到打卡":
                self.logger.info("执行签到操作")
                self._random_delay('click')
                sign_button.click()
                # 等待签到操作完成
                time.sleep(2)  # 等待可能的动画效果
                status = "签到成功"
            elif button_text == "今日已签到":
                self.logger.info("今日已完成签到")
                status = "今日已签到"
            else:
                status = "未知状态"
            
            # 保存签到后截图
            self._take_screenshot('after_sign')
            
            # 获取余额信息
            balance_info = self._get_balance_info()
            
            # 记录日志
            self._log_result(username, status, balance_info)
            
            self.logger.info(f"签到流程完成 - 账号: {username}, 状态: {status}")
            return True
            
        except Exception as e:
            error_msg = f"签到失败: {str(e)}"
            self.logger.error(error_msg)
            # 发生错误时保存截图
            self._take_screenshot('error')
            self._log_result(username, error_msg)
            return False

    def run(self):
        """运行签到程序"""
        try:
            self.logger.info("开始运行签到程序")
            # 创建浏览器实例
            self._ensure_browser()
            
            total_accounts = len(self.config['accounts'])
            self.logger.info(f"共有 {total_accounts} 个账号需要处理")
            
            for index, account in enumerate(self.config['accounts'], 1):
                self.logger.info(f"正在处理第 {index}/{total_accounts} 个账号: {account['username']}")
                success = self.sign_in(account['username'], account['password'])
                
                if success:
                    self.logger.info(f"账号 {account['username']} 处理完成")
                else:
                    self.logger.warning(f"账号 {account['username']} 处理失败")
                
                if account != self.config['accounts'][-1]:
                    delay = random.uniform(3, 5)
                    self.logger.info(f"等待 {delay:.1f} 秒后处理下一个账号")
                    time.sleep(delay)
            
            self.logger.info("所有账号处理完成")
        except Exception as e:
            self.logger.error(f"运行签到程序时出错: {e}")
        finally:
            # 清理浏览器实例
            self._cleanup()

if __name__ == "__main__":
    bot = NewBotAISignIn()
    try:
        bot.run()
    except Exception as e:
        bot.logger.error(f"程序执行出错: {e}")
    finally:
        bot._cleanup() 
