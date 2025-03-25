#!/usr/bin/env python3
import os
import json

def check_files():
    """检查cookies相关文件"""
    print("当前目录:", os.getcwd())
    # print("\n目录内容:")
    # for item in os.listdir('.'):
    #     if os.path.isfile(item):
    #         size = os.path.getsize(item)
    #         print(f"- {item} ({size} 字节)")
    #     else:
    #         print(f"- {item} (目录)")
    
    # 检查cookies_results.json
    if os.path.exists('cookies_results.json'):
        print("\ncookies_results.json存在")
        try:
            with open('cookies_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"包含 {len(data)} 条记录")
                
                if data and isinstance(data, list):
                    sample = data[0]
                    print(f"\n第一条记录:")
                    print(f"- 用户名: {sample.get('username')}")
                    print(f"- 状态码: {sample.get('status')}")
                    print(f"- cookies: {sample.get('cookies')}")
        except Exception as e:
            print(f"读取cookies_results.json失败: {str(e)}")
    else:
        print("\ncookies_results.json不存在")
    
    # 检查cookies_only.json
    if os.path.exists('cookies_only.json'):
        print("\ncookies_only.json存在")
        try:
            with open('cookies_only.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"包含 {len(data)} 条记录")
                
                if data and isinstance(data, dict):
                    users = list(data.keys())
                    if users:
                        sample_user = users[0]
                        print(f"\n第一条记录:")
                        print(f"- 用户名: {sample_user}")
                        print(f"- cookies: {data.get(sample_user)}")
        except Exception as e:
            print(f"读取cookies_only.json失败: {str(e)}")
    else:
        print("\ncookies_only.json不存在")

if __name__ == '__main__':
    check_files() 
