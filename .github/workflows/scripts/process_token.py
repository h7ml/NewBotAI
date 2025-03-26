#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用Markdown文件处理脚本
用于处理Markdown文件并生成GitHub评论的JSON内容
支持token.md和sign.md等不同类型的文件
"""

import json
import sys
import os


def process_markdown_file(file_path, title=None):
    """
    读取Markdown文件，处理内容，并生成GitHub评论的JSON格式
    
    参数:
      file_path: Markdown文件路径
      title: 评论标题，如果为None则根据文件名自动生成
      
    返回:
      生成的JSON字符串
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件 {file_path} 不存在", file=sys.stderr)
            return None
            
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 如果没有提供标题，根据文件名生成默认标题
        if title is None:
            file_name = os.path.basename(file_path)
            if file_name == 'token.md':
                title = "Token 更新报告"
            elif file_name == 'sign.md':
                title = "签到日志报告"
            else:
                title = f"{os.path.splitext(file_name)[0].capitalize()} 报告"
        
        # 创建评论内容
        comment = f"# {title}\n\n{content}"
        
        # 构建请求体
        request_body = {"body": comment}
        
        # 返回JSON字符串
        return json.dumps(request_body, ensure_ascii=False)
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}", file=sys.stderr)
        return None


def main():
    """主函数"""
    # 获取命令行参数
    if len(sys.argv) < 2:
        print("用法: process_token.py <文件路径> [标题]", file=sys.stderr)
        return 1
    
    file_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 处理文件
    result = process_markdown_file(file_path, title)
    
    # 输出结果
    if result:
        print(result)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
