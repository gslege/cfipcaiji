import requests
from bs4 import BeautifulSoup
import re
import os
import subprocess
import platform

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://api.uouin.com/cloudflare.html', 
    'https://raw.githubusercontent.com/xingpingcn/enhanced-FaaS-in-China/refs/heads/main/Cf.json', 
    'https://cf-ip.cdtools.click/beijing', 
    'https://cf-ip.cdtools.click/shanghai', 
    'https://cf-ip.cdtools.click/chengdu', 
    'https://cf-ip.cdtools.click/shenzhen'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

def ping_ip(ip_address):
    """
    测试IP地址的延迟
    返回延迟时间（毫秒），如果ping失败返回None
    """
    try:
        # 根据操作系统选择ping命令
        if platform.system().lower() == "windows":
            # Windows系统使用 -n 1 参数
            cmd = ["ping", "-n", "1", ip_address]
        else:
            # Linux/Mac系统使用 -c 1 参数
            cmd = ["ping", "-c", "1", ip_address]
        
        # 执行ping命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # 从输出中提取延迟时间
            output = result.stdout
            if platform.system().lower() == "windows":
                # Windows ping输出格式: 时间<1ms 或 时间=XXms
                time_match = re.search(r'时间[<=](\d+)ms', output)
            else:
                # Linux/Mac ping输出格式: time=XX.X ms
                time_match = re.search(r'time=(\d+(?:\.\d+)?)', output)
            
            if time_match:
                latency = float(time_match.group(1))
                return int(latency)  # 返回整数，不显示小数点
        return None
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
        return None

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 使用集合存储IP地址实现自动去重
unique_ips = set()

for url in urls:
    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url, timeout=5)
        
        # 确保请求成功
        if response.status_code == 200:
            # 获取网页的文本内容
            html_content = response.text
            
            # 使用正则表达式查找IP地址
            ip_matches = re.findall(ip_pattern, html_content, re.IGNORECASE)
            
            # 将找到的IP添加到集合中（自动去重）
            unique_ips.update(ip_matches)
    except requests.exceptions.RequestException as e:
        print(f'请求 {url} 失败: {e}')
        continue

# 测试每个IP地址的延迟并收集结果
if unique_ips:
    print(f'开始测试 {len(unique_ips)} 个IP地址的延迟...')
    ip_latency_list = []
    
    for ip in unique_ips:
        print(f'正在测试 {ip}...', end=' ')
        latency = ping_ip(ip)
        if latency is not None:
            ip_latency_list.append((ip, latency))
            print(f'延迟: {latency}ms')
        else:
            print('连接失败')
    
    # 按延迟时间排序（延迟小的在前）
    ip_latency_list.sort(key=lambda x: x[1])
    
    # 写入文件，格式为：IP地址，延迟ms
    with open('ip.txt', 'w', encoding='utf-8') as file:
        for ip, latency in ip_latency_list:
            file.write(f'{ip},CF优选IP,{latency}ms\n')
    
    print(f'\n已保存 {len(ip_latency_list)} 个有效IP地址到ip.txt文件，按延迟排序。')
