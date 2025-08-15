# cai.py
import argparse
import subprocess
import sys
import json
import os
from pathlib import Path

# Try to import SSL-related modules with fallback
try:
    import ssl
    import requests
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False
    print("警告: SSL模块不可用，将使用本地命令映射")

def load_api_key():
    """从.env文件加载API key"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('DEEPSEEK_API_KEY='):
                    return line.strip().split('=', 1)[1]
    return None

def save_api_key(api_key: str):
    """保存API key到.env文件"""
    env_file = Path('.env')
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(f'DEEPSEEK_API_KEY={api_key}\n')
    print(f"API key已保存到 {env_file}")

def call_deepseek_api(prompt: str, api_key: str) -> str:
    """调用DeepSeek API"""
    if not SSL_AVAILABLE:
        print("SSL模块不可用，无法进行API调用")
        return None
        
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一个PowerShell命令生成助手。用户会用中文描述想要执行的系统操作，你需要返回对应的PowerShell命令。只返回命令本身，不要解释。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 100
    }
    
    try:
        # 尝试修复SSL问题
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except ImportError as e:
        print(f"SSL模块不可用，无法进行API调用: {e}")
        return None
    except requests.exceptions.SSLError as e:
        print(f"SSL连接错误，无法进行API调用: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"API调用失败: {e}")
        return None
    except Exception as e:
        print(f"API调用出现未知错误: {e}")
        return None

def generate_powershell_command(natural_language: str) -> str:
    """生成PowerShell命令"""
    # 首先尝试从API key获取命令
    api_key = load_api_key()
    if api_key and SSL_AVAILABLE:
        print("正在使用DeepSeek API生成命令...")
        command = call_deepseek_api(natural_language, api_key)
        if command:
            return command
    
    # 如果API调用失败或没有API key，使用本地映射
    print("使用本地命令映射...")
    
    # 检查是否是环境变量相关命令
    if "添加到环境变量" in natural_language or "添加到path" in natural_language.lower():
        # 提取路径信息
        if "D:\\projects\\代码\\cai\\dist" in natural_language:
            path_to_add = "D:\\projects\\代码\\cai\\dist"
        elif "cai.exe" in natural_language:
            path_to_add = "D:\\projects\\代码\\cai\\dist"
        else:
            # 尝试从命令中提取路径
            import re
            path_match = re.search(r'[A-Za-z]:\\[^"]*', natural_language)
            if path_match:
                path_to_add = path_match.group()
            else:
                path_to_add = "D:\\projects\\代码\\cai\\dist"
        
        # 返回永久设置环境变量并立即生效的命令
        return f"""
$newPath = '{path_to_add}'
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike "*$newPath*") {{
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';' + $newPath, 'User')
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User')
    Write-Host "✅ 已成功将 $newPath 添加到永久环境变量中"
    Write-Host "当前会话已立即生效，新开终端也会生效"
}} else {{
    Write-Host "⚠️  $newPath 已存在于环境变量中"
}}
"""
    
    command_map = {
        # 文件和目录操作
        "查看当前目录的文件": "dir",
        "列出子目录": "dir /ad",
        "列出当前目录": "dir",
        "显示目录内容": "dir",
        "查看列表": "dir",
        "显示列表": "dir",
        "列出文件": "dir",
        "查看文件": "dir",
        
        # 系统信息
        "查看系统信息": "systeminfo",
        "显示系统信息": "systeminfo",
        "查看网络配置": "ipconfig",
        "显示网络配置": "ipconfig",
        "查看IP地址": "ipconfig",
        
        # 环境变量操作
        "查看环境变量": "Get-ChildItem Env:",
        "显示环境变量": "Get-ChildItem Env:",
        "查看PATH环境变量": "$env:Path -split ';'",
        "显示PATH环境变量": "$env:Path -split ';'",
        
        # 进程管理
        "查看运行进程": "Get-Process",
        "显示运行进程": "Get-Process",
        "查看进程列表": "Get-Process",
        
        # 服务管理
        "查看服务": "Get-Service",
        "显示服务": "Get-Service",
        "查看服务列表": "Get-Service",
        
        # 网络相关
        "测试网络连接": "Test-NetConnection google.com",
        "ping测试": "Test-NetConnection google.com",
        "查看端口": "netstat -an",
        "显示端口": "netstat -an"
    }
    return command_map.get(natural_language, None)

def main():
    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description='自然语言转PowerShell工具')
    parser.add_argument("command", nargs='?', help="自然语言指令，需用引号包裹", type=str)
    parser.add_argument("--dry-run", help="只显示生成的命令，不执行", action="store_true")
    parser.add_argument("--set", help="设置DeepSeek API key", type=str, metavar="api_key")
    args = parser.parse_args()

    # 处理设置API key
    if args.set:
        save_api_key(args.set)
        return

    # 检查是否提供了命令
    if not args.command:
        parser.print_help()
        return

    # 生成命令
    powershell_command = generate_powershell_command(args.command)
    print(f"输入指令: {args.command}")
    
    # 检查是否生成了有效命令
    if powershell_command is None:
        print("❌ 无法理解该指令，请尝试其他描述或设置API key以获得更好的支持")
        print("提示: 使用 cai.exe --set \"your_api_key\" 设置DeepSeek API key")
        return
    
    print(f"生成的PowerShell命令: {powershell_command}")
    print("-" * 50)

    # 默认执行模式，除非指定--dry-run
    if not args.dry_run:
        print("正在执行命令...")
        print("=" * 50)
        try:
            result = subprocess.run(["powershell", "-Command", powershell_command], 
                                  encoding="gbk", capture_output=True, text=True)
            print("执行结果:")
            print(result.stdout)
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
        except Exception as e:
            print(f"执行出错: {e}")
    else:
        print("提示: 使用 --dry-run 参数只显示命令而不执行")
        print("示例: cai.exe \"查看当前目录的文件\" --dry-run")

if __name__ == "__main__":
    main()
