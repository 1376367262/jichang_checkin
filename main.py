import requests
import json
import re
import os

# --- 新版 Server酱 推送函数 ---
def sc_send(sendkey, title, desp='', options=None):
    if not sendkey:
        return
    if options is None:
        options = {}
    
    # 判断 sendkey 是否以 'sctp' 开头，并提取数字构造 URL
    if sendkey.startswith('sctp'):
        match = re.match(r'sctp(\d+)t', sendkey)
        if match:
            num = match.group(1)
            url = f'https://{num}.push.ft07.com/send/{sendkey}.send'
        else:
            print('Invalid sendkey format for sctp')
            return
    else:
        url = f'https://sctapi.ftqq.com/{sendkey}.send'
        
    params = {
        'title': title,
        'desp': desp,
        **options
    }
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    try:
        response = requests.post(url, json=params, headers=headers)
        return response.json()
    except Exception as e:
        print(f"推送请求失败: {e}")

# --- 配置读取 ---
url = os.environ.get('URL')
config = os.environ.get('CONFIG')
SCKEY = os.environ.get('SCKEY')

login_url = f'{url}/auth/login'
check_url = f'{url}/user/checkin'

def sign(order, user, pwd):
    session = requests.session()
    header = {
        'origin': url,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    data = {
        'email': user,
        'passwd': pwd
    }
    
    try:
        print(f'=== 账号 {order+1} 进行登录... ===')
        print(f'账号：{user}')
        
        # 登录
        res = session.post(url=login_url, headers=header, data=data).text
        response = json.loads(res)
        print(f"登录结果: {response.get('msg')}")

        # 签到
        res2 = session.post(url=check_url, headers=header).text
        result = json.loads(res2)
        content = result.get('msg', '无返回信息')
        print(f"签到结果: {content}")

        # 使用新版函数推送
        if SCKEY:
            sc_send(SCKEY, '机场签到成功', content)
            print('推送成功')

    except Exception as ex:
        content = f'签到失败，错误原因: {ex}'
        print(content)
        if SCKEY:
            sc_send(SCKEY, '机场签到异常', content)
            print('异常推送成功')
            
    print(f'=== 账号 {order+1} 签到结束 ===\n')

if __name__ == '__main__':
    if not config:
        print('错误：未设置 CONFIG 环境变量')
        exit()
        
    configs = config.splitlines()
    if len(configs) % 2 != 0 or len(configs) == 0:
        print('配置文件格式错误（账号和密码需成对出现）')
        exit()

    user_quantity = len(configs) // 2
    for i in range(user_quantity):
        user = configs[i*2]
        pwd = configs[i*2+1]
        sign(i, user, pwd)
