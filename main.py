#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import sys
import time
from pathlib import Path

def ensure_dependencies():
    """确保依赖项已安装"""
    try:
        import yaml
        import playwright
        import selenium
    except ImportError as e:
        print(f"缺少必要的依赖项: {e}")
        print("正在尝试安装依赖...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("依赖安装完成，重新启动脚本...")
        except Exception as install_e:
            print(f"安装依赖失败: {install_e}")
            print("请手动执行: pip install -r requirements.txt")
            sys.exit(1)

def show_banner():
    """显示脚本banner"""
    banner = """
    ███╗   ██╗███████╗██╗    ██╗██████╗  ██████╗ ████████╗ █████╗ ██╗
    ████╗  ██║██╔════╝██║    ██║██╔══██╗██╔═══██╗╚══██╔══╝██╔══██╗██║
    ██╔██╗ ██║█████╗  ██║ █╗ ██║██████╔╝██║   ██║   ██║   ███████║██║
    ██║╚██╗██║██╔══╝  ██║███╗██║██╔══██╗██║   ██║   ██║   ██╔══██║██║
    ██║ ╚████║███████╗╚███╔███╔╝██████╔╝╚██████╔╝   ██║   ██║  ██║██║
    ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝
                                                                 
        NewBotAI 自动注册与签到工具 v1.0.0
    """
    print(banner)

def register_command(args):
    """执行注册命令"""
    from register import main as register_main
    sys.argv = ['register.py']
    if args.show_browser:
        sys.argv.append('--show-browser')
    if args.num_accounts:
        sys.argv.extend(['--num-accounts', str(args.num_accounts)])
    register_main()

def sign_command(args):
    """执行签到命令"""
    from sign import NewBotAISignIn
    # 创建签到实例并运行
    sign_bot = NewBotAISignIn()
    sign_bot.run()

def main():
    """主函数"""
    # 显示Banner
    show_banner()
    
    # 确保工作目录正确
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 确保依赖项已安装
    ensure_dependencies()
    
    # 创建命令行解析器
    parser = argparse.ArgumentParser(description='NewBotAI 自动注册与签到工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 注册命令
    register_parser = subparsers.add_parser('register', help='批量注册账号')
    register_parser.add_argument('--show-browser', action='store_true', help='显示浏览器窗口（默认为无头模式）')
    register_parser.add_argument('--num-accounts', type=int, help='要注册的账号数量（默认1000个）')
    register_parser.set_defaults(func=register_command)
    
    # 签到命令
    sign_parser = subparsers.add_parser('sign', help='执行自动签到')
    sign_parser.set_defaults(func=sign_command)
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助信息
    if not hasattr(args, 'func'):
        parser.print_help()
        return
    
    # 执行对应的命令
    try:
        args.func(args)
    except Exception as e:
        print(f"执行命令时出错: {e}")
        raise

if __name__ == "__main__":
    main() 
